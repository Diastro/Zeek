#!/bin/bash
# launch-clients.sh

COUNT=-1

function help {
    echo "usage: -h help"
    echo "       -n number of instances of client to launch locally"
}

while getopts n:h opt
 do
      case $opt in
          n) COUNT="${OPTARG}";;
          h) HELP="-1";;
          *) exit 1;;
        esac
done

if [ "$HELP" == "-1" ] || [ "$COUNT" == "-1" ]
then
    help
    exit 1
fi

for i in $(seq 1 $COUNT)
do
	python client.py > /dev/null &
	echo "Client $i started with PID : $!"
done
