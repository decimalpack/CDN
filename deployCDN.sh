#!/bin/bash
REPLICA_SERVERS=("proj4-repl1.5700.network" "proj4-repl2.5700.network" "proj4-repl3.5700.network" "proj4-repl4.5700.network" "proj4-repl5.5700.network" "proj4-repl6.5700.network" "proj4-repl7.5700.network")
for repl in "${REPLICA_SERVERS[@]}"
do
	echo "Deploying to $repl"
	ssh -i ~/.ssh/id_ed25519 dkgp@$repl "rm -rf  .cache .config .local .bash_history"
	scp -i ~/.ssh/id_ed25519 -r httpserver/httpserver dkgp@$repl:
	rsync -a --delete httpserver/disk/ dkgp@$repl:disk/ 
done

dns_server="proj4-dns.5700.network"
echo "Deploying to $dns_server"
scp dnsserver/dnsserver dnsserver/GeoLite2-City.mmdb dkgp@$dns_server: 
ssh dkgp@$dns_server  "pip3 install -U geoip2 dnslib && chmod u+x dnsserver"