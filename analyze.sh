#!/bin/bash

# Generate the state and coverage graphs

PFBENCH="$PWD/benchmark"
cd $PFBENCH

PATH=$PATH:$PFBENCH/scripts/execution:$PFBENCH/scripts/analysis scripts/analysis/profuzzbench_generate_all.sh $1 $2

RES_FOLDER=$(date "+res_%b-%d_%H-%M-%S")
echo "Results from analysis are stored in $RES_FOLDER"
mkdir ../$RES_FOLDER
mv *.png ../$RES_FOLDER
mv results-* ../$RES_FOLDER