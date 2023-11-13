#!/bin/bash

# Generate the state and coverage graphs

FILTER=$1
TIME=${2:-1440}

reset="\e[0m"
green="\e[0;92m"
yellow="\e[0;33m"
function warn  { echo -e "${yellow}[!] $1$reset"; }
function info  { echo -e "${green}[+]$reset $1"; }

if [ -z "$FILTER" ]; then
    echo "Usage: analyze.sh <subject names> <time in minutes>"
    exit 1
fi

PFBENCH="$PWD/benchmark"
cd $PFBENCH

for SUBJECT in $(echo $FILTER | tr "," "\n");
do
    echo "Analyzing $SUBJECT"
    # Check if results exists
    if [ -z "$(ls -A results-$SUBJECT)" ]; then
        warn "No results for subject $SUBJECT."
        warn "Please check whether the fuzzing has completed via the following command:"
        warn "  docker ps -a | grep $SUBJECT"
        docker ps -a | grep $SUBJECT
        warn ""
        warn "If the containers' status is 'Up ..', please wait for the fuzzing to complete."
        warn "Once the fuzzing complete, the containers' status will change to 'Exited ..'"
        continue
    fi
    PATH=$PATH:$PFBENCH/scripts/execution:$PFBENCH/scripts/analysis scripts/analysis/profuzzbench_generate_all.sh $SUBJECT $TIME
    
    RES_FOLDER=$(date "+res_${SUBJECT}_%b-%d_%H-%M-%S")
    
    info "Results from analysis for ${SUBJECT} are stored in $RES_FOLDER"
    mkdir ../$RES_FOLDER
    cp -r *_${SUBJECT}.png ../$RES_FOLDER
    cp -r results-${SUBJECT} ../$RES_FOLDER
done
