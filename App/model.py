"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """

#import geopandas as gpd
#from shapely.geometry import Polygon
import requests
from requests.api import request
from requests.models import LocationParseError, stream_decode_response_unicode
import config
import folium
import json
from math import cos,pi,sin,asin,sqrt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim
from DISClib.Utils import error as error
assert config

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'aeropuerto': None,
                    'rutas': None,
                    'components': None,
                    'paths': None,
                    'ciudades': None,
                    'red': None,
                    'IATA': None,
                    'id': None,
                    'aeropuertoLng': None
                    }

        analyzer['IATA'] = lt.newList()

        analyzer['id'] = lt.newList()

        analyzer['aeropuerto'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareIATA)

        analyzer['ciudades'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareCiudades)

        analyzer['rutas'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareIATA)

        analyzer['rutasNoDirigido'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=14000,
                                              comparefunction=compareIATA)

        analyzer['aeropuertoLng'] = om.newMap(omaptype='RBT',
                                      comparefunction=compareLongitude)

        analyzer['vuelos'] = m.newMap(numelements=14000,
                                maptype='PROBING',
                                comparefunction=compareIATA)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo
def addAirport(analyzer, route):
    salida = route['Departure']
    llegada = route['Destination']
    addStop(analyzer,salida)
    addStop(analyzer,llegada)
    

def addRoute(analyzer,route):
    salida = route['Departure']
    llegada = route['Destination']
    distancia = float(route['distance_km'])
    addConnection(analyzer, salida, llegada, distancia)

def addCity(analyzer,city):
    cityname = city['city_ascii']
    existe = m.contains(analyzer['ciudades'],cityname)
    if existe == False:
        vacia = lt.newList()
        lt.addLast(vacia,city)
        m.put(analyzer['ciudades'],cityname,vacia)
    else:
        lista = m.get(analyzer['ciudades'],cityname)['value']
        lt.addLast(lista,city)
    cityid = city['id']
    lt.addLast(analyzer['id'],cityid)
    

def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['rutas'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['rutas'], origin, destination, distance)
        if gr.getEdge(analyzer['rutas'], destination, origin):
            gr.addEdge(analyzer['rutasNoDirigido'], origin, destination, distance)
    return analyzer

