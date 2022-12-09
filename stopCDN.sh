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
for repl in "${REPLICA_SERVERS[@]}"
do
	echo "Stoppping $repl"
	ssh -i ~/.ssh/id_ed25519 $SERVERUSER@$repl "pkill -u $SERVERUSER httpserver"
done
dns_server="proj4-dns.5700.network"
echo "Stopping $dns_server"
ssh $SERVERUSER@$dns_server  "pkill -u $SERVERUSER dnsserver"