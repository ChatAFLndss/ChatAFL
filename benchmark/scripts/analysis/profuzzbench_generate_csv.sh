#!/bin/bash
prog=$1        #name of the subject program (e.g., lightftp)
runs=$2        #total number of runs
fuzzers=$3     #fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container
covfile=$4     #output CSV file
append=$5      #append mode
               #enable this mode when the results of different fuzzers need to be merged
states_data=$6

#create a new file if append = 0
if [ $append = "0" ]; then
  #echo "Trying to delete $PWD/$covfile"
  rm "$PWD/$covfile" ; touch $covfile
  echo "time,subject,fuzzer,run,cov_type,cov" >> $covfile

  #echo "Trying to delete $PWD/$states_data"
  rm $states_data ; touch $states_data
  echo "time,subject,fuzzer,run,state_type,state" >> $states_data
fi

#remove space(s) 
#it requires that there is no space in the middle
strim() {
  trimmedStr=$1
  echo "${trimmedStr##*( )}"
}

#original format: time,l_per,l_abs,b_per,b_abs
#converted format: time,subject,fuzzer,run,cov_type,cov
convert() {
  fuzzer=$1
  subject=$2
  run_index=$3
  ifile=$4
  ofile=$5

  {
    read #ignore the header
    while read -r line; do
      time=$(strim $(echo $line | cut -d',' -f1))
      l_per=$(strim $(echo $line | cut -d',' -f2))
      l_abs=$(strim $(echo $line | cut -d',' -f3))
      b_per=$(strim $(echo $line | cut -d',' -f4))
      b_abs=$(strim $(echo $line | cut -d',' -f5))
      echo $time,$subject,$fuzzer,$run_index,"l_per",$l_per >> $ofile
      echo $time,$subject,$fuzzer,$run_index,"l_abs",$l_abs >> $ofile
      echo $time,$subject,$fuzzer,$run_index,"b_per",$b_per >> $ofile
      echo $time,$subject,$fuzzer,$run_index,"b_abs",$b_abs >> $ofile
    done 
  } < $ifile
}

#original format: unix_time, cycles_done, cur_path, paths_total, pending_total, pending_favs, map_size, unique_crashes, unique_hangs, max_depth, execs_per_sec, n_nodes, n_edges, chat_times
#converted format: time,subject,fuzzer,run,data_type,data
convert_state() {
  fuzzer=$1
  subject=$2
  run_index=$3
  ifile=$4
  ofile=$5

  {
    read #ignore the header
    while read -r line; do
      time=$(strim $(echo $line | cut -d',' -f1))
      nodes=$(strim $(echo $line | cut -d',' -f12))
      edges=$(strim $(echo $line | cut -d',' -f13))
      echo $time,$subject,$fuzzer,$run_index,"nodes",$nodes >> $ofile
      echo $time,$subject,$fuzzer,$run_index,"edges",$edges >> $ofile
    done 
  } < $ifile
}


#extract tar files & process the data
for fuzzer in $fuzzers; do 
  for i in $(seq 1 $runs); do 
    printf "\nProcessing out-${prog}-${fuzzer}-${i} ..."
    rm -rf out-${prog}-${fuzzer}-${i}
    #tar -zxvf out-${prog}-${fuzzer}_${i}.tar.gz > /dev/null 2>&1
    tar -axf out-${prog}-${fuzzer}_${i}.tar.gz out-${prog}-${fuzzer}/cov_over_time.csv
    tar -axf out-${prog}-${fuzzer}_${i}.tar.gz out-${prog}-${fuzzer}/plot_data
    mv out-${prog}-${fuzzer} out-${prog}-${fuzzer}-${i}
    #combine all csv files
    convert $fuzzer $prog $i out-${prog}-${fuzzer}-${i}/cov_over_time.csv $covfile
    convert_state $fuzzer $prog $i out-${prog}-${fuzzer}-${i}/plot_data $states_data
  done 
done
