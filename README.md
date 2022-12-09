# CS5700 - Project4: CDN

## Collaborators

1. Alan Garcia
2. Dhruvam Kothari
3. Gowtham Potnuru

## High Level Approach

The CDN project contains 2 components, the DNS Server and the HTTP Server. The DNS server is responsible to statically assign an IP address to a client's query.
The HTTP server is responsible to serve content from the origin or from the cache.

### DNS Server

We used a combination of two approaches

1. Geolocation based routing
2. Active measurement using scamper

The algorithm for an incoming client the DNS server is as follows:

1. Is the client in `ROUTING_TABLE`? Then:
    1. Return best replica server IP address based on average latency.
2. Else:
    1. Use geolocation based routing to find the closest replica server by haversine distance.
    2. Store client ip address in a set `CLIENTS`

The `ROUTING_TABLE` is update periodically by pinging the `/ping` endpoint of the HTTP server. The `/ping` endpoint returns the latency between the `CLIENTS` and the replica server.

## HTTP Server

1. Model the cache as a 0/1 Knapsack problem and calculate optimal disk and RAM cache.
2. Use Brotli compression to compress individual files and store them in disk/ directory.
3. Expose a `/preload` endpoint to store the compressed files in RAM. As mentioned before, the preload_files for RAM have been precomputed.

## Features

### DNS Server

- The DNS server address the issue of statically assigning an IP address of the replica servers. Choosing a replica server plays a major role
in the rtt of a request from the client.
- To minimize this, a new client is assigned to a geographically closest server. The IP address of a client is translated to location coordinates and compared with
replica server coordinates.
- For all the previous clients the geolocation based strategy is changed to latency based strategy which uses active measurements.
- For every 100 seconds a batch update of clients latency between mutliple replica servers is calculated and the best replica server is assigned.
- An HTTP endpoint is exposed at every replica server through which the active measurement takes place.
We also used native parsers for the DNS protocol to speed up the CDN.

### HTTP Server

- About 90% cache hit rate is achieved by using a combination of disk and RAM cache.
- Small server binary size of <2MB, allowing more disk cache. This is achieved by optimizing the binary for size and compressing it with `upx`.

## Deployment

- See `make deploy` in the Makefile.
- For deployment we have 3 different scripts, DEPLOY | RUN | STOP
- These scripts enable us to remotely deploy the CDN and run them
- We copy the CDN relate files remotely which is the DNS files to the DNS server and HTTP SERVER files to the replica servers.
- We configure each of the servers and start.

## Challenges

- One of the main challenged was in architecting the CDN to do active measurements which uses HTTP endpoints.
- Another challenge was the geolocation based routing where we had to figure the DB to use and the formula to find the distance.
- The use of `scamper` for active measurement required some detail.
- Tradeoff of size/speed for compression. We initially achieved a 95% hit rate using aggressive compression, however the decompression times were about 1s, which was slower than fetching from origin.
- Our initial implementation of async http server with brotli used about 50MB disk space as libraries, hence we had to rewrite it in rust.
- We could achieve 93% hit rate by providing a custom dictionary for brotli compression. However, we could not implement it optimally in rust due to lack of easy library support.

## Contribution

### Alan Garcia

- Basic HTTP server setup
- Use of SCAMPER and active measurement
- Deploy scripts

### Dhruvam Kothari

- DNS setup
- HTTP server implementation
- Compression of data
- Optimizing latency and cache hit rate

### Gowtham Potnuru

- Resolving IP's for client based on geogrpahy and active measurements.
- Update client and replica server mapping
- Testing DNS and HTTP Server
