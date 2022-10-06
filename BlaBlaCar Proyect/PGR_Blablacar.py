

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import numpy as np
#import pandas as pd
from datetime import datetime
from tqdm import tqdm
from pymongo import MongoClient
import requests as req
#from blablacarapi import BlaBlaCarApi
from datetime import date
from datetime import timedelta
import warnings
import pyshorteners
import re
warnings.filterwarnings('ignore')


cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_api=db.viajes_api_v3 # tabla filtrada api
colec_bruto=db.dicc_bruto # tabla bruto api
colec_solicitud=db.Solicitudes # tabla solicitudes


#print(cursor.list_database_names())

#print(cursor.list_database_names())
num_key = input("ingrese el numero de la key a usar")
#Api_key BlaBlaCar
with open(f'../Claves/blablacar_api_key{num_key}.txt') as archivo:
    bla_api_key = archivo.readline().rstrip('\n')
    
    
def datos_api (x):
    
    global contador 
    global id
    contador = 0
    
    
    if x['search_info']['count'] - x['search_info']['full_trip_count'] < 100:
        largo = x['search_info']['count'] - x['search_info']['full_trip_count']
    else:
        largo = 100

    for e in range(largo):
        try:
            id = x['trips'][e]['link'][x['trips'][e]['link'].index('id=')+3:x['trips'][e]['link'].index('-')]
            
            if len(list(colec_api.find({'ID': id}))) == 0: #comprobamos si el ID ya esta en BBDD (len 0 = a no existe en bbdd)

                fecha = x['trips'][e]['waypoints'][0]['date_time'][:10]
                hora = x['trips'][e]['waypoints'][0]['date_time'][11:16]
                origen = x['trips'][e]['waypoints'][0]['place']['city']
                destino = x['trips'][e]['waypoints'][1]['place']['city']
                precio = x['trips'][e]['price']['amount']
                distancia = x['trips'][e]['distance_in_meters']
                tiempo = x['trips'][e]['duration_in_seconds']

                provincia_origen = x['link'][x['link'].index('&fn=')+4:x['link'].index('&tn=')]
                provincia_destino = x['link'][x['link'].index('&tn=')+4:x['link'].index('&db=')]

                link = x['trips'][e]['link']
                
                shortener = pyshorteners.Shortener()
                short_link = shortener.dagd.short(link)
                

                # a veces no viene modelo, por lo que el largo seria diferente a 6
                if len(x['trips'][e]) == 6:
                    marca_vehiculo = x['trips'][e]['vehicle']['make']
                    modelo_vehiculo = x['trips'][e]['vehicle']['model']
                else:
                    marca_vehiculo = 'desconocido'
                    modelo_vehiculo = 'desconocido'

                columns = ['ID', 'FECHA', 'HORA', 'ORIGEN', 'PROVINCIA_ORIGEN', 'DESTINO', 'PROVINCIA_DESTINO', 'MARCA VEHICULO', 'MODELO_VEHICULO', 'DIASTANCIA', 'DURACIÓN', 'PRECIO', 'LINK', 'LINK_CORTO']
                datos = [id, fecha, hora, origen, provincia_origen, destino, provincia_destino, marca_vehiculo, modelo_vehiculo, distancia, tiempo, precio, link, short_link]
                data = dict(zip(columns, datos))
                colec_api.insert_one(data)
                contador += 1

            else:
                pass
            
        except:
            print(f'Error en la linea {e}')
            
       
    return #print(f'Subproceso finalizado. Importadas {contador} líneas')    


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

                #llamamos a la función de envio de wasap
                envio_mail (EmailSolicitud, NombreSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud)
                whatsapp(TelefonoSolicitud, NombreSolicitud, FechaSolicitud, HoraSolicitud, OrigenSolicitud, DestinoSolicitud, LINK, PrecioSolicitud)
                #actualizamos bbdd con Contactado SI por que ya hemos enviado el mail
                myquery = { "ID": IDSolicitud }
                newvalues = { "$set": { "CONTACTADO": "SI" } }

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


    pwk.sendwhatmsg_instantly( TelefonoSolicitud ,f'''Hola _{NombreSolicitud}_, \
tenemos buenas noticias, hemos encontrado un viaje que cumple con las condiciones que nos 
solicitaste.\n
*Origen*: {OrigenSolicitud}
*Destino*: {DestinoSolicitud}
*Fecha*: {FechaSolicitud}
*Hora*: {HoraSolicitud}
*Precio*: {PrecioSolicitud} €
Este es el *Link*: \n
{LINK}''' ,tab_close=True)
    #time.sleep(5)       
    #pyautogui.click(1050, 950)
    #k.press_and_release('enter')
 

    return print(f'Whatsapp enviado a \033[33m {NombreSolicitud} \x1b[0m' )
    
