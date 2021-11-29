
from math import cos,pi,sin,asin,sqrt


def dist(lat1,lat2,lon1,lon2):
    """
    devuelve la distancia en km entre dos puntos del planeta
    """
    lat1 = lat1 * (pi/180)
    lat2 = lat2 * (pi/180)
    lon1 = lon1 * (pi/180)
    lon2 = lon2 * (pi/180)
    v1 = sin((lat2-lat1)/2)
    v2 = sin((lon2-lon1)/2)
    return 2 * 6367 * asin(sqrt(v1**2 + cos(lat1) * cos(lat2) * v2 ** 2))

l1 = 0
l2 = 0
l3 = 0
l4 = 90
l5 = pi/2

print(dist(l1,l2,l3,l4))
print(dist(l1,l2,l3,l5))

latT = 35.6897
lonT = 139.6922
latH = 35.5523
lonH = 139.7799
print(dist(latH,latH,lonT,lonH))