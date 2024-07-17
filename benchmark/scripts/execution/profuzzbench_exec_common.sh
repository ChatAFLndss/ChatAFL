#!/bin/bash

DOCIMAGE=$1   #name of the docker image
RUNS=$2       #number of runs
SAVETO=$3     #path to folder keeping the results

FUZZER=$4     #fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container
OUTDIR=$5     #name of the output folder created inside the docker container
OPTIONS=$6    #all configured options for fuzzing
TIMEOUT=$7    #time for fuzzing
SKIPCOUNT=$8  #used for calculating coverage over time. e.g., SKIPCOUNT=5 means we run gcovr after every 5 test cases
DELETE=$9

WORKDIR="/home/ubuntu/experiments"

#keep all container ids
cids=()

#create one container for each run
for i in $(seq 1 $RUNS); do
  id=$(docker run --cpus=1 -d -it $DOCIMAGE /bin/bash -c "cd ${WORKDIR} && run ${FUZZER} ${OUTDIR} '${OPTIONS}' ${TIMEOUT} ${SKIPCOUNT}")
  cids+=(${id::12}) #store only the first 12 characters of a container ID
done

dlist="" #docker list
for id in ${cids[@]}; do
  dlist+=" ${id}"
done

#wait until all these dockers are stopped
printf "\n${FUZZER^^}: Fuzzing in progress ..."
printf "\n${FUZZER^^}: Waiting for the following containers to stop: ${dlist}"
docker wait ${dlist} > /dev/null
wait

#collect the fuzzing results from the containers
printf "\n${FUZZER^^}: Collecting results and save them to ${SAVETO}"
index=1
for id in ${cids[@]}; do
  printf "\n${FUZZER^^}: Collecting results from container ${id}"
  docker cp ${id}:/home/ubuntu/experiments/${OUTDIR}.tar.gz ${SAVETO}/${OUTDIR}_${index}.tar.gz > /dev/null
  if [ ! -z $DELETE ]; then
    printf "\nDeleting ${id}"
    docker rm ${id} # Remove container now that we don't need it
  fi
  index=$((index+1))
done

printf "\n${FUZZER^^}: I am done!\n"