regex_dias = re.compile(r'^[0-9]$')
from datetime import date

today = date.today()

fecha_true = False
while fecha_true != True:
    sumadias = input("¿Quiere añadir algun dia mas a hoy? Vacio == hoy || 1 = mañana... : ")
    if sumadias == "":
        fecha = f'{today}'
        fecha_true = True
    elif re.fullmatch(regex_dias, sumadias):
        fecha = today + timedelta(int(sumadias))
        fecha_true = True
    else:
        continue
print(fecha)

url_to_mad = []
url_to_bar = []
url_to_sev = []
url_to_val = []
url_to_zar = []
url_to_mal = []
url_to_x = []

########### MADRID ###########

coordenadas_mad = '40.40841%2C-3.6876'

coordenadas_mad_to_x = ['43.37012,-8.39114', '38.99588,-1.85574', '38.34548,-0.4831', '40.65586,-4.69771', '38.87874,-6.97099', '41.38424,2.17634', '43.25721,-2.9239', '42.34113,-3.70419', '39.47316,-6.37121', '36.52171,-6.28414', '39.9864,-0.03688', '38.98651,-3.93131', '37.87954,-4.78032', '40.07653,-2.13152', '41.98186,2.82411', '37.17641,-3.60001', '40.63435,-3.1621', '37.26004,-6.9504', '42.14062,-0.40842', '37.76519,-3.79035', '42.59912,-5.56707', '41.61527,0.62061', '42.85058,-2.67275', '42.46644,-2.44565', '43.00912,-7.55817', '36.72034,-4.41997',  '36.83892,-2.46413','37.98436,-1.12854', '42.33654,-7.86368', '43.36232,-5.84372', '42.00783,-4.5346', '42.8141,-1.64515', '42.43381,-8.64799', '40.96736,-5.66538', '43.31717,-1.98191', '43.46297,-3.80474', '40.94987,-4.12524', '37.3862,-5.99251', '41.76327,-2.46624', '41.1191,1.25842', '40.34412,-1.10927', '39.85715,-4.02431', '39.47534,-0.37565', '41.65232,-4.72334', '41.49913,-5.75494','41.65645,-0.87928']

for e in coordenadas_mad_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_mad}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_mad.append(url_append)

    
########### BARCELONA ###########


coordenadas_bar = '41.38424,2.17634'
coordenadas_bar_to_x = ['43.37012,-8.39114', '38.34548,-0.4831', '40.65586,-4.69771', '42.34113,-3.70419', '36.52171,-6.28414', '38.98651,-3.93131', '40.07653,-2.13152', '37.17641,-3.60001', '37.26004,-6.9504', '37.76519,-3.79035', '41.61527,0.62061', '42.46644,-2.44565', '40.40841,-3.6876', '37.98436,-1.12854', '43.36232,-5.84372', '42.8141,-1.64515', '40.96736,-5.66538', '43.46297,-3.80474', '37.3862,-5.99251', '41.1191,1.25842', '39.85715,-4.02431', '41.65232,-4.72334', '41.65645,-0.87928', '38.99588,-1.85574', '36.83892,-2.46413', '38.87874,-6.97099', '43.25721,-2.9239', '39.47316,-6.37121', '39.9864,-0.03688', '37.87954,-4.78032', '41.98186,2.82411', '40.63435,-3.1621', '42.14062,-0.40842', '42.59912,-5.56707', '42.85058,-2.67275', '43.00912,-7.55817', '36.72034,-4.41997', '42.33654,-7.86368', '42.00783,-4.5346', '42.43381,-8.64799', '43.31717,-1.98191', '40.94987,-4.12524', '41.76327,-2.46624', '40.34412,-1.10927', '39.47534,-0.37565', '41.49913,-5.75494']

