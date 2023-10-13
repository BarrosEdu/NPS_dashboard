#Importando as bibliotecas
import pandas as pd
#pd.set_option('display.max_columns', 70)
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

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
col3,col4,col4 = st.columns(3)

fig_nps = px.line(nps_df, x="Date", y="NPS", title="NPS Monthly")
col1.plotly_chart(fig_nps)

contador = pd.DataFrame(df_1['FB_SENTIMENT'].value_counts()).reset_index()

fig_sentiment = px.pie(contador, names="FB_SENTIMENT", values="count", title="NPS Group")
col2.plotly_chart(fig_sentiment)