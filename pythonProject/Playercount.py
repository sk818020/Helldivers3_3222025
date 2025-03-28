from datetime import tzinfo

import streamlit as st
#from seaborn.external.docscrape import header
from st_aggrid import AgGrid
import st_aggrid
import json
import requests
import pandas as pd
import numpy as np
#import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
import plotly.express as px
import datetime as dt
#from streamlit_dynamic_filters import DynamicFilters
import pytz

st.set_page_config(layout="wide")

res = requests.get("https://helldiverstrainingmanual.com/api/v1/war/campaign")
response = json.loads(res.text)
df = pd.DataFrame(response)
df.rename(columns={'players': 'player_count'}, inplace=True)
l_planets = df['planetIndex'].unique().tolist()
df3 = pd.DataFrame()
for i in l_planets:
    planet = str(i)
    planet_name = df[df['planetIndex'] == int(planet)]['name'].iloc[0]
    res = requests.get("https://helldiverstrainingmanual.com/api/v1/war/history/{x}".format(x = planet))
    response = json.loads(res.text)
    df2 = pd.DataFrame(response)
    df2['created_at'] = pd.to_datetime(df2['created_at'])
    df2['created_at'] = df2['created_at'].dt.tz_convert('MST')
    df3 = pd.concat([df3, df2])
map1 = df[['planetIndex', 'name', 'faction']]
df3 = pd.merge(df3, map1, left_on='planet_index', right_on='planetIndex')
df3['created_at'] = pd.to_datetime(df3['created_at'])
df3['created_at'] = df3['created_at'].dt.tz_convert('MST')

current_time = dt.datetime.now()
timezone = pytz.timezone('America/Denver')
localized_time = timezone.localize(current_time)
localized_time = localized_time.strftime('%m/%d/%y - %H:%M')
#stamp = dt.datetime.now().strftime('%m/%d/%y - %H:%M')
#stamp = stamp.replace(tzinfo=dt.timezone.utc)

st.title('Helldivers 2 Player Count Analysis - {x} MST'.format(x = localized_time))
st.text_area("",
    "Note: the left graph uses minute by minute data, and the right uses every 5 minute data. This can lead to small differences"\
    " in player count.",
             height = 80
)

st.sidebar.image(r"https://image.api.playstation.com/vulcan/ap/rnd/202309/2115/249a75447b653d4118ee62f1a733ad8ee66beaa0e11ea60b.png")
st.sidebar.header('Choose selection:')

planet_filter = st.sidebar.multiselect(
    'Select Planet',
    options = df3['name'].unique()
)
faction_filter = st.sidebar.multiselect(
    'Select Faction',
    options = df3['faction'].unique(),
    default = df3['faction'].unique()
)

col1, col2, col3 = st.columns(3)
fig1 = px.bar(df[df['faction'].isin(faction_filter)], x='faction', y='player_count', color = 'name',
              title = 'Player Count by Faction and Planet')
fig2 = px.line(df3[df3['faction'].isin(faction_filter)], x = 'created_at', y = 'player_count', color = 'name',
               title = 'Player Count (last 24 hours, Mountain time)')
fig3 = px.line(df3, y = 'current_health', x = 'created_at', color = 'name',
               title = 'Current Health by Planet')

with col1:
    st.plotly_chart(fig1)
with col2:
    st.plotly_chart(fig2)
with col3:
    st.plotly_chart(fig3)
@st.cache_data
def convert_df(df3):
    return df3.to_csv(index=False).encode('utf-8')

csv = convert_df(df3)
st.download_button(
    "Press to download data",
    csv,
    "player-data {x}.csv".format(x = localized_time),
    "text/csv",
    key="download-csv"
)
st_aggrid.AgGrid(df3[df3['faction'].isin(faction_filter)])