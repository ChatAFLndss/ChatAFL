#!/bin/bash

PROGRAM=$WORKDIR/pure-ftpd-stateafl/src/pure-ftpd

BSS=`nm $PROGRAM |grep -E " b | B "|sort|perl -n -a -e 'BEGIN { $addr=0; $end=0; $bss=0; } chomp($F[2]); if($F[2] eq "__bss_start") { $bss=1; } if($F[2] =~ /^_Z/ && $F[2] =~ /asan|sanitizer/) { if ($bss == 1) { if(++$NR == 1) { $addr=$F[0]; } else { $end=$F[0]; } } } END { printf("0x%s-%x\n", $addr, hex($end)-hex($addr)) if($addr != 0); }'`
DATA=`nm $PROGRAM |grep -E " d | D "|sort|perl -n -a -e 'BEGIN { $addr=0; $end=0; $data=0; } chomp($F[2]); if($F[2] eq "__data_start") { $data=1; } if($F[2] =~ /^_Z/ && $F[2] =~ /sanitizer/) { if ($data == 1) { if(++$NR == 1) { $addr=$F[0]; } else { $end=$F[0]; } } } END { printf("0x%s-%x\n", $addr, hex($end)-hex($addr)) if($addr != 0); }'`

AFL_INIT_AREA=`nm $PROGRAM |sort|grep -A 1 "__afl_area_initial"|perl -n -a -e '$NR++; if($NR==1) { $addr = $F[0]; } if ($NR==2) { printf("%s-%x\n", $addr, hex($F[0])-hex($addr)); }'`

SYMBOLS="replybuf|wrstr.outbuf|wrstr.outcnt|fd"
GLOBALS=`gdb $PROGRAM -ex 'info variables' --batch | grep -v "File "| grep '*' |perl -n -e 'BEGIN{$globals=()} if(/\*([a-zA-Z0-9_]+)/) {push @globals,$1} END{print join("|",@globals); }'`
EXTERNALS=`gdb $PROGRAM -ex 'info variables' --batch | perl -n -e 'BEGIN{$externals=()} if($on){ if(/([a-zA-Z0-9_]+)(?:\[|;)/) { push @externals,$1; } } if(m|^File\s[^.]|) { $on = 1; } if(/^$/) { $on = 0; } END{print join("|",@externals); }'`
MISC_ADDR=`nm $PROGRAM |sort|perl -n -a -e '$NR++; if (defined $line && $NR==$line+1) { printf(":0x%s-%x", $addr, hex($F[0])-hex($addr)); }  if(/\s(b|B|d|D)\s/ && /'$SYMBOLS'|'$GLOBALS'|'$EXTERNALS'/) { $addr = $F[0]; $line=$NR; } else { $addr = undef; $line = $undef; }'`

TRACER_DATA=`readelf -S $PROGRAM |grep -A 1 tracer_data | awk '(NR==1) {printf "0x%s-",$4} (NR==2) {print $1}'`
TRACER_BSS=`readelf -S $PROGRAM |grep -A 1 tracer_bss  | awk '(NR==1) {printf "0x%s-",$4} (NR==2) {print $1}'`

export BLACKLIST_GLOBALS=$BSS:$DATA:${TRACER_DATA}:${TRACER_BSS}:${AFL_INIT_AREA}:${MISC_ADDR}
