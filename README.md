CS5700 - Project4: CDN

Collaborators: Alan Garcia, Dhruvam K, Gowtham Potnuru

High Level Approach:

The CDN project contains 2 components, the DNS Server and the HTTP Server. The DNS server is responsible to statically assign an IP address to a client's query.
The HTTP server is responsible to serve content from the origin or from the cache.
We identified that for a faster CDN, the rtt has to be the least between the client and the http server. For this to happen, the client should be mapped to the 
best possible replica server and also we have to reduce the dependency of the origin server which increase the rtt.
Keep these 2 things in mind, we came up with a strategy to design a fast CDN. 

Features:

DNS Server
- The DNS server address the issue of statically assigning an IP address of the replica servers. Choosing a replica server plays a major role
in the rtt of a request from the client.
- To minimize this, a new client is assigned to a geographically closest server. The IP address of a client is translated to location coordinates and compared with
replica server coordinates.
- For all the previous clients the geolocation based strategy is changed to latency based strategy which uses active measurements.
- For every 100 seconds a batch update of clients latency between mutliple replica servers is calculated and the best replica server is assigned.
- An HTTP endpoint is exposed at every replica server through which the active measurement takes place.
We also used native parsers for the DNS protocol to speed up the CDN.

HTTP Server
- The HTTP server address the issue of serving the content rapidly to the client. The origin server contains the whole dataset and each of the replicas contain part of the data (20MB) which acts as a cache.
- Inorder to minize the rtt, it is important to have high hit rate. There are 2 parts to this, to imrpove the hit rate the initial data preloaded into the cache matters.
- We tried to fill the cache considering 2 factors - popularity of the wesbites and the size of the content. It is like solving a knapsack problem.
- Once the cache is preloaded, if there is a cache miss the content is replaces using the LFU strategy. The least frequenctly used content is replaced with the new content.
- Another optimization is loading more content into the cache which increases the hit rate. 
 So we used Brotli compression to compress the web content and store more data inside the cache.
- Another important feature of the HTTP server is the continuous active measurement which helps the DNS to map best replica servers. The DNS server hits the /ping endpoint to which activcates the scamper.
We use scamper to measure the latency between the replica server and the clients. The data collected is returned to the DNS server.

Deployment:

- For deployment we have 3 different scripts, DEPLOY | RUN | STOP
- These scripts enable us to remotely deploy the CDN and run them
- We copy the CDN relate files remotely which is the DNS files to the DNS server and HTTP SERVER files to the replica servers. 
- We configure each of the servers and start.

Challenges:

- One of the main challenged was in architecting the CDN to do active measurements which uses HTTP endpoints.
- Another challenge was the geolocation based routing where we had to figure the DB to use and the formula to find the distance.
- The use of SCAMPER for active measurement required some detail.
- Another big issue was the tradeoff between compression size and decompression times. We had to evaluate the rtt from the origin and decompression times from the disk.

Contribution:

Alan Garcia
- Basic HTTP server setup
- Use of SCAMPER and active measurement
- Deploy scripts

Dhruvam Kothari
- DNS setup
- HTTP server cache implementation 
- Compression of data
- Optimizing latency and cache hit rate

Gowtham Potnuru
- Resolving IP's for client based on geogrpahy and active measurements.
- Update client and replica server mapping
- Testing DNS and HTTP Server