def addStop(analyzer, stopid):
    """ 
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['rutas'], stopid):
            gr.insertVertex(analyzer['rutas'], stopid)
            lt.addLast(analyzer['IATA'],stopid) 
        if not gr.containsVertex(analyzer['rutasNoDirigido'], stopid):
            gr.insertVertex(analyzer['rutasNoDirigido'], stopid)
        aero = m.contains(analyzer['vuelos'],stopid)
        if aero == False:
            dict = {'entraV': lt.newList(),'saleV' : lt.newList()}
            m.put(analyzer['vuelos'],stopid,dict)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')

def addDataAirport(analyzer,airport):
    iata = airport['IATA']
    m.put(analyzer['aeropuerto'],iata,airport)
    #lt.addLast(analyzer['IATA'],iata) 
    addStop(analyzer, iata)
    updateLongitudeIndexAero(analyzer['aeropuertoLng'], airport)

def updateLongitudeIndexAero(map, aero):
    """
    Se toma la longitud del aeropuerto y se busca si ya existe en el arbol
    dicha longitud.  Si es asi, se adiciona a su lista de avistamientos.
    Si no se encuentra creado un nodo para esa longitud en el arbol
    se crea uno
    """
    longitude = float(aero['Longitude'])
    entry = om.get(map, longitude)
    if entry is None:
        datentry = newLongitudeEntryAero(longitude)
        om.put(map, longitude, datentry)
    else:
        datentry = me.getValue(entry)
    addLongitudeIndexAero(datentry, aero)
    return map

def updateLatitudeIndexAero(map, aero):
    """
    Se toma la latitud del avistamiento y se busca si ya existe en el arbol
    dicha latitud.  Si es asi, se adiciona a su lista de avistamientos.
    Si no se encuentra creado un nodo para esa latitud en el arbol
    se crea uno
    """
    latitude = float(aero['Latitude'])
    entry = om.get(map, latitude)
    if entry is None:
        datentry = newLatitudeEntryAero(latitude)
        om.put(map, latitude, datentry)
    else:
        datentry = me.getValue(entry)
    addLatitudeIndexAero(datentry, aero)
    return map


def addLongitudeIndexAero(datentry, avistamiento):
    """
    Actualiza un indice.  Este indice tiene una lista
    de avistamientos y una tabla de hash cuya llave es la longitud y
    el valor es un mapa con la latitud como llave y valor los avistamientos de
    la longitud que se está consultando (dada por el nodo del arbol)
    """
    updateLatitudeIndexAero(datentry['latitudeIndex'], avistamiento)
    return datentry


def addLatitudeIndexAero(datentry, avistamiento):
    """
    Actualiza un indice.  Este indice tiene una lista
    de avistamientos y una tabla de hash cuya llave es la latitud y
    el valor es una lista con los avistamientos de dicho tipo en la latitud que
    se está consultando (dada por el nodo del arbol)
    """
    lst = datentry['lstAeros']
    lt.addLast(lst, avistamiento)
    return datentry

def newLongitudeEntryAero(longitude):
    """
    Crea una entrada en el indice por aeropuerto, es decir en el arbol
    binario.
    """
    longitudentry = {'longitude': None, 'latitudeIndex': None}
    longitudentry['longitude'] = longitude
    longitudentry['latitudeIndex'] = om.newMap(omaptype='RBT',
                                      comparefunction=compareLatitude)
    return longitudentry


def newLatitudeEntryAero(latitude):
    """
    Crea una entrada en el indice por ciudad, es decir en el arbol
    binario.
    """
    latitudentry = {'latitude': None, 'lstAeros': None}
    latitudentry['latitude'] = latitude
    latitudentry['lstAeros'] = lt.newList('SINGLE_LINKED', compareLongitude)
    return latitudentry

def addVuelo(analyzer,route):
    iataS = route['Departure']
    iataD = route['Destination']
    listaS = m.get(analyzer['vuelos'],iataS)['value']['saleV']
    listaD = m.get(analyzer['vuelos'],iataD)['value']['entraV']
    lt.addLast(listaS,route)
    lt.addLast(listaD,route)

# Funciones para creacion de datos

# Funciones de consulta
def prueba(analyzer):
    numeroAirport = m.size(analyzer['aeropuerto'])
    numeroVertices = gr.numVertices(analyzer['rutas'])
    numeroLados = gr.numEdges(analyzer['rutas'])
    numeroCiudades = lt.size(analyzer['id'])
    numeroVertices2 = gr.numVertices(analyzer['rutasNoDirigido'])
    numeroLados2 = gr.numEdges(analyzer['rutasNoDirigido'])
    iata = lt.getElement(analyzer['IATA'],1)
    iata2 = lt.getElement(analyzer['IATA'],numeroVertices)
    id = lt.getElement(analyzer['id'],1)
    id2 = lt.getElement(analyzer['id'],numeroCiudades)
    datosaero = m.get(analyzer['aeropuerto'],iata)['value']
    datosaero2 = m.get(analyzer['aeropuerto'],iata2)['value']
    for city in lt.iterator(m.valueSet(analyzer['ciudades'])): 
        for data in lt.iterator(city):
            if data['id'] == id:
                datoscity = data
            if data['id'] == id2:
                datoscity2 = data
    vuelostotales = 0
    for iata in lt.iterator(m.valueSet(analyzer['vuelos'])):
        saleV = lt.size(iata['saleV'])
        entraV = lt.size(iata['entraV'])
        vuelostotales = vuelostotales + saleV + entraV 
    vuelostotales = vuelostotales / 2 
    return [numeroAirport,numeroVertices,numeroLados,numeroCiudades,numeroVertices2,numeroLados2,datosaero,datosaero2,datoscity,datoscity2,vuelostotales]

def maxinterconexion(analyzer):
    lista = m.valueSet(analyzer['vuelos'])
    max = lt.newList()
    lt.addFirst(max,0)
    for vertice in lt.iterator(lista):
      total = lt.size(vertice['saleV']) + lt.size(vertice['entraV'])
      temp = lt.getElement(max,1)
      if total > temp:
          lt.addFirst(max,total)
      else:
          for i in range(2,lt.size(max)):
              temp2 = lt.getElement(max,i)
              if total > temp2 and total < lt.getElement(max,i-1):
                  lt.insertElement(max,total,i)
                  break
    lstiata = lt.newList() 
    listaK = m.keySet(analyzer['vuelos'])
    for i in lt.iterator(max):
        for vertice in lt.iterator(listaK):
            dict = m.get(analyzer['vuelos'],vertice)['value']
            grado = lt.size(dict['saleV']) + lt.size(dict['entraV'])
            if grado == i:
                iata = vertice
                dataairport = m.get(analyzer['aeropuerto'],iata)['value']
                dataairport['sale'] = str(lt.size(dict['saleV']))
                dataairport['entra'] = str(lt.size(dict['entraV']))
                dataairport['grado'] = str(grado)
                lt.addLast(lstiata,dataairport)
        if lt.size(lstiata) > 5:
            break 
    return (lt.getElement(max,1),lt.subList(lstiata,1,5))
    


def encontrarClusteres(analyzer,aeroI,aeroF):
    """
    Req 2
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['rutas'])
    total = scc.connectedComponents(analyzer['components'])
    unidos = scc.stronglyConnected(analyzer['components'], aeroI, aeroF)

    
    map = folium.Map()
    cluster1 = me.getValue(m.get(analyzer['components']["idscc"],aeroI))
    cluster2 = me.getValue(m.get(analyzer['components']["idscc"],aeroF))
    dataairport1 = me.getValue(m.get(analyzer['aeropuerto'],aeroI))
    dataairport2 = me.getValue(m.get(analyzer['aeropuerto'],aeroF))
    lat_point_list1 = []
    lon_point_list1 = []
    lat_point_list2 = []
    lon_point_list2 = []
    for aero1 in lt.iterator(m.keySet(analyzer['components']["idscc"])):
        if me.getValue(m.get(analyzer['components']["idscc"],aero1)) == cluster1:
            a = me.getValue(m.get(analyzer["aeropuerto"],aero1))
            lat_point_list1.append(float(a["Latitude"]))
            lon_point_list1.append(float(a["Longitude"]))
        if not unidos and me.getValue(m.get(analyzer['components']["idscc"],aero1)) == cluster2:
            a = me.getValue(m.get(analyzer["aeropuerto"],aero1))
            lat_point_list2.append(float(a["Latitude"]))
            lon_point_list2.append(float(a["Longitude"]))
    
    if len(lat_point_list1) > 2:
        polygon_geom = Polygon(zip(lon_point_list1, lat_point_list1))
        polygon_geom2 = polygon_geom.convex_hull
        folium.GeoJson(polygon_geom2, style_function= lambda x: {"color":"blue"}).add_to(map)
    elif len(lat_point_list1) == 2:
        folium.PolyLine(locations=[[float(lat_point_list1[0]), float(lon_point_list1[0])],[float(lat_point_list1[1]), float(lon_point_list1[1])]]).add_to(map)
    
    if len(lat_point_list2) > 2:
        polygon_geom = Polygon(zip(lon_point_list2, lat_point_list2))
        polygon_geom2 = polygon_geom.convex_hull
        folium.GeoJson(polygon_geom2, style_function= lambda x: {"color":"red"}).add_to(map)
    elif len(lat_point_list2) == 2:
        folium.PolyLine(locations=[[float(lat_point_list2[0]), float(lon_point_list2[0])],[float(lat_point_list2[1]), float(lon_point_list2[1])]]).add_to(map)
    
    folium.Marker(location=[dataairport1["Latitude"], dataairport1["Longitude"]], icon=folium.Icon(color="blue")).add_to(map)
    folium.Marker(location=[dataairport2["Latitude"], dataairport2["Longitude"]], icon=folium.Icon(color="red")).add_to(map)
        
    map.save("mapaClústeres.html")
    return total, unidos
   



