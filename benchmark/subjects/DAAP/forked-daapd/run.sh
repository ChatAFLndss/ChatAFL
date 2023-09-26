#!/bin/bash

FUZZER=$1     #fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container
OUTDIR=$2     #name of the output folder
OPTIONS=$3    #all configured options -- to make it flexible, we only fix some options (e.g., -i, -o, -N) in this script
TIMEOUT=$4    #time for fuzzing
SKIPCOUNT=$5  #used for calculating cov over time. e.g., SKIPCOUNT=5 means we run gcovr after every 5 test cases

strstr() {
  [ "${1#*$2*}" = "$1" ] && return 1
  return 0
}

#Network deamons needed by forked-daapd
sudo /etc/init.d/dbus start
sudo /etc/init.d/avahi-daemon start

sudo /etc/init.d/dbus status
if [ $? -ne 0 ]
then
  echo "Unable to run DBUS"
  exit 1
fi

sudo /etc/init.d/avahi-daemon status
if [ $? -ne 0 ]
then
  echo "Unable to run AVAHI daemon"
  exit 1
fi

#Commands for afl-based fuzzers (e.g., aflnet, aflnwe)
if $(strstr $FUZZER "afl") || $(strstr $FUZZER "llm"); then

  # Run fuzzer-specific commands (if any)
  if [ -e ${WORKDIR}/run-${FUZZER} ]; then
    source ${WORKDIR}/run-${FUZZER}
  fi

  TARGET_DIR=${TARGET_DIR:-"forked-daapd"}
  INPUTS=${INPUTS:-${WORKDIR}"/in-daap"}

  #Step-1. Do Fuzzing
  #Move to fuzzing folder
  cd $WORKDIR

  timeout -k 2s --preserve-status $TIMEOUT /home/ubuntu/${FUZZER}/afl-fuzz -d -i ${INPUTS} -o $OUTDIR -N tcp://127.0.0.1/3689 $OPTIONS ${WORKDIR}/${TARGET_DIR}/src/forked-daapd -d 0 -c ${WORKDIR}/forked-daapd.conf -f

  STATUS=$?

  #Step-2. Collect code coverage over time
  #Move to gcov folder
  cd $WORKDIR

  #The last argument passed to cov_script should be 0 if the fuzzer is afl/nwe and it should be 1 if the fuzzer is based on aflnet
  #0: the test case is a concatenated message sequence -- there is no message boundary
  #1: the test case is a structured file keeping several request messages
  if [ $FUZZER = "aflnwe" ]; then
    cov_script ${WORKDIR}/${OUTDIR}/ 3689 ${SKIPCOUNT} ${WORKDIR}/${OUTDIR}/cov_over_time.csv 0
  else
    cov_script ${WORKDIR}/${OUTDIR}/ 3689 ${SKIPCOUNT} ${WORKDIR}/${OUTDIR}/cov_over_time.csv 1
  fi

  cd $WORKDIR/forked-daapd-gcov
  gcovr -r . --html --html-details -o index.html
  mkdir ${WORKDIR}/${OUTDIR}/cov_html/
  cp *.html ${WORKDIR}/${OUTDIR}/cov_html/

  #Step-3. Save the result to the ${WORKDIR} folder
  #Tar all results to a file
  cd ${WORKDIR}
  tar -zcvf ${WORKDIR}/${OUTDIR}.tar.gz ${OUTDIR}

  exit $STATUS
fi
