#!/usr/bin/python3
"""Strategy: Always origin"""
import argparse
import logging
import socket
from typing import Tuple
import threading
import heapq
from queue import PriorityQueue
from dnslib import *
import requests
import json
from urllib.request import urlopen
from math import radians, cos, sin, asin, sqrt, inf

def get_ip_address():
    """Get local IP address.

    Returns
    -------
    IPv4Address
        Local IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


ORIGIN = "cs5700cdnorigin.ccs.neu.edu"
ORIGIN_IP = socket.gethostbyname(ORIGIN)
CLIENT_REPLICA_ROUTING_TABLE = {}
REPLICA_SERVERS = []

def find_closest_replica_server(source_ip):
    source_coordinates = find_location_coordinates(source_ip)
    replica_servers = ['175.253.115.99', '142.250.72.100', '204.44.192.60']
    min_dist = inf
    closest_server = replica_servers[0]

    for server in replica_servers:
        server_coordinates = find_location_coordinates(server)
        dist = distance_between_locations(server_coordinates, source_coordinates)
        if dist < min_dist:
            closest_server = server

    return closest_server

def distance_between_locations(loc1, loc2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(loc1[0])
    lon2 = radians(loc1[1])
    lat1 = radians(loc2[0])
    lat2 = radians(loc2[1])
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)

def find_location_coordinates(ip):
    url = 'http://ipinfo.io/' + ip + '/json'
    response = urlopen(url)
    data = json.load(response)
    print(data)
    lat = float(data['loc'].split(",")[0])
    lon = float(data['loc'].split(",")[1])
    
    return (lat, lon)

def resolve(client_address: Tuple[str, int])->str:
    client_ip = client_address[0]
    
    if client_ip in CLIENT_REPLICA_ROUTING_TABLE:
        return CLIENT_REPLICA_ROUTING_TABLE[client_ip]
    
    else:
        closest_server = find_closest_replica_server(client_ip)
        CLIENT_REPLICA_ROUTING_TABLE[client_ip] = closest_server

    return ORIGIN_IP

def parse_args():
    parser = argparse.ArgumentParser(description='DNS Server')
    parser.add_argument("-p",
                        "--port",
                        required=True,
                        type=int,
                        help='Port to listen on')
    parser.add_argument("-n",
                        "--name",
                        required=True,
                        help='CDN specific name')
    return parser.parse_args()

def serve_dns(port, server_domain):

    localIP = get_ip_address()
    bufferSize = 1024

    udp_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_sock.bind((localIP, port))
    logging.info(f"Listening on {localIP}:{port}")

    while True:
        message, address = udp_sock.recvfrom(bufferSize)
        query = DNSRecord.parse(message)
        logging.debug(f"Received {query} from {address}")
        repsonse = DNSRecord(DNSHeader(id=query.header.id, qr=0, aa=1,
                                          ra=1),
                                a=RR(server_domain,
                                     rdata=A(resolve(address))))
        logging.debug(f"Sending {repsonse} to {address}")
        udp_sock.sendto(repsonse.pack(), address)

def ping(client_ip, replica_ip):
    return requests.get('http://' + replica_ip + '/ping?client=' + client_ip)

def ping_replicas(client_ip):
    q = PriorityQueue()
    for replica in REPLICA_SERVERS:
        ping_time = ping(client_ip)
        q.put((ping_time, replica))
    
    CLIENT_REPLICA_ROUTING_TABLE[client_ip] = q.get()[1]

def update_client_replica_routing():
    for client in CLIENT_REPLICA_ROUTING_TABLE:
        ping_replicas(client)
    
    threading.Timer(300, update_client_replica_routing).start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    update_client_replica_routing()
    serve_dns(args.port, args.name)