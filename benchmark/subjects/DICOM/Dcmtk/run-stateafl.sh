#!/bin/bash

export TARGET_DIR="dcmtk-stateafl"

# Buffers for sending/receiving PDUs
export BLACKLIST_ALLOC_SITES=$(blacklist_alloc.sh $WORKDIR/dcmtk-stateafl/build/bin/dcmqrscp "dul.cc:2300")

export INPUTS=${WORKDIR}/in-dicom-replay
