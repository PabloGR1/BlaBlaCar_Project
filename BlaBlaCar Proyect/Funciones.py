import pandas as pd
import datetime as datetime
from datetime import datetime
from datetime import date
from tqdm import tqdm
from pymongo import MongoClient
import requests as req
from datetime import timedelta
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

import warnings
warnings.filterwarnings('ignore')


cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3

regex_mail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
regex_hora = re.compile(r'([01]?[0-9]|2[0-3]):[0-5][0-9]$')
regex_fecha = re.compile(r'(^20[0-2][0-9]-((0[1-9])|(1[0-2]))-([0-2][1-9]|3[0-1]))$')
regex_precio = re.compile(r'^[0-9][0-9]\.[0-9][0-9]$')
regex_telefono = re.compile(r'^(6|7)([0-9]){8}$')

def tulink (origen, destino, fecha, hora, hora2, precio):
    
    
    LINK2 = list(colec_api.find({'$and': [{'PROVINCIA_ORIGEN': origen}, # filtros que usamos
                               {'PROVINCIA_DESTINO': destino},
                               {'FECHA': fecha},
                               {'HORA' : {'$gte': (hora)}},
                               {'HORA' : {'$lte': (hora2)}},
                               {'PRECIO' : {'$lte': (precio)}}]},

                                {'LINK'}).sort('PRECIO', 1))   #columas que queremos mostrar y ordenado por precio
    
    global lst_link
    lst_link = []
    
    for i in range(len(LINK2)):
        lst_link.append(LINK2[i]['LINK'])
        
    return (lst_link)
    
def notificaciones():
    global LINK
    global bbdd
    
    # Traemos DDBB solicitudes con Contactado = NO
    bbdd = pd.DataFrame(list(colec_solicitud.find({'CONTACTADO': 'NO'})))

    # bucle para recorrer todas filas de la bbdd de clientes
    for i in range(len(bbdd)):
        NombreSolicitud = (bbdd.NOMBRE)[i]
        FechaSolicitud = (bbdd.FECHA)[i]
        HoraSolicitud = (bbdd.HORA)[i] #hora minima viaje
        Hora2Solicitud = (bbdd.HORA2)[i] #hora maxima viaje
        OrigenSolicitud = (bbdd.ORIGEN)[i]
        DestinoSolicitud = (bbdd.DESTINO)[i]
        PrecioSolicitud = (bbdd.PRECIO)[i]
        IDSolicitud = (bbdd.ID)[i]
        EmailSolicitud = (bbdd.EMAIL)[i]
        TelefonoSolicitud = (bbdd.TELEFONO)[i]

        # si el registro no tiene viaje en bbdd viajes, salta al except
        try:
            
            
            LINK = tulink (OrigenSolicitud, DestinoSolicitud, FechaSolicitud, HoraSolicitud, Hora2Solicitud,  PrecioSolicitud)[0] # 0 es para traer solo el primer link encontrado
                   
            if len(LINK) != 0:
                print(f'''Hola {NombreSolicitud}, este es tu link:\n{LINK}''')

                #llamamos a la función de envio de mail
                envio_mail (EmailSolicitud, NombreSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud)
                
                whatsapp(TelefonoSolicitud, NombreSolicitud, FechaSolicitud, HoraSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud)
                #actualizamos bbdd con Contactado SI por que ya hemos enviado el mail
                myquery = { "ID": IDSolicitud }
                newvalues = { "$set": { "CONTACTADO": "NO" } }

                colec_solicitud.update_one(myquery, newvalues)         

            else:
                pass

        except:
            continue

    bbddpdts = pd.DataFrame(list(colec_solicitud.find({'CONTACTADO': 'NO'})))
       
    return print(f'Clientes pendientes de contacto: {len(bbddpdts)}')
    
def whatsapp(TelefonoSolicitud, NombreSolicitud, FechaSolicitud, HoraSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud):
    import pywhatkit as pwk
    import time
    from selenium import webdriver 
    import pyautogui
    import keyboard as k
    from selenium import webdriver
    import pyautogui, webbrowser
    from time import sleep


    pwk.sendwhats_image( TelefonoSolicitud ,"../BlaBlaCar Proyect/BlaBlaPablo.jpg", f'''Hola _{NombreSolicitud}_, \
tenemos buenas noticias, hemos encontrado un viaje que cumple con los criterios que nos 
indicaste.\n
    *Origen*: {OrigenSolicitud}
    *Destino*: {DestinoSolicitud}
    *Fecha*: {FechaSolicitud}
    *Hora*: {HoraSolicitud}
    *Precio*: {PrecioSolicitud}
    Este es el *Link*: \n
    {LINK}''')

    pyautogui.press("enter")
    sleep(3)
    pyautogui.hotkey('ctrlleft', 'w')
    sleep(3)
    pyautogui.press("enter")
 

    return print(f'Whatsapp enviado a \033[33m {NombreSolicitud} \x1b[0m' )
    
