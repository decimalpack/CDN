#!/bin/bash
LONG=port:,origin:,name:,username:,keyfile:
SHORT=p:,o:,n:,u:,i:
OPTS=$(getopt --alternative --options $SHORT --longoptions $LONG -- "$@") 

eval set -- "$OPTS"

while :
do
  case "$1" in
	-p | --port)       PORT="$2"       ; shift 2  ;;
    -o | --origin)     ORIGIN="$2"     ; shift 2  ;;
	-n | --name)       NAME="$2"       ; shift 2  ;;
	-u | --username)   SERVERUSER="$2"    ; shift 2  ;;
	-i | --keyfile)    KEYFILE="$2"    ; shift 2  ;;
	--) shift; break ;;
	*) echo "Unexpected option: $1 - this should not happen."
       usage ;;
  esac
done


REPLICA_SERVERS=("proj4-repl1.5700.network" "proj4-repl2.5700.network" "proj4-repl3.5700.network" "proj4-repl4.5700.network" "proj4-repl5.5700.network" "proj4-repl6.5700.network" "proj4-repl7.5700.network")
preload=`cat ./preload_files.txt|tr '\n' ';'`
for repl in "${REPLICA_SERVERS[@]}"
do
	ssh -i $KEYFILE $SERVERUSER@$repl "screen -d -m ./httpserver -p $PORT -o http://cs5700cdnorigin.ccs.neu.edu:8080/" 
	echo "Preloading $repl"
	sleep 0.5s # wait for server to start
	curl --data $preload $repl:25015/preload
done
echo "Allow 10 minutes for cache to warm up."

dns_server="proj4-dns.5700.network"
echo "Running $dns_server"
ssh $SERVERUSER@$dns_server  "screen -d -m ./dnsserver -p $PORT -n dc"