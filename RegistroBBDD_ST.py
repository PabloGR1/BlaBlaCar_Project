import streamlit as st
import pymongo
from pymongo import MongoClient
cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3

nombre = st.text_input('Inserte su nombre: ')

if nombre:
  origen = st.text_input('Inserte la provincia de origen: ')
