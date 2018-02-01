echo "1. Choose environment '$COMP_ENV'"

#This script assumes that an environment variable COMP_ENV has been set. The
#script chooses directories and compilers based on the value of this variable.

if [ COMP_ENV == "RB_LOCAL" ]; then #RB's local machine
  export CENSUSDIR=/home/rick/data/gis/census
elif [ COMP_ENV == "RB_COMET" ]; then
  #Comet supercomputer
  export CENSUSDIR=/home/rbarnes1/scratch/census2
else
  echo "Unrecognised environment! You should edit RUN.sh to match your machine!"
  exit 1
fi



echo "2. Acquiring data"

wget --continue --no-directories --directory-prefix=$CENSUSDIR -i data_files

exit 0

echo "2. Converting shapefiles from WGS84 into a conterminous AEA projection..."

ls $CENSUSDIR/tracts/*       | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'
ls $CENSUSDIR/block_groups/* | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'
ls $CENSUSDIR/blocks/*       | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'



echo "3. Compiling the code"

if [ COMP_ENV == "RB_COMET" ]; then
  module load gcc/6.2.0 #Only needed on XSEDE
fi

cd scripts
make -j 4
cd ..



#May be necessary to get executables to run
#export LD_PRELOAD=/share/apps/compute/gcc-6.2.0/lib64/libstdc++.so.6



echo "4. Calculating scores"

#2010 subunits, 2010 congressional districts
ls $CENSUSDIR/tracts/*_reproj.shp       | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp   -noprintparent
ls $CENSUSDIR/block_groups/*_reproj.shp | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -noshp -noprintparent
ls $CENSUSDIR/blocks/*_reproj.shp*      | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -noshp -noprintparent

echo "4b. Generating spotcheck shapefiles"

ls $CENSUSDIR/block_groups/*_reproj.shp | sed 's/\.shp//' | shuf | head -n 3 | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp -printparent
ls $CENSUSDIR/blocks/*_reproj.shp*      | sed 's/\.shp//' | shuf | head -n 3 | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp -printparent

#2013 subunits, 2010 congressional districts
#ls $CENSUSDIR/tracts/*_reproj.shp | xargs -n 1 -I {} $COMPACTNESSEXE -sub {} -sup $CENSUSDIR/cong_dist_2013/tl_2013_us_cd113_reproj.shp -outsub {}.2013scores
#ls $CENSUSDIR/block_groups/*_reproj.shp | xargs -n 1 -I {} $COMPACTNESSEXE -sub {} -sup $CENSUSDIR/cong_dist_2013/tl_2013_us_cd113_reproj.shp -outsub {}.2013scores
#ls $CENSUSDIR/blocks/*_reproj.shp | sed 's/.2013scores//' | uniq -u | xargs -n 1 -I {} $COMPACTNESSEXE -sub {} -sup $CENSUSDIR/cong_dist_2013/tl_2013_us_cd113_reproj.shp -outsub {}.2013scores



echo "8. Aggregating scores"
mkdir -p results/
#2010 subunits, 2010 congressional districts
python3 -i ./scripts/aggregate_scores.py $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp '$CENSUSDIR/tracts/*.scores' '$CENSUSDIR/block_groups/*.scores' '$CENSUSDIR/blocks/*.scores'

#2013 subunits, 2010 congressional districts
#python3 -i ./aggregate_scores.py $CENSUSDIR/cong_dist_2013/tl_2013_us_cd113_reproj.shp '$CENSUSDIR/tracts/*.2013scores' '$CENSUSDIR/block_groups/*.2013scores' '$CENSUSDIR/blocks/*.2013scores'




wget --continue -r --no-parent -e robots=off 'https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/'






