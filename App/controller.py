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
 """

import config as cf
from App import model
import csv

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros
def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer

# Funciones para la carga de datos
def loadServices(analyzer, routefile,airportfile,cityfile):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    routefile = cf.data_dir + routefile 
    input_file = csv.DictReader(open(routefile, encoding="utf-8"),
                                delimiter=",")

    airportfile = cf.data_dir + airportfile 
    input_file2 = csv.DictReader(open(airportfile, encoding="utf-8"),
                                delimiter=",")

    cityfile = cf.data_dir + cityfile 
    input_file3 = csv.DictReader(open(cityfile, encoding="utf-8"),
                                delimiter=",")                            

    #lastservice = None
    """
    for service in input_file:
        if lastservice is not None:
            sameservice = lastservice['ServiceNo'] == service['ServiceNo']
            samedirection = lastservice['Direction'] == service['Direction']
            samebusStop = lastservice['BusStopCode'] == service['BusStopCode']
            if sameservice and samedirection and not samebusStop:
                model.addStopConnection(analyzer, lastservice, service)
        lastservice = service
    model.addRouteConnections(analyzer)
    return analyzer
    """
    for route in input_file:
        model.addAirport(analyzer,route)
        model.addRoute(analyzer,route)

    for airport in input_file2:
        model.addDataAirport(analyzer,airport)

    for city in input_file3:
        model.addCity(analyzer,city)

    return analyzer
# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
def prueba(analyzer):
    return model.prueba(analyzer)

def maxinterconexion(analyzer):
    return model.maxinterconexion(analyzer)

def encontrarClusteres(cont,aeropuertoinicial,aeropuertofinal):
    return model.encontrarClusteres(cont,aeropuertoinicial,aeropuertofinal)

def cityToairport(analyzer,ciudad):
    return model.cityToairport(analyzer,ciudad)

def rutasMin(grafo,vertice):
    return model.rutasMin(grafo,vertice)

def camino(paths,vertice):
    return model.camino(paths,vertice)



def usarMillas(cont, ciudad, millas):
    return model.usarMillas(cont, ciudad, millas)

# Funciones para enmascarar
def iterador(lst):
    return model.iterador(lst)

def mget(map,llave):
    return model.mget(map,llave)

def ltsize(lista):
    return model.ltsize(lista)

def ltgetElement(lista,pos):
    return model.ltgetElement(lista,pos)

def ltnewList():
    return model.ltnewList()

def ltAddLast(lista,elem):
    return model.ltAddLast(lista,elem)