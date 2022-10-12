import streamlit as st
from datetime import datetime
import pymongo

from pymongo import MongoClient
cursor=MongoClient('mongodb+srv://PGR:PGR123@cluster0.oxuoatg.mongodb.net/?retryWrites=true&w=majority'')
db=cursor.BlaBlaCar # bbdd
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


