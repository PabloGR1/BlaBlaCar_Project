#presentation

import streamlit as st
import pymongo

import numpy as np
import pandas as pd
import webbrowser
import json
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image

import matplotlib.pyplot as plt
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

import warnings
warnings.filterwarnings('ignore')


st.set_page_config(
    page_title="Final project Ironhack",
    page_icon="🚀",
    layout="wide"
)
image=Image.open('1080x360.jfif')

st.sidebar.header('Miguel Mota Cava')
st.sidebar.write('Bootcamp de Data')



pes = ['pestaña1', 'pestaña2', 'pestaña3', 'pestaña4']

pes = st.tabs(['Player search','Player comparation', 'Player prediction', 'Final'])

with pes[0]:
    st.title('Fifa 23  -  players search')

    with open('databaseplayers.json') as json_file: 
        data = json.load(json_file)

    dt1 = pd.DataFrame(data)
    dt1['sho'] = dt1['sho'].astype('int16')
    dt1['pas'] = dt1['pas'].astype('int16')
    dt1['pac'] = dt1['pac'].astype('int16')
    dt1['dri'] = dt1['dri'].astype('int16')
    dt1['def'] = dt1['def'].astype('int16')
    dt1['phy'] = dt1['phy'].astype('int16')
    
    jug = [str(dt1.names[i])+' '+str(dt1.version[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
    jug2 = [str(dt1.names[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
    dt1['jug']=jug
    dt1['jug2']=jug2
    
    player_filter =  st.selectbox('Select a player', pd.unique(dt1['names']))

    st.empty()

    dt1 =dt1[dt1['names']==player_filter]
        
    jug = [str(dt1.names[i])+' '+str(dt1.version[i])+' '+str(dt1.med[i]) for i in (list(dt1.names.index))]

    jug = st.tabs([str(jug[i]) for i in range(len(list(dt1.names.index)))])
        
    client = pymongo.MongoClient("mongodb+srv://miguelmotacava:Mmcmmc164@proyectofifa.qbief4y.mongodb.net/test")
    db = client.fifa23
    price_df = pd.json_normalize(list(db.price_players3.find({'names':player_filter})))
    price_df = price_df.drop(['_id'], axis =1)
    
    
    for j,i in  enumerate(list(dt1[dt1['names']==player_filter].index)):
        
        client = pymongo.MongoClient("mongodb+srv://miguelmotacava:Mmcmmc164@proyectofifa.qbief4y.mongodb.net/test")
        db = client.fifa23
        price_df = pd.json_normalize(list(db.price_players3.find({'names':player_filter})))
        price_df = price_df.drop(['_id'], axis =1)
        price_df = price_df[price_df.med==int(dt1.med[i])] 
        
        
        
        with jug[j]:
            c0 = st.container()
            c1, c2, c3, c4, c5 = st.columns(5)
            e0 =st.container()
            fig_col1, fig_col2 = st.columns(2)
            e1 =st.container()
            col1 = st.container()
            e2 =st.container()
            cc1 = st.container()
            
            with c0:
                st.header('Player')
                
            c1.metric(
                       label="Nombre",
                       value=dt1.names[i]
                      )

            with c2:
                st.image(dt1.face_url[i], width = 72)

            with c3:
                st.image(dt1.flags_url[i], width = 110)

            with c4:
                st.image(dt1.club_url[i], width = 68)
                
            c5.metric(
                       label="Precio",
                       value=(list(price_df.price)[-1])
                      )
            
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            st.write(' ')
            
            with e0:
                st.write(' ')
                
                
            with fig_col1:
                st.header('Radar')
                fig = radar(str(dt1.jug[i]))
                st.write(fig)
                
                
            with e1:
                st.write(' ')
            
            
            with fig_col2:
                st.header('Statistics')
                dtx = dt1[dt1.jug==dt1.jug[i]]
                fig2 = px.bar(data_frame=dtx, 
                              x='names', 
                              y=[dtx.pac, dtx.sho, dtx.pas, dtx.dri, dtx['def'], dtx.phy], 
                              barmode = 'group', 
                              title=f'Estadísticas', 
                              template="plotly_dark")
                fig2.update_layout(
                title=f'Estadisticas de {str(dt1.names[i])}',
                xaxis_title='Estadisticas',
                yaxis_title="Valar sobre 100",
                legend_title="Estadisticas",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
                fig2.update_layout(
                xaxis_title='pac                 sho                 pas                 dri                  def                 phy',
                yaxis_title="Valor estadisticas",
                legend_title=f'{(dt1.jug[i])}'
                )
                st.write(fig2)
            

            
            with e2:
                st.write(' ')
            
            with col1:
                st.header('Price Evolution')
                st.write(evo_price1([dt1.names[i]],[dt1.jug2[i]]))
           
            
            with cc1:
                st.header('Detailed Information')
                st.table(dt1[['names', 'pos', 'version', 'equipo', 'liga', 'med', 'pac', 'sho', 'pas',
       'dri', 'def', 'phy', 'S/M', 'W/F', 'foot', 'att/def_average', 'igs']][dt1.med==(dt1.med[i])])
          
        
with pes[1]:
    
    pest1, pest2 = st.tabs(['Free comparation', 'Position comparation'])
    
    with pest1:
        dt1 = pd.DataFrame(data)
        jug = [str(dt1.names[i])+' '+str(dt1.version[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
        jug2 = [str(dt1.names[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
        dt1['jug']=jug
        dt1['jug2']=jug2
        options = st.multiselect(
         'Select players',
         list(dt1['jug'])  
                                )
        plays = [dt1.index[dt1.jug==i][0] for i in options]    
        names = [j for i in options for j in list(dt1.names[dt1.jug==i])]
        play = [j for i in options for j in list(dt1.jug2[dt1.jug==i])]

        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.header('Radar Comparation')
            fig = radar2(plays)
            st.write(fig)

        with fig_col2:
            st.header('Statistics Comparation')
            fig = bar_comp(plays)
            st.write(fig)

        cc1 = st.container()

        with cc1:
            st.header('Price Evolution') 
            fig = evo_price(names, play)
            st.write(fig)
        
        n=options
        ind=[]
        for i in n:
            ind.append(list(dt1.names[dt1.jug==i].index))
        indd=[j for i in ind for j in i]
       
        cc2 = st.container()
        
        with cc2:
            st.header('Detailed Information')
            st.table(dt1[['names', 'pos', 'version', 'equipo', 'liga', 'med', 'pac', 'sho', 'pas',
       'dri', 'def', 'phy', 'S/M', 'W/F', 'foot', 'att/def_average', 'igs']].loc[indd])
    
    
    with pest2:
        dt1 = pd.DataFrame(data)
        jug = [str(dt1.names[i])+' '+str(dt1.version[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
        jug2 = [str(dt1.names[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
        dt1['jug']=jug
        dt1['jug2']=jug2
        pos_filter = st.selectbox('Select a position', pd.unique(dt1['pos']))
        
        st.dataframe(dt1[['names', 'pos', 'version', 'equipo', 'liga', 'med', 'pac', 'sho', 'pas',
       'dri', 'def', 'phy', 'S/M', 'W/F', 'foot', 'att/def_average', 'igs']][dt1.pos==pos_filter])
        
        options = st.multiselect(
         'Select players',
         list(dt1['jug'][dt1.pos==pos_filter])  
                                )
        plays = [dt1.index[dt1.jug==i][0] for i in options]    
        names = [j for i in options for j in list(dt1.names[dt1.jug==i])]
        play = [j for i in options for j in list(dt1.jug2[dt1.jug==i])]

        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.header('Radar Comparation')
            fig = radar2(plays)
            st.write(fig)

        with fig_col2:
            st.header('Statistics Comparation')
            fig = bar_comp(plays)
            st.write(fig)

        cc1 = st.container()

        with cc1:
            st.header('Price Evolution') 
            fig = evo_price(names, play)
            st.write(fig)
        
        n=options
        ind=[]
        for i in n:
            ind.append(list(dt1.names[dt1.jug==i].index))
        indd=[j for i in ind for j in i]
       
        cc2 = st.container()
        
        with cc2:
            st.header('Detailed Information')
            st.table(dt1[['names', 'pos', 'version', 'equipo', 'liga', 'med', 'pac', 'sho', 'pas',
       'dri', 'def', 'phy', 'S/M', 'W/F', 'foot', 'att/def_average', 'igs']].loc[indd])
      
    
with pes[2]:
    
    st.header('Price Prediction')
    dt1 = pd.DataFrame(data)
    jug = [str(dt1.names[i])+' '+str(dt1.version[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
    jug2 = [str(dt1.names[i])+' '+str(dt1.med[i]) for i in (list(dt1.index))]
    dt1['jug']=jug
    dt1['jug2']=jug2
    
    player_filter =  st.selectbox('Select a player', pd.unique(dt1['jug']))
    price_df = pd.json_normalize(list(db.price_players3.find({'names':player_filter})))
    
    ind = list(dt1[dt1.jug==player_filter].index)

    name = dt1.names[ind[0]]
    med = int(dt1.med[ind[0]])
    ver =dt1.version[ind[0]]
    
    x = int(st.number_input('predicciones'))
    l = int(st.number_input('lags'))
    fig = predict_price(name, med, ver,x, l)
    st.write(fig)



    
        
        
with pes[3]:
        
    a,s,b =st.columns(3)
    with a:
        st.write(' ')
    with s:
        st.title('¡Muchas gracias a todos!  :)')
        st.image(Image.open('bichoironhack.jpg'))
    with b:
        st.write(' ')     
   
