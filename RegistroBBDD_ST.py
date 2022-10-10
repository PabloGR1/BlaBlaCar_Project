import streamlit as st
#from pymongo import MongoClient
from datetime import datetime

cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3


st.set_page_config(
    page_title="Final project Ironhack",
    page_icon="🚀",
    layout="wide")

st.title('Solicitud de viaje')

nombre = st.text_input('Inserte su nombre: ')

if nombre:
    telefono = st.text_input('Inserte su telefono: ', type= "password")
    
    if telefono:
        Origen = st.text_input('Inserte el origen de su viaje: ')
    
    
       
else:
    pass


origen = origen.capitalize()
destino = destino.capitalize()
precio = str(precio)
email = email.lower()
nombre = nombre.title()
telefono = str('+34') + str(telefono)

id = datetime.today().strftime('%Y%m%d%H%M%S')

columns = ['ID', 'NOMBRE', 'TELEFONO', 'ORIGEN']
datos = [id, nombre, telefono, origen]
data = dict(zip(columns, datos))
colec_solicitud.insert_one(data);


