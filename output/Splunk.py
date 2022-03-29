import json
import logging
from splunk_hec_handler import SplunkHecHandler

# Splunk Host Information #
splunk_host = 'splunk.server.local'
splunk_token = '<SPLUNK TOKEN>'
splunk_port = 8088
splunk_proto = 'http'
splunk_source = "HEC_Example"


def __init__(*args):
    rebuild_string = ""
    for arg in args:
        rebuild_string = rebuild_string + arg
    data = json.loads(rebuild_string[1:].replace("'", ""))
    logger = logging.getLogger('HEC_Handler')
    logger.setLevel(logging.DEBUG)
    print(data)
    splunk_handler = SplunkHecHandler(splunk_host, splunk_token, port=splunk_port, proto=splunk_proto, source=data["Module"])
    logger.addHandler(splunk_handler)
    logger.log(logging.INFO, data["Data"])
    logger.removeHandler(splunk_handler)





