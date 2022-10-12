import streamlit as st
from datetime import datetime
import pymongo

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Declare API version "1" for MongoClient "client"
server_api = ServerApi('1')
client = MongoClient(server_api=server_api)

client = pymongo.MongoClient("mongodb+srv://<username>:<password>@cluster0.oxuoatg.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.BlaBlaCar
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3




nombre = st.text_input('Inserte su nombre: ')
nombre = nombre.title()

if nombre:
  origen = st.text_input('Inserte la provincia de origen: ')
  origen = origen.capitalize()

id = datetime.today().strftime('%Y%m%d%H%M%S')
#destino = destino.capitalize()
#precio = str(precio)
#email = email.lower()

#telefono = str('+34') + str(telefono)

if st.button('Registrar'):
  columns = ['ID', 'NOMBRE', 'ORIGEN']
  datos = [id, nombre, origen]
  data = dict(zip(columns, datos))
  colec_solicitud.insert_one(data);
  st.write('Registrado')
  
else:
    st.write('No Registrado')


