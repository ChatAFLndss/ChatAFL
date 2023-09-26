#!/bin/bash

prog="testOnDemandR"

#try to gracefully terminate the server first
pid1=$(ps aux | grep ${prog} | grep -v "color" | awk '{print $2}')
kill -SIGUSR1 $pid1 > /dev/null 2>&1
sleep 1
#if it is still alive because of some unknown reason, force to stop it
pid2=$(ps aux | grep ${prog} | grep -v "color" | awk '{print $2}')
if [ "$pid1" == "$pid2" ]; then
  kill -SIGTERM $pid2 > /dev/null 2>&1
fi
