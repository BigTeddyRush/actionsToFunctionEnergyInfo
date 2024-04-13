import pandas as pd
import streamlit as st
import plotly.express as px
import os
from data import my_dict

data = my_dict
df = pd.DataFrame(data)

# Streamlit-App-Layout definieren
st.title('Visualisierung des DataFrames')

# DataFrame anzeigen
st.write(df)

# Plot erstellen
fig = px.line(df, x='unix_seconds', y='data', color='name', title='Hydro pumped storage consumption über die Zeit')
fig.update_layout(xaxis_title='Zeit', yaxis_title='Verbrauch')
st.plotly_chart(fig)
