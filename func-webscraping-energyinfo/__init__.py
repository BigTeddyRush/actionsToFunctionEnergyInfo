import azure.functions as func
import logging
import pyodbc
from config import database_config
import requests
from bs4 import BeautifulSoup
import json
import datetime


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

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This is a so damn fu***** bad day. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

