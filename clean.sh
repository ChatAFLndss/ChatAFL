#!/bin/bash
subjects=(lightftp bftpd proftpd pure-ftpd exim live555 kamailio forked-daapd lighttpd1)
for subject in ${subjects[@]};
do
    # Delete All containers based on the image
    { docker ps -a -q  --filter ancestor=${subject}:latest | xargs docker stop 2> /dev/null | xargs docker rm 2> /dev/null ; } 2>&1 > /dev/null
    # Delete the image
    docker rmi $subject 2> /dev/null
done

echo "Clean complete"
