#--------------------------------------------------------------------------------------------------
#               Importar Librerias
#--------------------------------------------------------------------------------------------------


import mysql.connector
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import numpy as np
import imutils
import cv2
import sys
import ctypes
from shutil import rmtree
import datetime
import re
import serial
import time


def EjecutarCam():
	#Crear Conexión DB MySQL
	mydb = mysql.connector.connect(
	  host="b4ul0gc0bnq5osjqr6re-mysql.services.clever-cloud.com",
	  user="urtaijruysi98xkg",
	  password="iWdJvXY3ytgiOxM4ZmKD",
	  database="b4ul0gc0bnq5osjqr6re",
	  port="20549"
	)
	#Crear Cursor
	mycursor = mydb.cursor()

	#Crear Conexion DB FireBase 
	cred = credentials.Certificate("fireSDK.json")
	firebase_admin.initialize_app(cred, {
		'databaseURL' : 'https://internalsecurity-6ac0c.firebaseio.com/'
		}
	)

	dataPath = 'C:/Users/USER/Desktop/FacePython/Data' #Cambia a la ruta donde hayas almacenado Data
	imagePaths = os.listdir(dataPath)
	print('imagePaths=',imagePaths)

	face_recognizer = cv2.face.EigenFaceRecognizer_create()

	# Leyendo el modelo
	face_recognizer.read('modeloEigenFace.xml')

	#--------------------------------------------------------------------------------------------------
	#               Definir Camaras
	#--------------------------------------------------------------------------------------------------

	#cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)                                   ---  Webcam
	#cap = cv2.VideoCapture('http://user:password@IP:Puerto')                  ---  Conexion general cam IP
	#cap = cv2.VideoCapture('rtsp://admin:1234@192.168.1.4:8554/live')         ---  IP cam por rtsp
	#cap = cv2.VideoCapture('http://admin:1234@192.168.1.4:8081/video')        ---  IP cam por http 
	#cap = cv2.VideoCapture('http://root:admin@192.168.1.3/mjpg/video.mjpg')   ---  Camara Axis

	cap0   = cv2.VideoCapture('PyEntrada.mp4')
	cap1   = cv2.VideoCapture('PyBiblioteca.mp4')
	cap2   = cv2.VideoCapture('PyRegistro.mp4')
	cap3   = cv2.VideoCapture('PyBloqueE.mp4')
	cap4   = cv2.VideoCapture('PyDesvio.mp4')
	cap5   = cv2.VideoCapture('PyPlaza.mp4')
	cap6   = cv2.VideoCapture('PyAdministracion.mp4')
	cap7   = cv2.VideoCapture('PyPasilloGP7.mp4')
	cap8   = cv2.VideoCapture('PySalida.mp4')

	global P4Admisiones
	global P4Registro
	global NumeroVisitantes
	global PuertoCOM

	#--------------------------------------------------------------------------------------------------
	#               Definir Rutas
	#--------------------------------------------------------------------------------------------------

	P4Admisiones = ['Entrada', 'Biblioteca','Registro','BloqueE','DnPlaza','Admisiones','Pasillo G-P7','Salida']
	P4Registro   = ['Entrada', 'Biblioteca','Registro','BloqueE','DnPlaza','Pasillo Dn-P7','Salida']

	#--------------------------------------------------------------------------------------------------
	#               Definir Puerto Serial - Arduino
	#--------------------------------------------------------------------------------------------------

	PuertoCOM = 'COM5'
	mycursor.execute("SELECT count(ruta_id) FROM `visits`")
	myresult = mycursor.fetchall()
	NumeroVisitantes = myresult[0][0]

	faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

	while True:

		mycursor.execute("SELECT count(ruta_id) FROM `visits`")
		myresult = mycursor.fetchall()
		NewNumeroVisitantes = myresult[0][0]

		if NumeroVisitantes != NewNumeroVisitantes:
			#Borrar Carpeta Data si existe, esto es para crear otra carpeta Data con los visitantes que siguen dentro y eliminar los que estan fuera
			ctypes.windll.user32.MessageBoxW(0, "La carpeta Data no existe. Se procede a crear una", "Data does not exist", 1)
			if os.path.exists(dataPath):
				rmtree("Data")
			#Obtener Info de la DB
			mycursor = mydb.cursor()
			mycursor.execute("SELECT id, fullname, type_doc, document, images, ruta_id FROM `visits`WHERE status = 'In' ORDER BY created_at ASC")
			myresult = mycursor.fetchall()

			#--------------------------------------------------------------------------------------------------
			#               Creacion de Carpetas y Guardado de imagenes traidas de la DB
			#--------------------------------------------------------------------------------------------------

			#Contar las filas que se traen de la DB
			filas = len(myresult)
			#Crear Carpeta Data si no existe
			ruta = os.getcwd()
			dataPath = ruta + '/Data'
			if not os.path.exists(dataPath):
				#print('La carpeta Data no existe. Se procede a crear una')
				#ctypes.windll.user32.MessageBoxW(0, "La carpeta Data no existe. Se procede a crear una", "Data does not exist", 1)
				#print('Carpeta Data Creada: ',dataPath)
				os.makedirs(dataPath)
			#Crear Carpetas de visitantes si no existen
			i=0
			#ctypes.windll.user32.MessageBoxW(0, "Si la carpeta del visitante no existe se procede a crear una", "Create Visitor Files", 1)
			for x in range(filas):
				personPath = dataPath + '/' + myresult[i][3] + '+' + str(myresult[i][0]) + '+' + myresult[i][5]
				
				if not os.path.exists(personPath):
					#print('Carpeta creada: ',personPath)
					os.makedirs(personPath)
				i=i+1

			ImgSQL = "global"
			def write_file(data, filename,i):
			    with open(filename, 'wb') as f:
			        f.write(data)
			        ImgSQL = cv2.imread('rostro_SQL.jpg')
			        #cv2.imshow('ImgSQL', ImgSQL)
			        count=0
			        gray = cv2.cvtColor(ImgSQL, cv2.COLOR_BGR2GRAY)
			        AuximagenDB = ImgSQL.copy()
			        faces = faceClassif.detectMultiScale(gray,1.3,5)
			        personPath = dataPath + '/' + myresult[i][3] + '+' + str(myresult[i][0]) + '+' + myresult[i][5]
			        for (x,y,w,h) in faces:
			        	cv2.rectangle(ImgSQL, (x,y),(x+w,y+h),(0,255,0),2)
			        	rostro = AuximagenDB[y:y+h,x:x+w]
			        	rostro = cv2.resize(rostro,(150,150),interpolation=cv2.INTER_CUBIC)
			        	cv2.imwrite(personPath + '/rotro_{}.jpg'.format(count),rostro)
			        	#cv2.imshow('Rostro',rostro)
			        	count = count + 1
			        	#cv2.imshow('ImgSQL',ImgSQL)
				        #cv2.waitKey(0)
				        #cv2.destroyAllWindows()

			#Guardar Imagenes en las carpetas creadas

			faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
			i=0
			for x in range(filas):
				write_file(myresult[i][4], 'rostro_SQL.jpg',i)
				#imagenDB =  imutils.resize(ImgSQL, width=640)
				i=i+1


			#--------------------------------------------------------------------------------------------------
			#                        ENTRENANDO EL SISTEMA DE RECONOCIMIENTO
			#--------------------------------------------------------------------------------------------------


			peopleList = os.listdir(dataPath)
			#print('Lista de personas: ', peopleList)

			labels = []
			facesData = []
			label = 0

			for nameDir in peopleList:
				personPath = dataPath + '/' + nameDir
				#print('Leyendo las imágenes')

				for fileName in os.listdir(personPath):
					#print('Rostros: ', nameDir + '/' + fileName)
					labels.append(label)
					facesData.append(cv2.imread(personPath+'/'+fileName,0))
				label = label + 1

			# Métodos para entrenar el reconocedor
			face_recognizer = cv2.face.EigenFaceRecognizer_create()

			# Entrenando el reconocedor de rostros
			#ctypes.windll.user32.MessageBoxW(0, "Se procede a entrenar el modelo EigenFace", "Create EigenFace Model", 1)
			face_recognizer.train(facesData, np.array(labels))

			# Almacenando el modelo obtenido
			face_recognizer.write('modeloEigenFace.xml')
			#print("Modelo almacenado...")

			#--------------------------------------------------------------------------------------------------
			#                                      ARDUINO 
			#--------------------------------------------------------------------------------------------------

			# Habilitar puerto de conexión Arduino
			s = serial.Serial(PuertoCOM, 9600)
			# Esperar para que se inicialice
			time.sleep(2)  
			# Enviar al Arduino  
			s.write(b'9')

			NumeroVisitantes = NewNumeroVisitantes
			

		ret0,frame0 = cap0.read()
		ret1,frame1 = cap1.read()
		ret2,frame2 = cap2.read()
		ret3,frame3 = cap3.read()
		ret4,frame4 = cap4.read()
		ret5,frame5 = cap5.read()
		ret6,frame6 = cap6.read()
		ret7,frame7 = cap7.read()
		ret8,frame8 = cap8.read()

		#-----------------------------------------------------------------------
		#                            CAMARA DE ENTRADA         0
		#-----------------------------------------------------------------------

		if (ret0) :
			if ret0 == False: break
			frame0 = cv2.resize(frame0, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame0,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFacesq
				if result[1] < 5700:
					
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame0,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame0, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result0 = mycursor.fetchall()
					filas0 = len(result0)

					if filas0 == 0:

						ahora = datetime.datetime.now()
						fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement0 = "INSERT INTO FaceRec (document,destino) VALUES(%s,%s)"
						val0 = (PartsNameFolder[0],'Entrada')
						mycursor.execute(SQLStatement0,val0)
						mydb.commit()

						SQLStatement00 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						mycursor.execute(SQLStatement00,val00)
						mydb.commit()

						SQLStatement00 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						mycursor.execute(SQLStatement00,val00)
						mydb.commit()

						lugar = 'Entrada'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Entrada':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Entrada',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Entrada':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Entrada',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						
					elif result0[0][1] != 'Entrada':

						ahora = datetime.now()
						fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement0 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val0 = (PartsNameFolder[0],'Entrada',PartsNameFolder[0])
						mycursor.execute(SQLStatement0,val0)
						mydb.commit()

						SQLStatement00 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						mycursor.execute(SQLStatement00,val00)
						mydb.commit()

						SQLStatement00 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						mycursor.execute(SQLStatement00,val00)
						mydb.commit()

						lugar = 'Entrada'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Entrada':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Entrada',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Entrada', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Entrada':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Entrada',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()

					
				else:
					cv2.putText(frame0,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame0, (x,y),(x+w,y+h),(0,0,255),2)
			
			cv2.imshow('Entrada',frame0)
			cv2.moveWindow('Entrada',268,0)
			k = cv2.waitKey(1)
			if k == 27:
				break
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 0", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE BIBLIOTECA      1
		#-----------------------------------------------------------------------

		if (ret1) :
			if ret1 == False: break
			frame1 = cv2.resize(frame1, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame1,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame1,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame1, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Biblioteca':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Biblioteca',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Biblioteca', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Biblioteca', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Biblioteca'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Biblioteca', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Biblioteca':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Biblioteca',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Biblioteca', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Biblioteca':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Biblioteca',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						
				else:
					cv2.putText(frame1,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame1, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('Biblioteca',frame1)
			cv2.moveWindow('Biblioteca',634,0)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 1", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE REGISTRO        2
		#-----------------------------------------------------------------------

		if (ret2) :
			if ret2 == False: break
			frame2 = cv2.resize(frame2, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame2,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame2,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame2, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Registro':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Registro',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Registro', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Registro', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Registro'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Registro', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Registro':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Registro',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Registro', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Registro':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Registro',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						
				else:
					cv2.putText(frame2,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame2, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('Registro',frame2)
			cv2.moveWindow('Registro',1000,0)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 2", "Error", 1)
			break	

		#-----------------------------------------------------------------------
		#                            CAMARA DE BLOQUE E        3
		#-----------------------------------------------------------------------

		if (ret3) :
			if ret3 == False: break
			frame3 = cv2.resize(frame3, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame3,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame3,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame3, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Bloque E1':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Bloque E1',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Bloque E1', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Bloque E1', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Bloque E1'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Bloque E1', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      	if resultDesvio[0][1] != 'Bloque E1':

						        	ahora = datetime.datetime.now()
						        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
						        	val1 = (PartsNameFolder[0],'Bloque E1',fecha, PartsNameFolder[1],PartsNameFolder[0])
						        	mycursor.execute(SQLStatement1,val1)
						        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Bloque E1', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Bloque E1':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Bloque E1',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						
				else:
					cv2.putText(frame3,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame3, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('BloqueE',frame3)
			cv2.moveWindow('BloqueE',268,206)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 3", "Error", 1)
			break	

		#-----------------------------------------------------------------------
		#                            CAMARA DE GRAPHIQUE       4
		#-----------------------------------------------------------------------

		if (ret4) :
			if ret4 == False: break
			frame4 = cv2.resize(frame4, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame4,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame4,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame4, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Graphique':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Graphique',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Graphique', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Graphique', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Graphique'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Graphique', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Graphique':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Graphique',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Graphique', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Graphique':

						        		ahora = datetime.datetime.now()
						        		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						        		SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
						        		val1 = (PartsNameFolder[0],'Graphique',fecha, PartsNameFolder[1],PartsNameFolder[0])
						        		mycursor.execute(SQLStatement1,val1)
						        		mydb.commit()
						
				else:
					cv2.putText(frame4,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame4, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('Graphique',frame4)
			cv2.moveWindow('Graphique',634,206)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 4", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE DN PLAZA        5
		#-----------------------------------------------------------------------

		if (ret5) :
			if ret5 == False: break
			frame5 = cv2.resize(frame5, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame5, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame5,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame5,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame5, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Dn Plaza':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Dn Plaza',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Dn Plaza', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Dn Plaza', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Dn Plaza'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Dn Plaza', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Dn Plaza':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Dn Plaza',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Dn Plaza', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Dn Plaza':

						        		ahora = datetime.datetime.now()
						        		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						        		SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
						        		val1 = (PartsNameFolder[0],'Dn Plaza',fecha, PartsNameFolder[1],PartsNameFolder[0])
						        		mycursor.execute(SQLStatement1,val1)
						        		mydb.commit()
						
				else:
					cv2.putText(frame5,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame5, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('DnPlaza',frame5)
			cv2.moveWindow('DnPlaza',1000,206)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 5", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE ADMISIONES      6
		#-----------------------------------------------------------------------

		if (ret6) :
			if ret6 == False: break
			frame6 = cv2.resize(frame6, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame6, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame6,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame6,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame6, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Admisiones':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Admisiones',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Admisiones', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Admisiones', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Admisiones'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Admisiones', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Admisiones':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Admisiones',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()

						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Admisiones', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Admisiones':

						        		ahora = datetime.datetime.now()
						        		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						        		SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
						        		val1 = (PartsNameFolder[0],'Admisiones',fecha, PartsNameFolder[1],PartsNameFolder[0])
						        		mycursor.execute(SQLStatement1,val1)
						        		mydb.commit()
						
				else:
					cv2.putText(frame6,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame6, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('Admisiones',frame6)
			cv2.moveWindow('Admisiones',268,412)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 6", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE PASILLO G-P7    7
		#-----------------------------------------------------------------------

		if (ret7) :
			if ret7 == False: break
			frame7 = cv2.resize(frame7, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame7, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame7,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame7,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame7, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Pasillo G-P7':

						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Pasillo G-P7',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Pasillo G-P7', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Pasillo G-P7', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						#------------------------------------
						#             ALARMAS
						#------------------------------------

						lugar = 'Pasillo G-P7'
						#Se busca si ya se encuentrea en la base de datos de desvio el visitante
						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if PartsNameFolder[2] == 'P4-Admisiones':
						  	if lugar in P4Admisiones:
						    	#Verifico si no esta en la db
						    	if FilasDesvio == 0:
						      		pass

						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Pasillo G-P7', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

							      	if resultDesvio[0][1] != 'Pasillo G-P7':

							        	ahora = datetime.datetime.now()
							        	fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

							        	SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
							        	val1 = (PartsNameFolder[0],'Pasillo G-P7',fecha, PartsNameFolder[1],PartsNameFolder[0])
							        	mycursor.execute(SQLStatement1,val1)
							        	mydb.commit()
						      
						elif PartsNameFolder[2] == 'P4-Registro':
						  	if lugar in P4Registro:
						    	if FilasDesvio == 0:
						      		pass
						      
						    	#Si hay algo quito la alerta
						    	else:
						      		SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						      		val1 = (PartsNameFolder[0],PartsNameFolder[1])
						      		mycursor.execute(SQLStatement1,val1)
						      		mydb.commit()

						      		for key in fireKeys:
										fireDelete = fireRefKey.child(key)
										fireDelete.delete()
						  	else:
						    	# Si no se encuentra se hace un INSERT
						    	if FilasDesvio == 0:

						      		ahora = datetime.datetime.now()
						      		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						      		SQLStatement00 = "INSERT INTO Desvio (document,posicion,fecha,user_id) VALUES(%s,%s,%s,%s)"
						      		val00 = (PartsNameFolder[0],'Pasillo G-P7', fecha, PartsNameFolder[1])
						      		mycursor.execute(SQLStatement00,val00)
						      		mydb.commit()

						      		if lenfireKeys > 0:
										pass
										
									else:
										fireRefKey.push({ 'documento': PartsNameFolder[0] })

						    	#Si ya se encuentra almenos un desvio se hace un UPDATE
						    	else:

						      		if resultDesvio[0][1] != 'Pasillo G-P7':

						        		ahora = datetime.datetime.now()
						        		fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

						        		SQLStatement1 = "UPDATE Desvio SET document = %s , posicion = %s , fecha = %s , user_id = %s WHERE document = %s "
						        		val1 = (PartsNameFolder[0],'Pasillo G-P7',fecha, PartsNameFolder[1],PartsNameFolder[0])
						        		mycursor.execute(SQLStatement1,val1)
						        		mydb.commit()
						
				else:
					cv2.putText(frame7,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame7, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('PasilloG-P7',frame7)
			cv2.moveWindow('PasilloG-P7',634,412)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 7", "Error", 1)
			break

		#-----------------------------------------------------------------------
		#                            CAMARA DE SALIDA          8
		#-----------------------------------------------------------------------

		if (ret8) :
			if ret8 == False: break
			frame8 = cv2.resize(frame8, (366, 206), fx = 0, fy = 0,interpolation = cv2.INTER_CUBIC)
			gray = cv2.cvtColor(frame8, cv2.COLOR_BGR2GRAY)
			auxFrame = gray.copy()

			faces = faceClassif.detectMultiScale(gray,1.3,5)

			for (x,y,w,h) in faces:
				rostro = auxFrame[y:y+h,x:x+w]
				rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
				result = face_recognizer.predict(rostro)

				#Ver Grado de Fidelidad
				cv2.putText(frame8,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)
				
				# EigenFaces
				if result[1] < 5700:
					NameFolder = imagePaths[result[0]]
					PartsNameFolder = re.split(r'[+]', NameFolder)
					cv2.putText(frame8,'{}'.format(PartsNameFolder[0]),(x,y-25),2,1.1,(0,255,0),1,cv2.LINE_AA)
					cv2.rectangle(frame8, (x,y),(x+w,y+h),(0,255,0),2)

					
					#Se sube a la DB la ubicacion del visitante
					mycursor.execute("SELECT document, destino FROM FaceRec WHERE document = %s ", (PartsNameFolder[0],))
					result1 = mycursor.fetchall()
					filas1 = len(result1)
					
					if result1[0][1] != 'Salida':
						# delete from RealTimeData where date = current_date()
						ahora1 = datetime.now()
						fecha1 = ahora1.strftime("%Y-%m-%d %H:%M:%S")

						SQLStatement1 = "UPDATE FaceRec SET document = %s , destino = %s WHERE document = %s "
						val1 = (PartsNameFolder[0],'Salida',PartsNameFolder[0])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Traz (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Salida', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement11 = "INSERT INTO Historial (document,destino,fecha,user_id) VALUES(%s,%s,%s,%s)"
						val11 = (PartsNameFolder[0],'Salida', fecha1, PartsNameFolder[1])
						mycursor.execute(SQLStatement11,val11)
						mydb.commit()

						SQLStatement1 = "DELETE FROM FaceRec WHERE document = %s  "
						val1 = (PartsNameFolder[0],)
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement1 = "DELETE FROM Traz WHERE document = %s AND user_id = %s "
						val1 = (PartsNameFolder[0],PartsNameFolder[1])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						SQLStatement1 = "UPDATE visits SET status = %s WHERE document = %s AND id = %s"
						val1 = ('Out',PartsNameFolder[0],PartsNameFolder[1])
						mycursor.execute(SQLStatement1,val1)
						mydb.commit()

						mycursor.execute("SELECT document, posicion FROM Desvio WHERE document = %s ", (PartsNameFolder[0],))
						resultDesvio = mycursor.fetchall()
						FilasDesvio = len(resultDesvio)

						fireRefKey = db.reference('Desvio')
						fireKeys = fireRefKey.order_by_child('documento').equal_to(PartsNameFolder[0]).get()
						lenfireKeys = len(fireKeys)

						if FilasDesvio == 0:
							pass
						  
						#Si hay algo quito la alerta
						else:
							
						  	SQLStatement1 = "DELETE FROM Desvio WHERE document = %s AND user_id = %s "
						  	val1 = (PartsNameFolder[0],PartsNameFolder[1])
						  	mycursor.execute(SQLStatement1,val1)
						  	mydb.commit()

						  	for key in fireKeys:
								fireDelete = fireRefKey.child(key)
								fireDelete.delete()


						#--------------------------------------------------------------------------------------------------
						#                                      ARDUINO 
						#--------------------------------------------------------------------------------------------------

						# Habilitar puerto de conexión Arduino
						s = serial.Serial(PuertoCOM, 9600)
						# Esperar para que se inicialice
						time.sleep(2)  
						# Enviar al Arduino  
						s.write(b'9')

						
				else:
					cv2.putText(frame8,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
					cv2.rectangle(frame8, (x,y),(x+w,y+h),(0,0,255),2)

			cv2.imshow('Salida',frame8)
			cv2.moveWindow('Salida',1000,412)
			k = cv2.waitKey(1)
			if k == 27:
				break
				
		else:
			ctypes.windll.user32.MessageBoxW(0, "No hay video en la camara 8", "Error", 1)
			break

	cap0.release()
	cap0.release()
	cv2.destroyAllWindows()
	pass