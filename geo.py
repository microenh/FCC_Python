#! /users/mark/developer/python/fcc_python/.venv/scripts/python.exe
from math import pi, sin , cos, atan2, sqrt


def grid_square(longitude, latitude):
    """
    longitude: decimal longitude -180 .. 180 (West is negative)
    latitude: decimal latitude -90 .. 90 (South is negative)
    returns 10 character string 'AA99aa99AA' (truncate for less precision)
    """
    DIVISORS = (
        (20.0, 10.0, ord('A')),
        (2.0, 1.0, ord('0')),
        (0.083333, 0.0416666, ord('a')),
        (0.0083333, 0.00416666, ord('0')),
        (0.00083333, 0.000416666, ord('A'))
    )
    latitude += 90
    longitude += 180
    results = []
    for long_div, lat_div, prefix in DIVISORS:        
        results.append(chr((lo := int(longitude / long_div)) + prefix)
                     + chr((la := int(latitude / lat_div)) + prefix))
        longitude -= lo * long_div
        latitude -= la * lat_div
    return ''.join(results)

def degrees_radians(degrees):
    return degrees * pi / 180.0

def radians_degrees(radians):
    return radians * 180.0 / pi
    
def bearing_dist(start_longitude, start_latitude,
            end_longitude, end_latitude):
    """
    start_longitude, end_longitude:
        decimal longitude -180 .. 180 (West is negative)
    start_latitude, end_latitude:
        decimal latitude -90 .. 90 (South is negative)
    calculates heading from start to end and distance
    """
    #R = 6371    # earth radius km
    R = 3959    # earth radius mi
    lat_start = degrees_radians(start_latitude)
    lon_start = degrees_radians(start_longitude)
    lat_end = degrees_radians(end_latitude)
    lon_end = degrees_radians(end_longitude)
    
    d_lon = lon_end - lon_start
    cos_lat_start = cos(lat_start)
    cos_lat_end = cos(lat_end)

    x = sin(d_lon) * cos_lat_end
    y = cos_lat_start * sin(lat_end) - sin(lat_start) * cos_lat_end * cos(d_lon)
    bearing = radians_degrees(atan2(x,y))
    if bearing < 0:
        bearing += 360

    d_lat = lat_end - lat_start
    a = sin(d_lat/2)**2 + cos_lat_start * cos(lat_end) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    dist = R * c

    return bearing, dist



    
    

if __name__ == '__main__':
    print (grid_square(-83.3940, 39.8541))
    print (bearing_dist(-83.3940, 39.8541, 0,50))
    print (coords("3105 Big Plain-Circleville Rd, 43140"))
    # print (grid_square(*coords("3105 Big Plain-Circleville Rd, 43140")))
    
                       
    
