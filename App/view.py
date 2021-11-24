"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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

import sys
import config
import threading
import folium
from flask import Flask
from App import controller
from DISClib.ADT import stack
from prettytable import PrettyTable
assert config

routefile = 'routes_full.csv'
airportfile = 'airports_full.csv'
cityfile = 'worldcities.csv'
initialRoute = None

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Encontrar puntos de interconexión aérea")
    print("2- Encontrar clústeres de tráfico aéreo")
    print("3- Encontrar la ruta más corta entre ciudades")
    print("4- Utilizar las millas de viajero")
    print("5- Cuantificar el efecto de un aeropuerto cerrado")
    print("6- Comparar con servicio WEB externo")
    #print("7- Visualializar gráficamente los requerimientos")

def prueba(cont):
    return controller.prueba(cont)

catalog = None

def salto(cad,lon): #texto muy largo 
	if len(cad)>lon:
		pos=lon-1
		for i in cad[lon-1:0:-1]:
			if i==" ":
				sal=cad[0:pos]+"\n"+salto(cad[pos+1:],lon)
				return sal
			pos=pos-1
		sal=cad[0:lon-1]+"\n"+salto(cad[lon-1:],lon)
		return sal
	else:
		return cad

def maxaero(lstaero):
    x = PrettyTable()
    x.field_names = ['IATA','Nombre aeropuerto','Ciudad','Pais']
    for aeropuerto in controller.iterador(lstaero):
        renglon = [salto(aeropuerto['IATA'],18),salto(aeropuerto['Name'],18),salto(aeropuerto['City'],18),salto(aeropuerto['Country'],18)]
        x.add_row(renglon)
    print(x)

def printmap(listaaero):

    numeroaero = 0
    sumalat = 0
    sumalon = 0
    for aero in controller.iterador(listaaero):
        sumalat = sumalat + float(aero['Latitude'])
        sumalon = sumalon + float(aero['Longitude'])
        numeroaero += 1 
    lat_prom = sumalat/numeroaero
    lon_prom = sumalon/numeroaero
    
    if numeroaero == 1:
        zoom = 15 
    else:
        zoom = 5

    app = Flask(__name__)
    @app.route('/')
    
    def index():
        start_coords = (lat_prom,lon_prom)
        folium_map = folium.Map(location=start_coords,
                            tiles="Stamen Terrain",
                            #min_lot=-109.05,
                            #max_lot=-103.00,
                            #min_lat=31.33,
                            #max_lat=37.00,
                            #max_bounds=True,
                            zoom_start= zoom,
                            #max_zoom = 5,
                            #min_zoom =4,
                            width = '100%',
                            height = '100%') 
                            #zoom_control=False)
        for i in controller.iterador(listaaero):
            folium.Marker([float(i['Latitude']),float(i['Longitude'])],popup='<i>' + i['Name'] + '</i>').add_to(folium_map)
            #folium.PolyLine(listaaero,color='red').add_to(folium_map)
        return folium_map._repr_html_()


    """"
    tooltip = "Click me!"

    folium.Marker(
    [45.3288, -121.6625], popup="<i>Mt. Hood Meadows</i>", tooltip=tooltip
    ).add_to(folium_map)
    folium.Marker(
    [45.3311, -121.7113], popup="<b>Timberline Lodge</b>", tooltip=tooltip
    ).add_to(folium_map)
    """
    if __name__ == '__main__':
        app.run() 


"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 0:
        print("Cargando información de los archivos ....")
        cont = controller.init()
        controller.loadServices(cont, routefile,airportfile,cityfile)
        carga = prueba(cont)
        print('El total de aeropuertos cargados es: ' + str(carga[0]))
        print('El total de vertices cargados es: ' + str(carga[1]))
        print('El número de rutas cargadas es: ' + str(carga[2]))
        print('El número de ciudades cargadas es: ' + str(carga[3]))

    elif int(inputs[0]) == 1:
        print('Determinando aeropuerto asociado a mayor número de rutas... ')
        total = controller.maxinterconexion(cont)
        print('El maximo numero de rutas asociado a un aeropuerto es ' + str(total[0]))
        maxaero(total[1])
        print('Para visualizar el mapa con las observaciones siga el enlace que se genera a continuación: ')
        printmap(total[1])

    elif int(inputs[0]) == 3:
        ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
        ciudadfinal = input('Ingrese la ciudad de destino (código ascii) : ')
        

    else:
        sys.exit(0)
sys.exit(0)

