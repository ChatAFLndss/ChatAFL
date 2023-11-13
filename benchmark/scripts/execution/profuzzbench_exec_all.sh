#!/bin/bash

export NUM_CONTAINERS="${NUM_CONTAINERS:-10}"
export TIMEOUT="${TIMEOUT:-86400}"
export SKIPCOUNT="${SKIPCOUNT:-1}"
export TEST_TIMEOUT="${TEST_TIMEOUT:-20000}"

export TARGET_LIST=$1
export FUZZER_LIST=$2

if [[ "x$TARGET_LIST" == "x" ]] || [[ "x$FUZZER_LIST" == "x" ]]
then
    echo "Usage: $0 TARGET FUZZER"
    exit 1
fi

echo
echo "# NUM_CONTAINERS: ${NUM_CONTAINERS}"
echo "# TIMEOUT: ${TIMEOUT} s"
echo "# SKIPCOUNT: ${SKIPCOUNT}"
echo "# TEST TIMEOUT: ${TEST_TIMEOUT} ms"
echo "# TARGET LIST: ${TARGET_LIST}"
echo "# FUZZER LIST: ${FUZZER_LIST}"
echo

for FUZZER in $(echo $FUZZER_LIST | sed "s/,/ /g")
do

    for TARGET in $(echo $TARGET_LIST | sed "s/,/ /g")
    do

        echo
        echo "***** RUNNING $FUZZER ON $TARGET *****"
        echo

