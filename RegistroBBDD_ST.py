import streamlit as st
import pymongo
from pymongo import MongoClient
cursor=MongoClient('mongodb://localhost:27017')
db=cursor.BlaBlaCar # bbdd
colec_solicitud=db.Solicitudes # tabla solicitudes
colec_api=db.viajes_api_v3

st.text_input('prueba')

import os

os.system("pip3 install pymongo")
import pymongo

st.text("This is my first Mongo")
