#!/bin/bash

export TARGET_DIR="openssh-stateafl"

# Blacklisting buffers for input/output packets

export BLACKLIST_ALLOC_SITES=

BLACKLIST_LINES="packet.c:237,packet.c:238,packet.c:239,packet.c:240"
OUTPUT=$($WORKDIR/blacklist_alloc.sh $WORKDIR/${TARGET_DIR}/sshd ${BLACKLIST_LINES})

if [ $? -eq 0 ]; then
  BLACKLIST_ALLOC_SITES=$OUTPUT
  echo "Black-listing alloc sites: ${BLACKLIST_ALLOC_SITES}"
fi

export INPUTS=${WORKDIR}/in-ssh-replay
