#!/bin/bash

if [ -z $KEY ]; then
    echo "NO OPENAI API KEY PROVIDED! Please set the KEY environment variable"
    exit 0
fi

# Update the openAI key
for x in ChatAFL ChatAFL-CL1 ChatAFL-CL2 ChatAFL-SEED ChatAFL-BIN SNetGen;
do
  sed -i "s/#define OPENAI_TOKEN \".*\"/#define OPENAI_TOKEN \"$KEY\"/" $x/chat-llm.h
done

for y in DICOM/Dcmtk DNS/Dnsmasq DTLS/TinyDTLS SSH/OpenSSH;
do
  sed -i "s/ENV OPENAI_API_KEY=\".*\"/ENV OPENAI_API_KEY=\"$KEY\"/" benchmark/subjects/$y/Dockerfile
done

for y in DAAP/forked-daapd FTP/BFTPD FTP/LightFTP FTP/ProFTPD FTP/PureFTPD HTTP/Lighttpd1 RTSP/Live555 SIP/Kamailio SMTP/Exim;
do
  sed -i "s/ENV OPENAI_API_KEY=\".*\"/ENV OPENAI_API_KEY=\"$KEY\"/" benchmark/subjects/$y/Dockerfile
done

# Copy the different versions of ChatAFL to the benchmark directories
for subject in ./benchmark/subjects/*/*; do
  rm -r $subject/aflnet 2>&1 >/dev/null
  cp -r aflnet $subject/aflnet

  rm -r $subject/chatafl 2>&1 >/dev/null
  cp -r ChatAFL $subject/chatafl
  
  rm -r $subject/chatafl-cl1 2>&1 >/dev/null
  cp -r ChatAFL-CL1 $subject/chatafl-cl1
  
  rm -r $subject/chatafl-cl2 2>&1 >/dev/null
  cp -r ChatAFL-CL2 $subject/chatafl-cl2

  rm -r $subject/chatafl-seed 2>&1 >/dev/null
  cp -r ChatAFL-SEED $subject/chatafl-seed
  
  rm -r $subject/chatafl-bin 2>&1 >/dev/null
  cp -r ChatAFL-BIN $subject/chatafl-bin

  rm -r $subject/snetgen 2>&1 >/dev/null
  cp -r SNetGen $subject/snetgen
done;

# Build the docker images

PFBENCH="$PWD/benchmark"
cd $PFBENCH
PFBENCH=$PFBENCH scripts/execution/profuzzbench_build_all.sh
