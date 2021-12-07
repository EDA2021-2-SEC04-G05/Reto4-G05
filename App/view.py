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
import json
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

def printClusteres(result):
    x = PrettyTable()
    x.field_names = ['Num. Total Clústeres', "Están Conectados"]
    renglon = [salto(str(result[0]),18),salto(str(result[1]),18)]
    x.add_row(renglon)
    print(x)
    



def printMillas(result):
    x = PrettyTable()
    x.field_names = ['Numero de nodos', "Costo total [km]"]
    renglon = [salto(str(result[0]),18),salto(str(round(result[1],2)),18)]
    x.add_row(renglon)
    print(x)
    print("Se recomiendan visitar las siguientes ciudades de acuerdo a la cantidad de millas:")
    y = PrettyTable()
    y.field_names = ['Ciudades']
    for ciudad in controller.iterador(result[2]):
        renglon = [salto(str(ciudad),18)]
        y.add_row(renglon)
    print(y)



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

def printmap2(listaaero):

    lista = []
    for i in controller.iterador(listaaero):
        lista.append([float(i['Latitude']),float(i['Longitude'])])
            #lista.append(float(i['Latitude']),float(i['Longitude']))
            #folium.Marker([float(i['Latitude']),float(i['Longitude'])],popup='<i>' + i['Name'] + '</i>').add_to(folium_map)
    for i in range(len(lista)-1):
        if lista[i][1] - lista[i+1][1] > 180:
            temp = lista[i+1][1] + 360 
            lista[i+1][1] = temp 
        if lista[i][1] - lista[i+1][1] < -180:
            temp = lista[i+1][1] - 360 
            lista[i+1][1] = temp 

    numeroaero = 0
    sumalat = 0
    sumalon = 0
    for aero in lista:
        sumalat = sumalat + aero[0]
        sumalon = sumalon + aero[1]
        numeroaero += 1 
    lat_prom = sumalat/numeroaero
    lon_prom = sumalon/numeroaero
    
    if numeroaero == 1:
        zoom = 15 
    else:
        zoom = 5

    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
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
    
        for i in range(len(lista)):
          aero = controller.ltgetElement(listaaero,i+1)
          folium.Marker(lista[i],popup='<i>' + aero['Name'] + '</i>').add_to(folium_map)
        folium.PolyLine(lista,color='red').add_to(folium_map)
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

def printmap3(listaaero,cerrado):

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
        icono = folium.Icon(color='red',icon='ban')
        folium.Marker([float(cerrado['Latitude']),float(cerrado['Longitude'])],popup='<i>' + cerrado['Name'] + '</i>',icon=icono).add_to(folium_map)   
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


def rd(a):
    return str(round(float(a),4))


