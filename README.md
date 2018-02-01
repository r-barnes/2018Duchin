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
    export CENSUSDIR=/home/rbarnes1/scratch/census2


Step 2: Acquire the Data
-----------------------------

Run the following commands to acquire data

    wget --continue --no-directories --directory-prefix=$CENSUSDIR -i data_files
    wget --continue -r --no-parent -e robots=off 'https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/'

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


Step 6: Aggregate the scores to generate numbers
------------------------------------------------

    mkdir -p results/
    python3 -i ./scripts/aggregate_scores.py $CENSUSDIR/congressional_districts/tl_2010_us_cd111_reproj.shp '$CENSUSDIR/tracts/*.scores' '$CENSUSDIR/block_groups/*.scores' '$CENSUSDIR/blocks/*.scores' aggregate-results.csv

The output is a file called 