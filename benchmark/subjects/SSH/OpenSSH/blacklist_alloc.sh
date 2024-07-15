#!/bin/bash

if [ "$#" -ne 2 ]
then
  echo "Usage: $0 <program> <comma-separated list of line numbers>"
  exit 1
fi

PROGRAM=$1
BLACKLIST_LINES=$2


if [ ! -f $PROGRAM ]
then
  echo "Program '$PROGRAM' not found"
  exit 1
fi

BLACKLIST_ALLOC_SITES=""

BLACKLIST_LINES_ARRAY=$(echo $BLACKLIST_LINES | tr ',' '\n')

for LINE in ${BLACKLIST_LINES_ARRAY}
do

  #echo "Parsing: $LINE"

  RANGE_CMD=$(gdb $PROGRAM -ex "info line $LINE" --batch | perl -n -e '$start=""; $end="";if(/starts\sat\saddress\s(0x[a-f0-9]+)\b/) { $start = $1; } if(/ends\sat\s(0x[a-f0-9]+)\b/) { $end = $1; } if($start ne "" && $end ne "") { print "--start-address=$start --stop-address=$end\n"; }')

  if [ "x${RANGE_CMD}" == "x" ]
  then
    echo "Failed to parse: $LINE"
    exit 1;
  fi

  ADDR=$(objdump -d $PROGRAM ${RANGE_CMD} | tac | grep -B 1 "callq" | cut -d':' -f 1 | tr -d ' ' | head -1)

  #echo "ADDR: $ADDR"

  if [ "x${ADDR}" == "x" ]
  then
    echo "Failed to parse: $LINE"
    exit 1;
  fi

  BLACKLIST_ALLOC_SITES="${BLACKLIST_ALLOC_SITES}:0x$ADDR"

done

#Remove first colon
BLACKLIST_ALLOC_SITES=${BLACKLIST_ALLOC_SITES:1}

echo $BLACKLIST_ALLOC_SITES

exit 0