def usarMillas(analyzer, ciudad, millas):
    """
    Req 4
    """
    analyzer["red"] = prim.PrimMST(analyzer["rutasNoDirigido"])
    aeropuerto = cityToairport(analyzer,ciudad)['IATA']
    distancia = millas*1.6
    numNodos = 0
    listaNodos = lt.newList(datastructure='ARRAY_LIST')
    for a in lt.iterator(m.valueSet(analyzer["red"]['edgeTo'])):
        llegadaNodo = a['vertexA']
        if not lt.isPresent(listaNodos,llegadaNodo):
            lt.addLast(listaNodos, llegadaNodo)
        salidaNodo = a['vertexB']
        if not lt.isPresent(listaNodos,salidaNodo):
            lt.addLast(listaNodos, salidaNodo)
    numNodos = lt.size(listaNodos)
    costoTotal = round(prim.weightMST(analyzer["rutasNoDirigido"],analyzer["red"]),2)
    visitadas = lt.newList(datastructure='ARRAY_LIST')
    recorrido = m.get(analyzer["red"]['distTo'], aeropuerto)['value']
    terminar = False
    distanciaTotal = 0
    while not terminar:
        distancia -= recorrido*2
        distanciaTotal += recorrido*2
        aero = m.get(analyzer["red"]['edgeTo'], aeropuerto)
        if aero:
            llegada = aero['value']['vertexA']
            salida = aero['value']['vertexB']
            peso = aero['value']['weight']
            ciudad = me.getValue(m.get(analyzer['aeropuerto'],llegada))["City"]
            ruta = {"salida":salida,"llegada":llegada,"distancia":peso,"ciudad":ciudad}
            lt.addLast(visitadas, ruta)
            aeropuerto = llegada
            recorrido = m.get(analyzer["red"]['distTo'], aeropuerto)['value']
        else:
            terminar = True

    distanciaTotal = round(distanciaTotal,2)
    distancia = round((distancia/1.6),2)
    
    
    map = folium.Map()
    for ruta in lt.iterator(visitadas):
        a = me.getValue(m.get(analyzer["aeropuerto"],ruta["salida"]))
        b = me.getValue(m.get(analyzer["aeropuerto"],ruta["llegada"]))
        folium.Marker(location=[a["Latitude"], a["Longitude"]]).add_to(map)
        folium.Marker(location=[b["Latitude"], b["Longitude"]]).add_to(map)
        folium.PolyLine(locations=[[float(a["Latitude"]), float(a["Longitude"])],[float(b["Latitude"]), float(b["Longitude"])]]).add_to(map)
    map.save("mapaMST.html")

    return numNodos, costoTotal, visitadas, distanciaTotal, distancia
    



