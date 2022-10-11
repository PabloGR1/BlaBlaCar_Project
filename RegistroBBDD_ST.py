import streamlit as st
from datetime import datetime
import pymongo
from pymongo import MongoClient
cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3

nombre = st.text_input('Inserte su nombre: ')

if nombre:
  origen = st.text_input('Inserte la provincia de origen: ')

id = datetime.today().strftime('%Y%m%d%H%M%S')
origen = origen.capitalize()
destino = destino.capitalize()
precio = str(precio)
email = email.lower()
nombre = nombre.title()
telefono = str('+34') + str(telefono)

if st.button('Registrar'):
  columns = ['ID', 'NOMBRE', 'ORIGEN']
  datos = [id, nombre, origen]
  data = dict(zip(columns, datos))
  colec_solicitud.insert_one(data);
  st.write('Registrado')
  
else:
    st.write('No Registrado')


