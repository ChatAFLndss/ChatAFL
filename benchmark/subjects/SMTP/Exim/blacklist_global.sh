#!/bin/bash

if [ "$#" -ne 2 ]
then
  echo "Usage: $0 <program> <comma-separated list of global symbols>"
  exit 1
fi

PROGRAM=$1
BLACKLIST_SYMBOLS=$2


if [ ! -f $PROGRAM ]
then
  echo "Program '$PROGRAM' not found"
  exit 1
fi

BLACKLIST_GLOBALS=""

BLACKLIST_SYMBOLS_ARRAY=$(echo $BLACKLIST_SYMBOLS | tr ',' '\n')

for SYMBOL in ${BLACKLIST_SYMBOLS_ARRAY}
do

  #echo "Parsing: $LINE"

  ADDR=$(objdump -t $PROGRAM | awk '($6=="'"$SYMBOL"'") { print $1"-"$5 }')

  if [ "x${ADDR}" == "x" ]
  then
    echo "Failed to parse: $SYMBOL"
    exit 1;
  fi

  #echo "ADDR: $ADDR"

  BLACKLIST_GLOBALS="${BLACKLIST_GLOBALS}:0x$ADDR"

done

#Remove first colon
BLACKLIST_GLOBALS=${BLACKLIST_GLOBALS:1}

echo $BLACKLIST_GLOBALS

exit 0