for e in coordenadas_bar_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_bar}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_bar.append(url_append)
    
    
########### VALENCIA ###########

coordenadas_val = '39.47534,-0.37565'
coordenadas_val_to_x = ['43.37012,-8.39114', '38.34548,-0.4831', '40.65586,-4.69771', '42.34113,-3.70419', '36.52171,-6.28414', '38.98651,-3.93131', '40.07653,-2.13152', '37.17641,-3.60001', '37.26004,-6.9504', '37.76519,-3.79035', '41.61527,0.62061', '42.46644,-2.44565', '40.40841,-3.6876', '37.98436,-1.12854', '43.36232,-5.84372', '42.8141,-1.64515', '40.96736,-5.66538', '43.46297,-3.80474', '37.3862,-5.99251', '41.1191,1.25842', '39.85715,-4.02431', '41.65232,-4.72334', '41.65645,-0.87928', '38.99588,-1.85574', '36.83892,-2.46413', '38.87874,-6.97099', '43.25721,-2.9239', '39.47316,-6.37121', '39.9864,-0.03688', '37.87954,-4.78032', '41.98186,2.82411', '40.63435,-3.1621', '42.14062,-0.40842', '42.59912,-5.56707', '42.85058,-2.67275', '43.00912,-7.55817', '36.72034,-4.41997', '42.33654,-7.86368', '42.00783,-4.5346', '42.43381,-8.64799', '43.31717,-1.98191', '40.94987,-4.12524', '41.76327,-2.46624', '40.34412,-1.10927', '41.38424,2.17634', '41.49913,-5.75494']

for e in coordenadas_val_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_val}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_val.append(url_append)
    
    
########### ZARAGOZA ###########

coordenadas_zar = '41.65645,-0.87928'
coordenadas_zar_to_x = ['43.37012,-8.39114', '38.34548,-0.4831', '40.65586,-4.69771', '42.34113,-3.70419', '36.52171,-6.28414', '38.98651,-3.93131', '40.07653,-2.13152', '37.17641,-3.60001', '37.26004,-6.9504', '37.76519,-3.79035', '41.61527,0.62061', '42.46644,-2.44565', '40.40841,-3.6876', '37.98436,-1.12854', '43.36232,-5.84372', '42.8141,-1.64515', '40.96736,-5.66538', '43.46297,-3.80474', '37.3862,-5.99251', '41.1191,1.25842', '39.85715,-4.02431', '41.65232,-4.72334', '39.47534,-0.37565', '38.99588,-1.85574', '36.83892,-2.46413', '38.87874,-6.97099', '43.25721,-2.9239', '39.47316,-6.37121', '39.9864,-0.03688', '37.87954,-4.78032', '41.98186,2.82411', '40.63435,-3.1621', '42.14062,-0.40842', '42.59912,-5.56707', '42.85058,-2.67275', '43.00912,-7.55817', '36.72034,-4.41997', '42.33654,-7.86368', '42.00783,-4.5346', '42.43381,-8.64799', '43.31717,-1.98191', '40.94987,-4.12524', '41.76327,-2.46624', '40.34412,-1.10927', '41.38424,2.17634', '41.49913,-5.75494']

for e in coordenadas_zar_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_zar}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_zar.append(url_append)


########### MALAGA ###########

