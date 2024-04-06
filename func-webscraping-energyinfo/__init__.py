import azure.functions as func
import logging
import pyodbc
import os
import requests
import json
import datetime
from azure.identity import DefaultAzureCredential
import struct


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name == 'load':
        webscraping()
        return func.HttpResponse(f"Hello, {name} worked fine. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "Bitte übergebe den Parameter 'load' als name, um die Datenbank zu befüllen ",
             status_code=200
        )

def webscraping():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    # power consumption in Germany on one specific day
    siteurl = f"https://api.energy-charts.info/total_power?country=de&start={yesterday}T00%3A00%2B01%3A00&end={yesterday}T23%3A45%2B01%3A00"
    response = requests.get(siteurl)
    power_consumption = json.loads(response.content.decode('utf-8'))

    # create a list of the time_stamps, types and data
    unix_seconds_list = []
    name_list = []
    data_list = []
    for typ in range(len(power_consumption['production_types'])):
        for time in range(len(power_consumption['unix_seconds'])):
            # append unix_seconds
            unix_seconds_list.append(datetime.datetime.fromtimestamp(power_consumption['unix_seconds'][time]).strftime("%m/%d/%Y, %H:%M:%S"))
            # append production_types
            name_list.append(power_consumption['production_types'][typ]['name'])
            # append data
            data_list.append(power_consumption['production_types'][typ]['data'][time])

    # create dict
    power_consumption_dict = {'unix_seconds' : unix_seconds_list, 'name' : name_list, 'data' : data_list}

    #server = 'energycharts.database.windows.net'
    #database = 'EnergyChartsDB'
    #username = 'bigteddyrush'
    #password = '{qepniZ-tyhxus-3pubmu}'
    driver = '{ODBC Driver 17 for SQL Server}'

    connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]

    try:
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
        with pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}) as conn:
            with conn.cursor() as cursor:
                # delte database to fill with new data
                cursor.execute("DELETE FROM dbo.EnergyCharts")
                for i in range(len(power_consumption_dict['unix_seconds'])):
                    unix_seconds = power_consumption_dict['unix_seconds'][i]
                    name = power_consumption_dict['name'][i]
                    data = power_consumption_dict['data'][i]

                    # INSERT-Befehl ausführen
                    query = "INSERT INTO dbo.EnergyCharts ([unix_seconds], [name], [data]) VALUES (?, ?, ?)"
                    cursor.execute(query, (unix_seconds, name, data))
    except pyodbc.Error as ex:
        print("Fehler beim Verbinden zur Datenbank:", ex)