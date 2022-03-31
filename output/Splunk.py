import json
import logging
import os

from splunk_hec_handler import SplunkHecHandler

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
    logger = logging.getLogger('HEC_Handler')
    logger.setLevel(logging.DEBUG)
    splunk_handler = SplunkHecHandler(splunk_host, splunk_token, port=splunk_port, proto=splunk_proto, source=data["Module"])
    logger.addHandler(splunk_handler)
    logger.log(logging.INFO, data["Data"])
    logger.removeHandler(splunk_handler)





