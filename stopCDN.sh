#!/bin/bash
REPLICA_SERVERS=("proj4-repl1.5700.network" "proj4-repl2.5700.network" "proj4-repl3.5700.network" "proj4-repl4.5700.network" "proj4-repl5.5700.network" "proj4-repl6.5700.network" "proj4-repl7.5700.network")
for repl in "${REPLICA_SERVERS[@]}"
do
	echo "Stopping $repl"
	ssh -i ~/.ssh/id_ed25519 dkgp@$repl "pkill -u dkgp httpserver"
done
dns_server="proj4-dns.5700.network"
echo "Stopping $dns_server"
ssh dkgp@$dns_server  "pkill -u dkgp dnsserver"