import os

from elasticsearch import Elasticsearch
import uuid
import json


user = os.environ['ELASTIC_USER']
password = os.environ['ELASTIC_PASSWORD']
host = os.environ['ELASTIC_HOST']
port = os.environ['ELASTIC_PORT']

def __init__(*args):
    rebuild_string = ""
    for arg in args:
        rebuild_string = rebuild_string + arg
    data = json.loads(rebuild_string[1:].replace("'", ""))
    es = Elasticsearch([{'host': host, 'port': port}], http_auth=(user, password))
    es.index(index="scrapeyard", id=uuid.uuid4(), documents=data)
