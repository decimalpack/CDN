import re
import json
from urllib.request import urlopen
from math import radians, cos, sin, asin, sqrt

def distance(lat1, lon1, lat2, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
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
    lat = float(data['loc'].split(",")[0])
    lon = float(data['loc'].split(",")[1])
    
    return lat, lon

lat2 = 63
lon2 = -5.79

print(distance(*find_location_coordinates('175.253.115.99'), lat2, lon2))
