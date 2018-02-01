2018Duchin
==========

**Title of Manuscript**:
TODO

**Authors**: TODO

**Corresponding Author**: TODO

**Code/Analysis By**: Richard Barnes (richard.barnes@berkeley.edu)

**DOI Number of Manuscript**
TODO

**Code Repositories**
 * [Author's GitHub Repository](https://github.com/r-barnes/2018Duchin)

This repository contains the analysis code used to produce some numbers,
statistics, and figures for the manuscript above.



Abstract
========

TODO



Compilation
===========

This step may be skipped if you have downloaded this code from Zenodo.

After cloning this repo you must acquire compactnesslib by running:

    git submodule init
    git submodule update

Compactnesslib relies on no external libraries beyond the C++11 standard
library.



Generating Numbers
==================

To generate the numbers used in the paper follow the following steps:


Step 1: Setup the Environment
-----------------------------

Export the `CENSUSDIR` variable set to an appropriate value. Mine is one of:

    export CENSUSDIR=/home/rick/data/gis/census
    export CENSUSDIR=/home/rbarnes1/scratch/census


Step 2: Acquire the Data
-----------------------------

Run the following commands to acquire data

    wget --continue --no-directories --directory-prefix=$CENSUSDIR -i data_files
    wget --continue -r --no-parent -e robots=off --no-directories 'https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/'

Because the census website is silly, you may have to fiddle with things to work
around their anti-webbot security.

After acquiring the data, you must reorganize it into `congressional_districts`,
`tracts/`, `block_groups/`, and `blocks/` subdirectories within `CENSUSDIR` as
appropriate. A quick examination of the following commands will give you the
idea.

You must also unpack the data.

Step 3: Reprojecting the Data
-----------------------------

The data must be in a planar projection for the calculations to yield correct
results. We use an Albers Equal Area projection suitable for use on the
conterminous United States. If area and perimeter are not being considered, just
geographic proximity, then this projection can also be used for Alaska, Hawaii,
and outlying areas.

The following lines reproject the data:

    ls $CENSUSDIR/tracts/*       | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'
    ls $CENSUSDIR/block_groups/* | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'
    ls $CENSUSDIR/blocks/*       | sed 's/.shp//' | xargs -n 1 -I {} ogr2ogr -f "ESRI Shapefile" {}_reproj.shp {}.shp -t_srs '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,-0,-0,-0,0 +units=m +no_defs'


Step 4: Compile the Code
-----------------------------

Since C++11 is used, on XSEDE's comet, you'll want:

    module load gcc/6.2.0 #Only needed on XSEDE

Regardless, run:

    cd scripts
    make -j 4 #Set 4 to the number of cores you have available. Compilation is fast regardless
    cd ..

On Comet you'll also need the C++ standard run-time library loaded:

    export LD_PRELOAD=/share/apps/compute/gcc-6.2.0/lib64/libstdc++.so.6


Step 5: Calculating Scores
-----------------------------

Scores are generated with:

    ls $CENSUSDIR/tracts/*_reproj.shp       | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp   -noprintparent
    ls $CENSUSDIR/block_groups/*_reproj.shp | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -noshp -noprintparent
    ls $CENSUSDIR/blocks/*_reproj.shp*      | sed 's/\.shp//' | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -noshp -noprintparent

Spotchecks for visualization can be generated with:

    ls $CENSUSDIR/block_groups/*_reproj.shp | sed 's/\.shp//' | shuf | head -n 3 | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp -printparent
    ls $CENSUSDIR/blocks/*_reproj.shp*      | sed 's/\.shp//' | shuf | head -n 3 | xargs -t -n 1 -I {} ./scripts/net_compact.exe -sub {}.shp -sup $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp -outpre {}_out -shp -printparent


Step 6: Unpack the Population Data
----------------------------------

The population data files were acquired above using:

    wget --continue -r --no-parent -e robots=off --no-directories 'https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/'

These files are assumed to be unpacked and living in a `$CENSUSDIR/popdata` directory.

Now, we aggregate the block ids and population values using:

    echo "BLOCKID10 POP10" > $CENSUSDIR/popdata/popdata.csv
    for f in $CENSUSDIR/popdata/*dbf; do echo "$f"; dbfdump $f | awk '{print $5" "$8}' | tail -n +2 >> $CENSUSDIR/popdata/popdata.csv; done




Step 6: Aggregate the scores to generate numbers
------------------------------------------------

    mkdir -p results/
    python3 -i ./scripts/aggregate_scores.py $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp '$CENSUSDIR/tracts/*.scores' '$CENSUSDIR/block_groups/*.scores' '$CENSUSDIR/blocks/*.scores' $CENSUSDIR/popdata/popdata.csv aggregate-results.csv

In this case, the output is a file called `aggregate-results.csv`.









Notes
=====

The table below (drawn from
[here](https://www.census.gov/geo/reference/geoidentifiers.html)) shows the
GEOID structure in TIGER/Line Shapefiles for some of the most common legal and
statistical geographies, as well as example GEOIDs for different geographic
areas.

    Area Type                                   GEOID Structure                  Number of Digits  Example Geographic Area                                                                                                        Example GEOID
    State                                       STATE                            2                 Texas                                                                                                                          48
    County                                      STATE+COUNTY                     2+3=5             Harris County, TX                                                                                                              48201
    County Subdivision                          STATE+COUNTY+COUSUB              2+3+5=10          Pasadena CCD, Harris County, TX                                                                                                4820192975
    Places                                      STATE+PLACE                      2+5=7             Houston, TX                                                                                                                    4835000
    Census Tract                                STATE+COUNTY+TRACT               2+3+6=11          Census Tract 2231 in Harris County, TX                                                                                         48201223100
    Block Group                                 STATE+COUNTY+TRACT+BLOCK GROUP   2+3+6+1=12        Block Group 1 in Census Tract 2231 in Harris County, TX                                                                        482012231001
    Block*                                      STATE+COUNTY+TRACT+BLOCK         2+3+6+4=15        (Note – some blocks also contain a one character suffix (A, B, C, ect.)  Block 1050 in Census Tract 2231 in Harris County, TX  482012231001050
    Congressional District (113th Congress)     STATE+CD                         2+2=4             Connecticut District 2                                                                                                         0902
    State Legislative District (Upper Chamber)  STATE+SLDU                       2+3=5             Connecticut State Senate District 33                                                                                           09033
    State Legislative District (Lower Chamber)  STATE+SLDL                       2+3=5             Connecticut State House District 147                                                                                           09147
    ZCTA **                                     ZCTA                             5                 Suitland, MD ZCTA                                                                                                              20746
    * The block group code is not included in the census block GEOID code because the first digit of a census block code represents the block group code.
    ** ZIP Code Tabulation Areas (ZCTAs) are generalized areal representations of United States Postal Service (USPS) ZIP Code service areas.