"""
Menu principal
"""
def thread_cycle():
    while True:
        printMenu()
        inputs = input('Seleccione una opción para continuar\n')
        if int(inputs[0]) == 0:
            print("Cargando información de los archivos ....")
            cont = controller.init()
            controller.loadServices(cont, routefile,airportfile,cityfile)
            carga = prueba(cont)
            print('El total de aeropuertos cargados es: ' + str(carga[0]))
            print('El total de vertices cargados en el grafo dirigido es: ' + str(carga[1]))
            print('El número de rutas cargadas en el grafo dirigido es: ' + str(carga[2]))
            print('El primer y el último aeropuerto cargado al grafo dirigido es: ')
            x = PrettyTable()
            x.field_names = ['Nombre','Ciudad','Pais','IATA','Latitud','Longitud']
            x.add_row([salto(carga[6]['Name'],15),carga[6]['City'],carga[6]['Country'],carga[6]['IATA'],rd(carga[6]['Latitude']),rd(carga[6]['Longitude'])])
            x.add_row([salto(carga[7]['Name'],15),carga[7]['City'],carga[7]['Country'],carga[7]['IATA'],rd(carga[7]['Latitude']),rd(carga[7]['Longitude'])])
            print(x)
            print('El total de vertices cargados en el grafo no dirigido es: ' + str(carga[4]))
            print('El número de rutas cargadas en el grafo no dirigido es: ' + str(carga[5]))
            print('El primer aeropuerto y el último cargado al grafo dirigido es: ')
            print(x) 
            print('El número de ciudades cargadas es: ' + str(carga[3]))
            print('La primera y última ciudad cargada es: ') 
            y = PrettyTable()
            y.field_names = ['Nombre','Pais','Población','Latitud','Longitud']
            y.add_row([salto(carga[8]['city_ascii'],15),carga[8]['country'],carga[8]['population'],rd(carga[8]['lat']),rd(carga[8]['lng'])])
            y.add_row([salto(carga[9]['city_ascii'],15),carga[9]['country'],carga[9]['population'],rd(carga[9]['lat']),rd(carga[9]['lng'])])
            print(y)

        elif int(inputs[0]) == 1:
            print('Determinando aeropuerto asociado a mayor número de rutas... ')
            total = controller.maxinterconexion(cont)
            print('El maximo numero de rutas asociado a un aeropuerto es ' + str(total[0]))
            maxaero(total[1])
            print('Para visualizar el mapa con las observaciones siga el enlace que se genera a continuación: ')
            printmap(total[1])


        elif int(inputs[0]) == 2:
            aeropuertoinicial = input('Ingrese el primer aeropuerto (código IATA) : ').upper()
            aeropuertofinal = input('Ingrese el segundo aeropuerto (código IATA) : ').upper()
            print("Encontrando clústeres de tráfico aéreo... ")
            result = controller.encontrarClusteres(cont,aeropuertoinicial,aeropuertofinal)
            printClusteres(result)
            print("Número total de clústeres presentes en la red de transporte aéreo: " + str(result[0]))
            if result[1] == True:
                valor = " sí"
            else:
                valor = " no"
            print("El aeropuerto ", aeropuertoinicial," y ", aeropuertofinal, valor," están en el mismo clúster aereo.")
            print("Se generó el archivo HTML, puede verse en la carpeta Reto4-G05")
            
        elif int(inputs[0]) == 3:
            ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
            lciudades1 = controller.mget(cont['ciudades'],ciudadinicial)
            while lciudades1 == None:
                print('No se encontro la ciudad,verifique que esta bien escrito el nombre')
                ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
                lciudades1  = controller.mget(cont['ciudades'],ciudadinicial)
            if controller.ltsize(lciudades1['value']) == 1:
                print('Se encontro una coincidencia entre el nombre de las ciudades')
                citydatai = controller.ltgetElement(lciudades1['value'],1)
                x = PrettyTable()
                x.field_names = ['Ciudad','Pais','Latitud','Longitud']
                for ciudad in controller.iterador(lciudades1['value']):
                    renglon = [salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    x.add_row(renglon)
                print(x)
            else:
                print('Se encontraron ' + str(controller.ltsize(lciudades1['value'])) + ' coincidencias para la ciudad dada: ')
                x = PrettyTable()
                x.field_names = ['Opción','Ciudad','Pais','Latitud','Longitud']
                pos = 1 
                for ciudad in controller.iterador(lciudades1['value']):
                    renglon = [str(pos),salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    pos += 1 
                    x.add_row(renglon)
                print(x)
                selec = int(input('Ingrese la opción correspondiente a la ciudad: '))
                citydatai = controller.ltgetElement(lciudades1['value'],selec)
                
            ciudadfinal = input('Ingrese la ciudad de destino (código ascii) : ')
            lciudades2 = controller.mget(cont['ciudades'],ciudadfinal)
            while lciudades2 == None:
                print('No se encontro la ciudad,verifique que esta bien escrito el nombre')
                ciudadfinal= input('Ingrese la ciudad de destino (código ascii) : ')
                lciudades2  = controller.mget(cont['ciudades'],ciudadfinal)
            if controller.ltsize(lciudades2['value']) == 1:
                print('Se encontro una coincidencia entre el nombre de las ciudades')
                citydataf = controller.ltgetElement(lciudades2['value'],1)
                x = PrettyTable()
                x.field_names = ['Ciudad','Pais','Latitud','Longitud']
                for ciudad in controller.iterador(lciudades2['value']):
                    renglon = [salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    x.add_row(renglon)
                print(x)
            else:
                print('Se encontraron ' + str(controller.ltsize(lciudades2['value'])) + ' coincidencias para la ciudad dada: ')
                x = PrettyTable()
                x.field_names = ['Opción','Ciudad','Pais','Latitud','Longitud']
                pos = 1 
                for ciudad in controller.iterador(lciudades2['value']):
                    renglon = [str(pos),salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    pos += 1 
                    x.add_row(renglon)
                print(x)
                selec = int(input('Ingrese la opción correspondiente a la ciudad: '))
                citydataf = controller.ltgetElement(lciudades2['value'],selec)
            print('Determinando aeropuertos mas cercanos...') 
            aeropuertoinicial = controller.cityToairport(cont,citydatai)
            aeropuertodestino = controller.cityToairport(cont,citydataf)
            print('Aeropuertos mas cercanos encontrados...')
            print('Determinando la ruta mas corta... ')
            cont['paths'] = controller.rutasMin(cont['rutas'],aeropuertoinicial['IATA'])
            camino = controller.camino(cont['paths'],aeropuertodestino['IATA'])
            if camino is not None: 
                x = PrettyTable()
                x.field_names = ['Aeropuerto de salida','Aeropuerto de llegada','Distancia en km ']
                pathlen = stack.size(camino)
                print('El camino es de longitud: ' + str(pathlen))
                lista = controller.ltnewList() 
                conteo = 0 
                while (not stack.isEmpty(camino)):
                    stop = stack.pop(camino)
                    aeropuertoS = controller.mget(cont['aeropuerto'],stop['vertexA'])['value']
                    aeropuertoD = controller.mget(cont['aeropuerto'],stop['vertexB'])['value']
                    distancia = stop['weight']
                    x.add_row([aeropuertoS['Name'],aeropuertoD['Name'],distancia])
                    if conteo == 0:
                        controller.ltAddLast(lista,aeropuertoS) 
                    conteo +=1 
                    controller.ltAddLast(lista,aeropuertoD)
                print(x)
                printmap2(lista)
            else:
                print('No hay camino')



        elif int(inputs[0]) == 4:
            ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
            lciudades1 = controller.mget(cont['ciudades'],ciudadinicial)
            while lciudades1 == None:
                print('No se encontro la ciudad,verifique que esta bien escrito el nombre')
                ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
                lciudades1  = controller.mget(cont['ciudades'],ciudadinicial)
            if controller.ltsize(lciudades1['value']) == 1:
                print('Se encontro una coincidencia entre el nombre de las ciudades')
                citydatai = controller.ltgetElement(lciudades1['value'],1)
                x = PrettyTable()
                x.field_names = ['Ciudad','Pais','Latitud','Longitud']
                for ciudad in controller.iterador(lciudades1['value']):
                    renglon = [salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    x.add_row(renglon)
                print(x)
            else:
                print('Se encontraron ' + str(controller.ltsize(lciudades1['value'])) + ' coincidencias para la ciudad dada: ')
                x = PrettyTable()
                x.field_names = ['Opción','Ciudad','Pais','Latitud','Longitud']
                pos = 1 
                for ciudad in controller.iterador(lciudades1['value']):
                    renglon = [str(pos),salto(ciudad['city_ascii'],18),salto(ciudad['country'],18),salto(ciudad['lat'],18),salto(ciudad['lng'],18)]
                    pos += 1 
                    x.add_row(renglon)
                print(x)
                selec = int(input('Ingrese la opción correspondiente a la ciudad: '))
                citydatai = controller.ltgetElement(lciudades1['value'],selec)
            millas = int(input('Ingrese la cantidad de millas que tiene disponibles: '))
            result = controller.usarMillas(cont, citydatai, millas)
            print("Red de expansión mínima: ")
            printMillas(result)
        
        elif int(inputs[0]) == 5:
            iata = input('Ingrese el código IATA del aeropuerto: ')
            listav = controller.adyacencia(cont,iata)
            listadata = controller.ltnewList()
            for i in controller.iterador(listav):
                data = controller.mget(cont['aeropuerto'],i)['value']
                controller.ltAddLast(listadata,data)
            aerodata = controller.mget(cont['aeropuerto'],iata)['value']
            print('Analizando los aeropuertos afectados si se cierra el aeropuerto... ' + aerodata['Name'])
            print('El número de aeropuertos afectados es: ' + str(controller.ltsize(listav)))
            if controller.ltsize(listav) > 6:
                listavacia = controller.concatlist(controller.sublista(listav,1,3),controller.sublista(listav,controller.ltsize(listav)-2,3))
            else:
                listavacia = listav 
            x = PrettyTable()
            x.field_names = ['Nombre','Ciudad','Pais']
            for vertice in controller.iterador(listavacia):
                data = controller.mget(cont['aeropuerto'],vertice)['value']
                renglon = [data['Name'],data['City'],data['Country']]
                x.add_row(renglon)
            #x.sortby = 'Nombre'
            print(x)
            printmap3(listadata,data)


        elif int(inputs[0]) == 6:
            
            ciudadinicial = input('Ingrese la ciudad de origen (código ascii) : ')
            ciudadfinal = input('Ingrese la ciudad de destino (código ascii) : ')
            
            result = controller.servicioWebExterno(cont, ciudadinicial, ciudadfinal)



        else:
            sys.exit(0)
    sys.exit(0)



if __name__ == "__main__":
    ruta = "Data/AirportNearestRelevant_v1_Version_1.0_swagger_specification.json"
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=thread_cycle)
    thread.start()


