#!/bin/bash

# Generate the state and coverage graphs

FILTER=$1
TIME=${2:-1440}

if [ -z "$FILTER" ]; then
    echo "Usage: analyze.sh <subject names> [time in minutes]"
    exit 1
fi

PFBENCH="$PWD/benchmark"
cd $PFBENCH

for SUBJECT in $(echo $FILTER | tr "," "\n");
do
    echo "Analyzing $SUBJECT"
    # Check if subject exists
    if [ ! -d "results-$SUBJECT" ]; then
        echo "Results folder for subject $SUBJECT, ignoring. Check the name and whether the campaign has finished"
        continue
    fi
    PATH=$PATH:$PFBENCH/scripts/execution:$PFBENCH/scripts/analysis scripts/analysis/profuzzbench_generate_all.sh $SUBJECT $TIME
    
    RES_FOLDER=$(date "+res_${SUBJECT}_%b-%d_%H-%M-%S")
    
    echo "Results from analysis for ${SUBJECT} are stored in $RES_FOLDER"
    mkdir ../$RES_FOLDER
    cp -r *_${SUBJECT}.png ../$RES_FOLDER
    cp -r results-${SUBJECT} ../$RES_FOLDER
done
