import pandas as pd
import streamlit as st
import plotly.express as px
import pyodbc

# Erstelle das Dictionary
power_consumption_dict = {'unix_seconds' : [], 'name' : [], 'data' : []}

server = 'energycharts.database.windows.net'
database = 'EnergyChartsDB'
driver = '{ODBC Driver 17 for SQL Server}'
username = 'bigteddyrush'
password = 'qepniZ-tyhxus-3pubmu'

# Daten aus Datenbank abrufen
try:
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            # Daten aus der Datenbank abrufen
            cursor.execute("SELECT unix_seconds, name, data FROM dbo.EnergyCharts")
            rows = cursor.fetchall()
            
            # Werte in das Dictionary speichern
            for row in rows:
                unix_seconds, name, data = row
                power_consumption_dict['unix_seconds'].append(unix_seconds)
                power_consumption_dict['name'].append(name)
                power_consumption_dict['data'].append(data)
except pyodbc.Error as ex:
    print("Fehler beim Verbinden zur Datenbank:", ex)

################################

data = power_consumption_dict

df = pd.DataFrame(data)

# Streamlit-App-Layout definieren
st.title('Visualisierung des DataFrames')

# DataFrame anzeigen
st.write(df)

# Plot erstellen
fig = px.line(df, x='unix_seconds', y='data', color='name', title='Hydro pumped storage consumption über die Zeit')
fig.update_layout(xaxis_title='Zeit', yaxis_title='Verbrauch')
st.plotly_chart(fig)
