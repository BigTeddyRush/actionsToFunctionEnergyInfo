import azure.functions as func
import logging
import pyodbc
import requests
import json
import datetime
import os


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
        
         # GitHub repository und Workflow Informationen
        repository_owner = "BigTeddyRush"
        repository_name = "container-actions-energy-info"
        workflow_file_path = "docker-image.yml"  # Passe den Pfad entsprechend an
        token = os.environ["TOKEN"]

        # Trigger des Workflow-Events
        trigger_workflow(repository_owner, repository_name, workflow_file_path, token)

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

    server = 'energycharts.database.windows.net'
    database = 'EnergyChartsDB'
    driver = '{ODBC Driver 17 for SQL Server}'

    try:
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';Authentication=ActiveDirectoryMsi',) as conn:
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

def trigger_workflow(repository_owner, repository_name, workflow_file_path, token):
    print(token)
    # GitHub API-Endpunkt für das Auslösen von Workflow-Events
    url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/actions/workflows/{workflow_file_path}/dispatches"

    # Erstelle den Payload für das simulierten Pull Request-Event
    payload = {
        "ref": "main",  # Ändere "main" zu deinem Hauptbranch-Namen
        "inputs": {}  # Optional: Füge Eingaben hinzu, die vom Workflow benötigt werden
    }

    # Führe den POST-Request aus, um das Workflow-Event auszulösen
    response = requests.post(url, json=payload, headers={"Authorization": f"token {token}"})

    # Überprüfe die Antwort des API-Aufrufs
    if response.status_code == 204:
        print("Workflow event successfully dispatched.")
    else:
        print(f"Failed to dispatch workflow event. Status code: {response.status_code}, Response: {response.text}")

   