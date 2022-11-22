import re
import json
from urllib.request import urlopen
from math import radians, cos, sin, asin, sqrt, inf

def find_closest_replica_server(source_ip):
    source_coordinates = find_location_coordinates(source_ip)
    replica_servers = ['175.253.115.99', '142.250.72.100', '204.44.192.60']
    min_dist = inf
    nearest_server = replica_servers[0]

    for server in replica_servers:
        server_coordinates = find_location_coordinates(server)
        dist = distance_between_locations(server_coordinates, source_coordinates)
        if dist < min_dist:
            nearest_server = server

    return nearest_server

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

find_location_coordinates('172.24.48.1')
# print(find_closest_replica_server('172.24.48.1'))
