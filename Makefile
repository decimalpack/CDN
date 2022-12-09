submit:
	zip Project5-CDN.zip *CDN dnsserver Makefile
httpserver: FORCE
	cd httpserver && cargo build --release && upx --best --lzma target/release/httpserver && mv target/release/httpserver .
	rm -rf httpserver/target
deploy: FORCE
	./stopCDN -p 25015 -o http://cs5700cdnorigin.ccs.neu.edu:8080/ -n cs5700cdn.example.com -u dkgp -i ~/.ssh/id_ed25519
	./deployCDN -p 25015 -o http://cs5700cdnorigin.ccs.neu.edu:8080/ -n cs5700cdn.example.com -u dkgp -i ~/.ssh/id_ed25519
	./runCDN -p 25015 -o http://cs5700cdnorigin.ccs.neu.edu:8080/ -n cs5700cdn.example.com -u dkgp -i ~/.ssh/id_ed25519

FORCE: