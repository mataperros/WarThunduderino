# -*- coding: utf-8 -*- #####################################################
# Programa para exreaer informacion sobre indicadores de estado y vuelo	 	#
# del juego War Thunder a travez del mapa online que este proporciona y	 	#
# enviarlos posteriormente a una tarjeta Arduino/genuino					#
#																		  	#
# Autor: Jesus David Salazar Garcia. Aka: El_Mataperros					 	#
# 03 de Junio de 2017.													  	#
#																		  	#
# Notas: *Ago esto pensando en aviones caza.								#
#		 *Auno NO SE IMPLEMENTA EL ENVIO DE DATOS HACIA ARDUINO.			#
#		 *Probado en windows, la version de WarThunder para linux al		#
#		  parecer no exporta los datos de "indicators".					  	#
#		 *El parametro "efficiency" que se extrae de se elimina, se espera  #
#		  en una futura actualizacion recuperarlo.							#
#																		  	#
#############################################################################

#############################################################################
#	Constantes																#
T = True	# No es necesario tocar esto.									#
F = False   # No es necesario tocar esto.									#
#############################################################################

#############################################################################
# Seleccion de datos a enviar												#
# Poner en T en los elementos que se desee enviar hacia Arduino/Genuino		#
# La ID corresponde al identificador con el que se enviara				 	#
#############################################################################
#INDICADOR		#¿MOSTRAR? 	#ID   #SE EXTRAE DE:	#########################
gear_position	  = T	  	# (A)  /state									#
IAS			 	  = T	  	# (B)  /state									#
TAS			 	  = F	  	# (C)  /state									#
rpm			 	  = F	  	# (D)  /state									#
power_hp		  = F	  	# (E)  /state									#
name_aircraft     = T	  	# (F)  /indicators								#
altitude_hour     = T	  	# (G)  /indicators								#
altitude_min	  = F	  	# (H)  /indicators								#
turn			  = F	  	# (I)  /indicators								#
bank			  = F	  	# (J)  /indicators								#
compass		 	  = F	  	# (K)  /indicators								#
oil_temp		  = T	  	# (L)  /state									#
water_temp	  	  = T	  	# (M)  /state									#
fuel			  = T	  	# (N)  /indicators								#
gears_lamp	  	  = F	  	# (O)  /indicators								#
flaps_position	  =	F		# (P)  /state									#
throttle		  =	F		# (Q)  /state									#
manifoldpressure  = F		# (R)  /state									#
pitch			  = F		# (S)  /state									#
thrust			  = F		# (T)  /state									#
compressorstage	  = F		# (U)  /state									#
#############################################################################

# Lista de etiquetas de datos
a_enviar = [
	["gear",				gear_position,  	"A"],
	["IAS",				 	IAS,				"B"],
	["TAS",				 	TAS,				"D"],
	["RPM1",				rpm,				"C"],
	["power1",			  	power_hp,			"E"],
	["type",				name_aircraft,		"F"],
	["altitude_hour",	   	altitude_hour,		"G"],
	["altitude_min",		altitude_min,		"H"],
	["turn",				turn,				"I"],
	["bank",				bank,				"J"],
	["compass",			 	compass,			"K"],
	["oiltemp1",			oil_temp,			"L"],
	["watertemp1",			water_temp,			"M"],
	["fuel1",			   	fuel,				"N"],
	["gears_lamp",		  	gears_lamp,			"O"],
	["flaps",		  		flaps_position, 	"P"],
	["throttle1",	  		throttle, 			"Q"],
	["manifoldpressure1",	manifoldpressure,   "R"],
	["pitch1",				pitch,				"S"],
	["thrust1",				thrust,				"T"],
	["compressorstage1",	compressorstage,	"U"]
	# NOTA: NO AÑADIR EL IDENTIFACADOR efficiency	#
	#		 este se pierde al tratar los datos		# 
	]

# Las librerias
import requests
import unicodedata
import time
import serial
import os

# Strings con las url's de los datos
state = "http://127.0.0.1:8111/state"
indicators = "http://127.0.0.1:8111/indicators"

# Bucle
while True:
	# Limpiado la pantallita, -_--DEPURACION--_-
	os.system('cls')
	
	# Extrallendo datos de las url's y concatenandolos
	req = requests.get(state)
	state_txt = req.text
	req = requests.get(indicators)
	Indicators_txt = req.text
	data_txt = state_txt + Indicators_txt


	# Convirtiendo de unicode a string utf-8.
	datosSTR = data_txt.encode("utf-8")

	# Eliminando Caracteres innecesarios antes de crear la lista.
	datosSTR = datosSTR.replace("{","")
	datosSTR = datosSTR.replace("}","")
	datosSTR = datosSTR.replace("\"","")
	datosSTR = datosSTR.replace(" ","")
	datosSTR = datosSTR.replace("\n","")
	datosSTR = datosSTR.replace(",%", "")
	datosSTR = datosSTR.replace(",km/h", "")
	datosSTR = datosSTR.replace(",hp", "")
	datosSTR = datosSTR.replace(",kgs", "")
	datosSTR = datosSTR.replace(",deg", "")
	datosSTR = datosSTR.replace(",C", "")
	datosSTR = datosSTR.replace(",atm", "")
	datosSTR = datosSTR.replace("efficiency1:", "")
	
	# Creacion de la lista tomando como separador la coma.
	datosSTR = datosSTR.split(",")
	# Averiguando la cantidad de datos en la lista para crear sublistas
	no_datos = len(datosSTR)
	# Ciclo para separar los indicadores.
	indicadores = [] # Lista para guardar los indicadores ya separados [nombre, valor]
	
	for i in range(0, no_datos):
		indicadores.append(datosSTR[i].split(":"))

	# Corroborando que la partida este iniciada
	
	for s in range(0, len(indicadores)):
		if "false" in indicadores[s]:
			status = True
		else:
			status = False

	# Dependiendo del estado se envia la señal de partida 
	# no iniciada o se procesan los datos
	arduino_TX = [] # Lista donde se almacenan los datos para arduino
	if status:
		arduino_TX = ['Z']
	else:
		
		for b in range(0, len(a_enviar)):
			# ¿Esta activado el indicador?
			if True in a_enviar[b]:
				
				for a in range(0, no_datos):
					# ¿Esta el indicador en la lista?
					if a_enviar[b][0] in indicadores[a]:
						# Salir del ciclo para conservar el valor de a que es el index del dato
						break
				# Buscamos el valor en datosSTR y el codigo en a_enviar utilizando el index a.
				temporal = [a_enviar[b][2], indicadores[a][1]]
				arduino_TX.append(temporal)
	# Aqui podemos trabajar la lista ya con el formato [[codigo_x, valor_x], [codigo_y, valor_y], ...., [codigo_n, valor_n].
	# Listo para enviarlo hacia arduino usando pyserial
	print arduino_TX
		
	time.sleep(.1)
