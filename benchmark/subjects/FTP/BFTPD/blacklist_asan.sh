#!/bin/bash

PROGRAM=$WORKDIR/bftpd-stateafl/bftpd

BSS=`nm $PROGRAM |grep -E " b | B "|sort|perl -n -a -e 'BEGIN { $addr=0; $end=0; $bss=0; } chomp($F[2]); if($F[2] eq "__bss_start") { $bss=1; } if($F[2] =~ /^_Z/ && $F[2] =~ /asan|sanitizer/) { if ($bss == 1) { if(++$NR == 1) { $addr=$F[0]; } else { $end=$F[0]; } } } END { printf("0x%s-%x\n", $addr, hex($end)-hex($addr)) if($addr != 0); }'`
DATA=`nm $PROGRAM |grep -E " d | D "|sort|perl -n -a -e 'BEGIN { $addr=0; $end=0; $data=0; } chomp($F[2]); if($F[2] eq "__data_start") { $data=1; } if($F[2] =~ /^_Z/ && $F[2] =~ /sanitizer/) { if ($data == 1) { if(++$NR == 1) { $addr=$F[0]; } else { $end=$F[0]; } } } END { printf("0x%s-%x\n", $addr, hex($end)-hex($addr)) if($addr != 0); }'`

AFL_INIT_AREA=`nm $PROGRAM |sort|grep -A 1 "__afl_area_initial"|perl -n -a -e '$NR++; if($NR==1) { $addr = $F[0]; } if ($NR==2) { printf("%s-%x\n", $addr, hex($F[0])-hex($addr)); }'`

TRACER_DATA=`readelf -S $PROGRAM |grep -A 1 tracer_data | awk '(NR==1) {printf "0x%s-",$4} (NR==2) {print $1}'`
TRACER_BSS=`readelf -S $PROGRAM |grep -A 1 tracer_bss  | awk '(NR==1) {printf "0x%s-",$4} (NR==2) {print $1}'`

export BLACKLIST_GLOBALS=$BSS:$DATA:${TRACER_DATA}:${TRACER_BSS}:${AFL_INIT_AREA}