def servicioWebExterno(analyzer, ciudadinicial, ciudadfinal):
    """
    Req 6
    """
    latI = str(ciudadinicial["lat"])
    lngI = str(ciudadinicial["lng"])
    latF = str(ciudadfinal["lat"])
    lngF = str(ciudadfinal["lng"])
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    h = {'content-type':  "application/x-www-form-urlencoded"}
    datos = "grant_type=client_credentials&client_id=iHOE66ZfwQyCeaHC2hisL6ga2iR5GO8l&client_secret=ZuKeobzwsVU6Es7g"
    response = requests.post(url, data=datos, headers= h)
    response_dict = json.loads(response.text)
    token = response_dict["access_token"]
    hToken = {'Authorization':  "Bearer "+token}
    urlCityInicial = "https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude="+latI+"&longitude="+lngI
    responseInicial = requests.get(urlCityInicial, headers= hToken)
    response_dictInicial = json.loads(responseInicial.text)
    aeroInicial = response_dictInicial["data"][0]

    urlCityFinal = "https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude="+latF+"&longitude="+lngF
    responseFinal = requests.get(urlCityFinal, headers= hToken)
    response_dictFinal = json.loads(responseFinal.text)
    aeroFinal = response_dictFinal["data"][0]  
    
    analyzer["pathsAPI"] = djk.Dijkstra(analyzer["rutas"],aeroInicial["iataCode"])
    camino = djk.pathTo(analyzer["pathsAPI"], aeroFinal["iataCode"])
    distancia = djk.distTo(analyzer["pathsAPI"], aeroFinal["iataCode"])
    distancia = round((distancia + aeroInicial['distance']['value'] + aeroFinal['distance']['value']),2)
    return camino, distancia
  