coordenadas_mal = '36.72034,-4.41997'
coordenadas_mal_to_x = ['43.37012,-8.39114', '38.34548,-0.4831', '40.65586,-4.69771', '42.34113,-3.70419', '36.52171,-6.28414', '38.98651,-3.93131', '40.07653,-2.13152', '37.17641,-3.60001', '37.26004,-6.9504', '37.76519,-3.79035', '41.61527,0.62061', '42.46644,-2.44565', '40.40841,-3.6876', '37.98436,-1.12854', '43.36232,-5.84372', '42.8141,-1.64515', '40.96736,-5.66538', '43.46297,-3.80474', '37.3862,-5.99251', '41.1191,1.25842', '39.85715,-4.02431', '41.65232,-4.72334', '39.47534,-0.37565', '38.99588,-1.85574', '36.83892,-2.46413', '38.87874,-6.97099', '43.25721,-2.9239', '39.47316,-6.37121', '39.9864,-0.03688', '37.87954,-4.78032', '41.98186,2.82411', '40.63435,-3.1621', '42.14062,-0.40842', '42.59912,-5.56707', '42.85058,-2.67275', '43.00912,-7.55817', '41.65645,-0.87928', '42.33654,-7.86368', '42.00783,-4.5346', '42.43381,-8.64799', '43.31717,-1.98191', '40.94987,-4.12524', '41.76327,-2.46624', '40.34412,-1.10927', '41.38424,2.17634', '41.49913,-5.75494']

for e in coordenadas_mal_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_mal}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_mal.append(url_append)


########### SEVILLA ###########

coordenadas_sev = '37.3862,-5.99251'
#coordenadas_sev_to_x = ['40.40841%2C-3.6876']
coordenadas_sev_to_x = ['43.37012,-8.39114', '38.34548,-0.4831', '40.65586,-4.69771', '42.34113,-3.70419', '36.52171,-6.28414', '38.98651,-3.93131', '40.07653,-2.13152', '37.17641,-3.60001', '37.26004,-6.9504', '37.76519,-3.79035', '41.61527,0.62061', '42.46644,-2.44565', '40.40841,-3.6876', '37.98436,-1.12854', '43.36232,-5.84372', '42.8141,-1.64515', '40.96736,-5.66538', '43.46297,-3.80474', '36.72034,-4.41997', '41.1191,1.25842', '39.85715,-4.02431', '41.65232,-4.72334', '39.47534,-0.37565', '38.99588,-1.85574', '36.83892,-2.46413', '38.87874,-6.97099', '43.25721,-2.9239', '39.47316,-6.37121', '39.9864,-0.03688', '37.87954,-4.78032', '41.98186,2.82411', '40.63435,-3.1621', '42.14062,-0.40842', '42.59912,-5.56707', '42.85058,-2.67275', '43.00912,-7.55817', '41.65645,-0.87928', '42.33654,-7.86368', '42.00783,-4.5346', '42.43381,-8.64799', '43.31717,-1.98191', '40.94987,-4.12524', '41.76327,-2.46624', '40.34412,-1.10927', '41.38424,2.17634', '41.49913,-5.75494']

for e in coordenadas_sev_to_x:
    url_append = f'https://public-api.blablacar.com/api/v3/trips?key={bla_api_key}&from_coordinate={coordenadas_sev}&from_country=ES&to_coordinate={e}&to_country=ES&locale=es-ES&currency=EUR&start_date_local={fecha}T00%3A00%3A00&count=100'
    url_to_sev.append(url_append)
    
#len(url_to_x)


########################

''' punto importante. gasta creditos de la api_key'''

url_general_to_x = [
                   url_to_mad,
                   url_to_bar,
                   url_to_val,
                   url_to_sev,
                   url_to_zar,
                   url_to_mal
                   ]

list_general_x = []
total = 0

for g in url_general_to_x:
    for e in tqdm(g):
        json = req.get(e).json()
        datos_api(json) #pasamos por la función
        #colec_bruto.insert_one(json) #insertamos el json en tabla bruto
        total += contador

#print(json)
print(f"FIN. Total lineas exportadas: {total}")

#notificaciones() #llamamos a función de notificaciones
input("ingrese cualquier tecla para finalizar")
