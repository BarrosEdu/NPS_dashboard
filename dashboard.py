#Importando as bibliotecas
import pandas as pd
#pd.set_option('display.max_columns', 70)
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

st.write("""
         # Welcome NPS Dashboard!
         A Python-built dashboard.
         """)
st.sidebar.header('We are working here')

#Carregando o dataset
df = pd.read_parquet('input/nps_data_full.parquet',engine='fastparquet')

#Selecionando as colunas para analise
df_1 = df[['FB_UID','WEEK_COMMENCING','STORE_LOCATIONCLASS','RATING_NPS','FB_SENTIMENT','FB_CHANNEL']]
df_1['WEEK_COMMENCING'] = pd.to_datetime(df_1['WEEK_COMMENCING'],yearfirst=True)

# Agrupando por dia
grouped_data = df_1.groupby(df_1['WEEK_COMMENCING'].dt.date)

nps_scores = []

# Loop through each day's data
for day, group in grouped_data:
    sample_size = group['FB_UID'].count()
    promoter = group[group['RATING_NPS'] >= 9]['FB_UID'].count()
    detractor = group[group['RATING_NPS'] <= 6]['FB_UID'].count()
    passive = group[(group['RATING_NPS'] == 7) | (group['RATING_NPS'] == 8)]['FB_UID'].count()

    # Calculate NPS for the current day
    percentage_promoters = (promoter / sample_size) * 100
    percentage_detractors = (detractor / sample_size) * 100

    NPS = percentage_promoters - percentage_detractors

    # Store the NPS score and the corresponding date in a list
    nps_scores.append({'Date': day, 'NPS': NPS})

# Create a new DataFrame with NPS scores for each day
nps_df = pd.DataFrame(nps_scores)

nps_df['Date'] = pd.to_datetime(nps_df['Date'])
nps_df['Month'] = nps_df['Date'].dt.month_name()

#Criando um filtro para analisar por mes.
month = st.sidebar.selectbox("Mes",nps_df['Month'].unique())
#nps_df = nps_df[nps_df["Month"] == month]




#Criando layout

col1,col2 = st.columns(2)
col3,col4,col5 = st.columns(3)

fig_nps = px.line(nps_df, x="Date", y="NPS", title="NPS Monthly")
col1.plotly_chart(fig_nps,use_container_width=True)

contador = pd.DataFrame(df_1['FB_SENTIMENT'].value_counts()).reset_index()
fig_sentiment = px.pie(contador, names="FB_SENTIMENT", values="count", title="NPS Group")
col2.plotly_chart(fig_sentiment,use_container_width=True)

touchpoint = pd.DataFrame(df_1['FB_CHANNEL'].value_counts()).reset_index()
fig_touch = px.bar(touchpoint, x="FB_CHANNEL", y="count", title="Total touchpoint")
col3.plotly_chart(fig_touch,use_container_width=True)

df_bar = pd.DataFrame(df_1['RATING_NPS'].value_counts()).reset_index()
fig_rating = px.bar(df_bar, x="RATING_NPS", y="count", title="Rating distribution",color='count')
col4.plotly_chart(fig_rating,use_container_width=True)

##NPS By Channel
df_channel = df_1.copy()
df_channel = df_channel[['RATING_NPS','FB_CHANNEL']]
touchpoint_nps = df_channel.groupby('FB_CHANNEL')['RATING_NPS'].apply(lambda x: (x >= 9).sum() / len(x) - (x <= 6).sum() / len(x)).reset_index()
touchpoint_nps.rename(columns={'RATING_NPS': 'NPS'}, inplace=True)
touchpoint_nps['NPS']= (touchpoint_nps['NPS']*100).round(0)


fig_channel = px.bar(touchpoint_nps, x='FB_CHANNEL',y='NPS', title="NPS by Channel",color='FB_CHANNEL',text_auto=True)
col5.plotly_chart(fig_channel,use_container_width=True)