def cityToairport(analyzer,ciudad):
    """
    asocia aeropuerto mas cercano a una ciudad dada 
    en primer lugar, hace una lista de los aeropuertos a menos de 10km de la ciudad, sino encuentra ninguno
    aumenta el radio de busqueda a 20km y seguira aumentando el radio de busqueda haata encontrar algun aeropuerto
    si en la región de busqueda hay mas de un aeropuerto se selecciona el aeropuerto mas cercano a la ciudad 
    """
    citydata = ciudad
    citylat = float(citydata['lat'])
    citylon = float(citydata['lng'])
    lista = lt.newList()
    km = 10
    while lt.size(lista) == 0:
        area = areabusqueda(citylat,citylon,km)
        rangoLong = om.values(analyzer["aeropuertoLng"],area[2],area[3])
        if lt.size(rangoLong) > 0:
            for long in lt.iterator(rangoLong):
                rangoLat = om.values(long["latitudeIndex"],area[0],area[1])
                for lat in lt.iterator(rangoLat):
                    for aero in lt.iterator(lat["lstAeros"]):
                        lt.addLast(lista,aero)
        km += 10 

    if lt.size(lista) == 1:
        return lt.getElement(lista,1)
    else:
        min = km 
        aeropuerto = None
        for aero in lt.iterator(lista):
            if dist(citylat, float(aero['Latitude']), citylon, float(aero['Longitude'])) < min:
                min = dist(citylat, float(aero['Latitude']), citylon, float(aero['Longitude']))
                aeropuerto = aero
        return aeropuerto 





def rutasMin(grafo,vertice):
    return djk.Dijkstra(grafo,vertice)

def camino(paths,vertice):
    return djk.pathTo(paths,vertice)

def adyacencia(analyzer,iata):
    return gr.adjacents(analyzer['rutas'],iata)

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento
def compareIATA(IATA1,IATA2):
    if type(IATA2) == dict:
        iata = IATA2['key']
        IATA2 = iata  
    if (IATA1 == IATA2):
        return 0
    elif (IATA1 > IATA2):
        return 1
    else:
        return -1

def compareCiudades(ciudad1,ciudad2): 
    if type(ciudad2) == dict:
        ciudad = ciudad2['key']
        ciudad2 = ciudad
    if (ciudad1 == ciudad2):
        return 0
    elif (ciudad1 > ciudad2):
        return 1
    else:
        return -1


def compareLongitude(lon1, lon2):
    """
    Compara dos longitudes
    """
    if (lon1 == lon2):
        return 0
    elif (lon1 > lon2):
        return 1
    else:
        return -1



def compareLatitude(lat1, lat2):
    """
    Compara dos latitudes
    """
    if (lat1 == lat2):
        return 0
    elif (lat1 > lat2):
        return 1
    else:
        return -1


# Funciones adicionales
def iterador(lst):
    return lt.iterator(lst)

def areabusqueda(lat,lon,radio):
    """
    devuelve las coordenadas de un cuadrado con centro en el punto: (lat,lon) con un radio dado
    """
    radianes = radio/6371.0
    angulo = radianes * 180/pi
    lat_min = lat - angulo 
    lat_max = lat + angulo
    lon_min = lon - angulo / cos(lat *(pi/180))
    lon_max = lon + angulo / cos(lat *(pi/180))

    return [lat_min,lat_max,lon_min,lon_max]

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

def mget(map,llave):
    return m.get(map,llave)

def ltsize(lista):
    return lt.size(lista)

def ltgetElement(lista,pos):
    return lt.getElement(lista,pos)

def ltnewList():
    return lt.newList()

def ltAddLast(lista,elem):
    return lt.addLast(lista,elem)
    lon_min = (lon - angulo) / cos(lat *(pi/180))
    lon_max = (lon + angulo) / cos(lat *(pi/180))
    
    return [lat_min,lat_max,lon_min,lon_max]

def concatlist(lst1,lst2):
    """
    Recibe dos listas, agrega los elementos de la segunda lista al final de la primera y retorna dicha lista 
    """
    for elem in lt.iterator(lst2):
        lt.addLast(lst1,elem)
    return lst1

def sublista(lista,posi,long):
    return lt.subList(lista,posi,long)
    return lt.addLast(lista,elem)
    return lt.addLast(lista,elem)
