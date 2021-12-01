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


import requests
from requests.api import request
from requests.models import LocationParseError
import config
import folium
import json
from math import cos,pi,sin,asin,sqrt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
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
                    }

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
    m.put(analyzer['ciudades'],cityname,city)

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
        if not gr.containsVertex(analyzer['rutasNoDirigido'], stopid):
            gr.insertVertex(analyzer['rutasNoDirigido'], stopid)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')

def addDataAirport(analyzer,airport):
    iata = airport['IATA']
    m.put(analyzer['aeropuerto'],iata,airport)

# Funciones para creacion de datos

# Funciones de consulta
def prueba(analyzer):
    numeroAirport = m.size(analyzer['aeropuerto'])
    numeroVertices = gr.numVertices(analyzer['rutas'])
    numeroLados = gr.numEdges(analyzer['rutas'])
    numeroCiudades = m.size(analyzer['ciudades'])
    numeroVertices2 = gr.numVertices(analyzer['rutasNoDirigido'])
    numeroLados2 = gr.numEdges(analyzer['rutasNoDirigido'])

    return [numeroAirport,numeroVertices,numeroLados,numeroCiudades,numeroVertices2,numeroLados2]

def maxinterconexion(analyzer):
    lista = gr.vertices(analyzer['rutas'])
    max = 0
    for vertice in lt.iterator(lista):
      total = gr.degree(analyzer['rutas'],vertice)
      if total > max:
        max = total
    lstiata = lt.newList() 
    for vertice in lt.iterator(lista):
        if gr.degree(analyzer['rutas'],vertice) == max:
            iata = vertice
            dataairport = m.get(analyzer['aeropuerto'],iata)['value']
            lt.addLast(lstiata,dataairport)
    return (max,lstiata)



def encontrarClusteres(analyzer,aeroI,aeroF):
    """
    Req 2
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['rutas'])
    total = scc.connectedComponents(analyzer['components'])
    unidos = scc.stronglyConnected(analyzer['components'], aeroI, aeroF)
    lstiata = lt.newList() 
    dataairport1 = m.get(analyzer['aeropuerto'],aeroI)['value']
    lt.addLast(lstiata,dataairport1)
    dataairport2 = m.get(analyzer['aeropuerto'],aeroF)['value']
    lt.addLast(lstiata,dataairport2)
    
    map = folium.Map()
    cluster1 = me.getValue(m.get(analyzer['components']["idscc"],aeroI))
    cluster2 = me.getValue(m.get(analyzer['components']["idscc"],aeroF))
    lstcluster1 = lt.newList(datastructure='ARRAY_LIST')
    lstcluster2 = lt.newList(datastructure='ARRAY_LIST')
    for aero1 in lt.iterator(m.keySet(analyzer['components']["idscc"])):
        if me.getValue(m.get(analyzer['components']["idscc"],aero1)) == cluster1:
            lt.addLast(lstcluster1,aero1)
        if not unidos and me.getValue(m.get(analyzer['components']["idscc"],aero1)) == cluster2:
            lt.addLast(lstcluster2,aero1)
    for aeroIata in lt.iterator(lstcluster1):
        a = me.getValue(m.get(analyzer["aeropuerto"],aeroIata))
        folium.Marker(location=[a["Latitude"], a["Longitude"]], icon=folium.Icon(color="red")).add_to(map)
    for aeroIata in lt.iterator(lstcluster2):
        a = me.getValue(m.get(analyzer["aeropuerto"],aeroIata))
        folium.Marker(location=[a["Latitude"], a["Longitude"]], icon=folium.Icon(color="blue")).add_to(map)
    map.save("mapaClústeres.html")
    
    return total, unidos, lstiata











def usarMillas(analyzer, ciudad, millas):
    """
    GRAFICAR
    map = folium.Map()
    for aero in lt.iterator(m.keySet(analyzer['red']["distTo"])):
        print(aero)
    for aero in lt.iterator(m.valueSet(analyzer['red']["edgeTo"])):
        a = me.getValue(m.get(analyzer["aeropuerto"],aero["vertexA"]))
        b = me.getValue(m.get(analyzer["aeropuerto"],aero["vertexB"]))
        folium.Marker(location=[a["Latitude"], a["Longitude"]]).add_to(map)
        folium.Marker(location=[b["Latitude"], b["Longitude"]]).add_to(map)
        folium.PolyLine(locations=[[float(a["Latitude"]), float(a["Longitude"])],[float(b["Latitude"]), float(b["Longitude"])]]).add_to(map)
    map.save("mapaUFOS.html")
    """
    """
    Req 4
    """
    analyzer["red"] = prim.PrimMST(analyzer["rutasNoDirigido"])
    aeropuerto = cityToairport(analyzer,ciudad)
    distancia = millas/3.2
    analyzer["red"] = prim.PrimMST(analyzer["rutasNoDirigido"])
    numNodos = m.size(analyzer["red"]['distTo'])
    costoTotal = prim.weightMST(analyzer["rutasNoDirigido"],analyzer["red"])
    visitadas = lt.newList(datastructure='ARRAY_LIST')
    recorrido = m.get(analyzer["red"]['distTo'], aeropuerto)['value']
    while distancia - recorrido >= 0:
        distancia -= recorrido
        aero = m.get(analyzer["red"]['edgeTo'], aeropuerto)['value']['vertexA']
        lt.addLast(visitadas, aero)
        aeropuerto = aero
        recorrido = m.get(analyzer["red"]['distTo'], aeropuerto)['value']
    ciudades = lt.newList(datastructure='ARRAY_LIST')
    for i in lt.iterator(ciudades):
        aero = lt.getElement(visitadas,i)
        ciudad = airportTocity(analyzer, aero)
        lt.addLast(ciudades,ciudad)
        
    return numNodos, costoTotal, ciudades
    



def servicioWebExterno(analyzer, ciudadinicial, ciudadfinal):
    """
    Req 6
    """
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    h = {'content-type':  "application/x-www-form-urlencoded"}
    datos = "grant_type=client_credentials&client_id=iHOE66ZfwQyCeaHC2hisL6ga2iR5GO8l&client_secret=ZuKeobzwsVU6Es7g"
    response = requests.post(url, data=datos, headers= h)
    response_dict = json.loads(response.text)
    token = response_dict["access_token"]
    latI = str(me.getValue(m.get(analyzer["ciudades"],ciudadinicial))["lat"])
    lngI = str(me.getValue(m.get(analyzer["ciudades"],ciudadinicial))["lng"])
    
    url = "https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude="+latI+"&longitude="+lngI
    print(url)
    h = {'Authorization':  "Bearer "+token}
    response2 = requests.post(url, headers= h)
    print(response2.content)
    
    """
    latF = str(me.getValue(m.get(analyzer["ciudades"],ciudadfinal))["lat"])
    lngF = str(me.getValue(m.get(analyzer["ciudades"],ciudadfinal))["lng"])
    """


    pass

  

"""

    "type": "amadeusOAuth2Token",
    "username": "s.forerog2@uniandes.edu.co",
    "application_name": "Reto 4",
    "client_id": "iHOE66ZfwQyCeaHC2hisL6ga2iR5GO8l",
    "token_type": "Bearer",
    "access_token": "mdd3fVwDsPVahTkdulBmh9Y7HjSt",
    "expires_in": 1799,
    "state": "approved",
    "scope": ""

"""
 
    





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
    lon_min = (lon - angulo) / cos(lat *(pi/180))
    lon_max = (lon + angulo) / cos(lat *(pi/180))
    
    return [lat_min,lat_max,lon_min,lon_max]