def envio_mail (EmailSolicitud, NombreSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud):

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    
    with open('../Claves/gmail_key.txt') as archivo:
        gmail_key = archivo.readline().rstrip('\n')

    # configuración conexión GMAIL
    smtp_address = 'smtp.gmail.com'
    smtp_port = '465'

    # información de la cuenta de mail
    email_address = 'pavotuenlace@gmail.com'
    email_password = gmail_key

    # cuenta de destino
    email_receiver = EmailSolicitud

    # on crée un e-mail
    message = MIMEMultipart(f'{NombreSolicitud} este es tu link de BlaBlaCar')
    # on ajoute un sujet
    message["Subject"] = f"[BlaBlaCar] Link {OrigenSolicitud}  a {DestinoSolicitud}"
    # un émetteur
    message["From"] = 'Alegre aqui tienes tu enlace a cuchillo'
    # un destinataire
    message["To"] = email_receiver

    # on crée un texte et sa version HTML
    texte = ''

    html = f'''
    <html>
    <body>
    <h1>BlaBlaPablo</h1>
    <b>Hola {NombreSolicitud}:</b>
    <b>Tenemos buenas noticias, hemos encontrado un viaje, con las condiciones que nos indicaste</b>
    <br>
    <b>Viaje de {OrigenSolicitud} a {DestinoSolicitud}, con un precio inferior a {PrecioSolicitud} &euro;:</b>
    <br>
    <b>Link: {LINK} </b>
    <br>
    <b>Gracias por usar nuestro servicio</b>
    <br>

    </body>
    </html>
    '''

    # creamos dos elementos MIMEText
    texte_mime = MIMEText(texte, 'plain')
    html_mime = MIMEText(html, 'html')

    # adjuntamos estos dos elementos
    message.attach(texte_mime)
    message.attach(html_mime)


    # creamos la conexión
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
      # connexion completada
        server.login(email_address, email_password)
      # envio de mail correcto
        server.sendmail(email_address, email_receiver, message.as_string())
              
    return print(f'Email enviado correctamente a {NombreSolicitud}')

def Registro_BBDD():

    id = datetime.today().strftime('%Y%m%d%H%M%S')

    nombre = input("Ingrese su \033[91m NOMBRE \x1b[0m : ")

    fecha_true = False
    while fecha_true != True:
        fecha = input("Ingrese la \033[91m FECHA \x1b[0m que desea su viaje |formato (aaaa-mm-dd)|: ")
        if re.fullmatch(regex_fecha, fecha):
            fecha_true = True
        else:
            continue

    hora_true = False
    while hora_true != True:
        hora = input("Ingrese la \033[91m HORA salida minima \x1b[0m que desea de su viaje |formato (hh:mm)|: ")  
        if re.fullmatch(regex_hora, hora):
            hora_true = True
        else:
            continue

    hora2_true = False
    while hora2_true != True:
        hora2 = input("Ingrese la \033[91m HORA salida maxima \x1b[0m que desea su viaje |formato (hh:mm)|: ")  
        if re.fullmatch(regex_hora, hora2):
            hora2_true = True
        else:
            continue

    origen = input("Ingrese la \033[91m provincia de ORIGEN \x1b[0m : ")
    destino = input("Ingrese la \033[91m provincia de DESTINO \x1b[0m : ")

    precio_true = False
    while precio_true != True:
        precio = input("Ingrese el \033[91m precio maximo \x1b[0m de su viaje : |formato (XX.XX)|: ")
        if re.fullmatch(regex_precio, precio):
            precio_true = True
        else:
            continue


    email_true = False
    while email_true != True:    
        email = input("Ingrese su \033[91m correo electronico \x1b[0m : ") 
        if re.fullmatch(regex_mail, email):
            email_true = True
        elif email == "":
            email_true = True
        else:
            continue    


    telefono_true = False
    while telefono_true != True:
        telefono = input("Ingrese su \033[91m numero de telefono movil \x1b[0m : ")
        if re.fullmatch(regex_telefono, telefono):
            telefono_true = True
        elif telefono == "":
            telefono_true = True
        else:
            continue 

    origen = origen.capitalize()
    destino = destino.capitalize()
    precio = str(precio)
    email = email.lower()
    nombre = nombre.title()
    telefono = str('+34') + str(telefono)

    columns = ['ID', 'NOMBRE', 'FECHA', 'HORA', 'HORA2', 'ORIGEN', 'DESTINO', 'PRECIO', 'EMAIL', 'CONTACTADO', 'TELEFONO']
    datos = [id, nombre, fecha, hora, hora2, origen, destino, precio, email, 'NO', telefono]
    data = dict(zip(columns, datos))
    colec_solicitud.insert_one(data);

    return print(f'Estupendo \033[33m {nombre} \x1b[0m , hemos registrado tu viaje a \033[33m {destino} \x1b[0m')