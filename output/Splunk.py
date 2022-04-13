import json
import requests
import os

# Splunk Host Information #
splunk_host = os.environ['SPLUNK_HOST']
splunk_token = os.environ['SPLUNK_TOKEN']
splunk_port = os.environ['SPLUNK_PORT']
splunk_proto = os.environ['SPLUNK_PROTO']
splunk_source = os.environ['SPLUNK_SOURCE']


def __init__(*args):
    rebuild_string = ""
    for arg in args:
        rebuild_string = rebuild_string + arg
    data = json.loads(rebuild_string[1:].replace("'", ""))
    url = splunk_proto + '://' + splunk_host + ':' + splunk_port + '/services/collector/event'
    authHeader = {'Authorization': 'Splunk ' + splunk_token}
    payload = {}
    payload.update({"sourcetype": "_json"})
    payload.update({"source": data['Module']})
    payload.update({"host": "omegon"})
    payload.update({"event": data['Data']})
    r = requests.post(url, headers=authHeader, json=payload, verify=False)
