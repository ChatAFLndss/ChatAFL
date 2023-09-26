#!/bin/bash

cd $WORKDIR

killall pjsua-x86_64-unknown-linux-gnu >/dev/null 2>&1

/bin/sleep 0.1

$WORKDIR/pjproject/pjsip-apps/bin/pjsua-x86_64-unknown-linux-gnu --local-port=5068 \
	        --id sip:33@127.0.0.1 --registrar sip:127.0.0.1 \
		--proxy sip:127.0.0.1 --realm '*' --username 33 --password 33 \
		--auto-answer 200 --auto-play --play-file $WORKDIR/StarWars3.wav --auto-play-hangup \
		--duration=10 --use-cli --no-cli-console --cli-telnet-port=34254 >/dev/null 2>&1 &