##### FTP #####

        if [[ $TARGET == "lightftp" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-lightftp

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lightftp $NUM_CONTAINERS results-lightftp aflnet out-lightftp-aflnet "-P FTP -D 10000 -q 3 -s 3 -E -K -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lightftp $NUM_CONTAINERS results-lightftp chatafl out-lightftp-chatafl "-P FTP -D 10000 -q 3 -s 3 -E -K -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lightftp $NUM_CONTAINERS results-lightftp chatafl-cl1 out-lightftp-chatafl_cl1 "-P FTP -D 10000 -q 3 -s 3 -E -K -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lightftp $NUM_CONTAINERS results-lightftp chatafl-cl2 out-lightftp-chatafl_cl2 "-P FTP -D 10000 -q 3 -s 3 -E -K -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi


        if [[ $TARGET == "bftpd" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-bftpd

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh bftpd $NUM_CONTAINERS results-bftpd aflnet out-bftpd-aflnet "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh bftpd $NUM_CONTAINERS results-bftpd chatafl out-bftpd-chatafl "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi
            
            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh bftpd $NUM_CONTAINERS results-bftpd chatafl-cl1 out-bftpd-chatafl_cl1 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh bftpd $NUM_CONTAINERS results-bftpd chatafl-cl2 out-bftpd-chatafl_cl2 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi


        if [[ $TARGET == "proftpd" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-proftpd

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh proftpd $NUM_CONTAINERS results-proftpd aflnet out-proftpd-aflnet "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh proftpd $NUM_CONTAINERS results-proftpd chatafl out-proftpd-chatafl "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh proftpd $NUM_CONTAINERS results-proftpd chatafl-cl1 out-proftpd-chatafl_cl1 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh proftpd $NUM_CONTAINERS results-proftpd chatafl-cl2 out-proftpd-chatafl_cl2 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi

        if [[ $TARGET == "pure-ftpd" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-pure-ftpd

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh pure-ftpd $NUM_CONTAINERS results-pure-ftpd aflnet out-pure-ftpd-aflnet "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh pure-ftpd $NUM_CONTAINERS results-pure-ftpd chatafl out-pure-ftpd-chatafl "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh pure-ftpd $NUM_CONTAINERS results-pure-ftpd chatafl-cl1 out-pure-ftpd-chatafl_cl1 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh pure-ftpd $NUM_CONTAINERS results-pure-ftpd chatafl-cl2 out-pure-ftpd-chatafl_cl2 "-m none -P FTP -D 10000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi


##### SMTP #####

        if [[ $TARGET == "exim" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-exim

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh exim $NUM_CONTAINERS results-exim aflnet out-exim-aflnet "-P SMTP -D 10000 -q 3 -s 3 -E -K -W 100 -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh exim $NUM_CONTAINERS results-exim chatafl out-exim-chatafl "-P SMTP -D 10000 -q 3 -s 3 -E -K -W 100 -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh exim $NUM_CONTAINERS results-exim chatafl-cl1 out-exim-chatafl_cl1 "-P SMTP -D 10000 -q 3 -s 3 -E -K -W 100 -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh exim $NUM_CONTAINERS results-exim chatafl-cl2 out-exim-chatafl_cl2 "-P SMTP -D 10000 -q 3 -s 3 -E -K -W 100 -m none -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi


##### RTSP #####

        if [[ $TARGET == "live555" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-live555

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh live555 $NUM_CONTAINERS results-live555 aflnet out-live555-aflnet "-P RTSP -D 10000 -q 3 -s 3 -E -K -R -m none" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh live555 $NUM_CONTAINERS results-live555 chatafl out-live555-chatafl "-P RTSP -D 10000 -q 3 -s 3 -E -K -R -m none" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh live555 $NUM_CONTAINERS results-live555 chatafl-cl1 out-live555-chatafl_cl1 "-P RTSP -D 10000 -q 3 -s 3 -E -K -R -m none" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh live555 $NUM_CONTAINERS results-live555 chatafl-cl2 out-live555-chatafl_cl2 "-P RTSP -D 10000 -q 3 -s 3 -E -K -R -m none" $TIMEOUT $SKIPCOUNT &
            fi

        fi


##### SIP #####

        if [[ $TARGET == "kamailio" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-kamailio

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh kamailio $NUM_CONTAINERS results-kamailio aflnet out-kamailio-aflnet "-m none -P SIP -l 5061 -D 50000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi
            
            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh kamailio $NUM_CONTAINERS results-kamailio chatafl out-kamailio-chatafl "-m none -P SIP -l 5061 -D 50000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh kamailio $NUM_CONTAINERS results-kamailio chatafl-cl1 out-kamailio-chatafl_cl1 "-m none -P SIP -l 5061 -D 50000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh kamailio $NUM_CONTAINERS results-kamailio chatafl-cl2 out-kamailio-chatafl_cl2 "-m none -P SIP -l 5061 -D 50000 -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi

##### DAAPD #####

        if [[ $TARGET == "forked-daapd" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-forked-daapd

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh forked-daapd $NUM_CONTAINERS results-forked-daapd aflnet out-forked-daapd-aflnet "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh forked-daapd $NUM_CONTAINERS results-forked-daapd chatafl out-forked-daapd-chatafl "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh forked-daapd $NUM_CONTAINERS results-forked-daapd chatafl-cl1 out-forked-daapd-chatafl_cl1 "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh forked-daapd $NUM_CONTAINERS results-forked-daapd chatafl-cl2 out-forked-daapd-chatafl_cl2 "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi

##### HTTP #####

        if [[ $TARGET == "lighttpd1" ]] || [[ $TARGET == "all" ]]
        then

            cd $PFBENCH
            mkdir results-lighttpd1

            if [[ $FUZZER == "aflnet" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lighttpd1 $NUM_CONTAINERS results-lighttpd1 aflnet out-lighttpd1-aflnet "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -R -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lighttpd1 $NUM_CONTAINERS results-lighttpd1 chatafl out-lighttpd1-chatafl "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -R -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl1" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lighttpd1 $NUM_CONTAINERS results-lighttpd1 chatafl-cl1 out-lighttpd1-chatafl_cl1 "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -R -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

            if [[ $FUZZER == "chatafl-cl2" ]] || [[ $FUZZER == "all" ]]
            then
                profuzzbench_exec_common.sh lighttpd1 $NUM_CONTAINERS results-lighttpd1 chatafl-cl2 out-lighttpd1-chatafl_cl2 "-P HTTP -D 200000 -m none -q 3 -s 3 -E -K -R -t ${TEST_TIMEOUT}+" $TIMEOUT $SKIPCOUNT &
            fi

        fi


        if [[ $TARGET == "all" ]]
        then
            # Quit loop -- all fuzzers and targets have already been executed
            exit
        fi

    done
done

