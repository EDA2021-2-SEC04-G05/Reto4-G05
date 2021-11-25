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


import config
from math import cos,pi
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
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
                    'ciudades':None
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
    return analyzer

def addStop(analyzer, stopid):
    """ 
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['rutas'], stopid):
            gr.insertVertex(analyzer['rutas'], stopid)
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

    return [numeroAirport,numeroVertices,numeroLados,numeroCiudades]

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
    return total, unidos











def usarMillas(analyzer, ciudad, millas):
    """
    Req 4
    """
    distancia = millas/1.6
    analyzer["paths"] = djk.Dijkstra(analyzer["rutas"], ciudad)
    print(analyzer["paths"]['source'])
    print(analyzer["paths"]['iminpq'])






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