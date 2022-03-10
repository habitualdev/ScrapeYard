import logging
from splunk_hec_handler import SplunkHecHandler

# Splunk Host Information #
splunk_host = 'splunkfw.domain.tld'
splunk_token = '<PLACEHOLDER TOKEN>'
splunk_port = 8088
splunk_proto = 'http'
splunk_source = "HEC_Example"


def __init__(*args):
    rebuild_string = ""
    for arg in args:
        rebuild_string = rebuild_string + arg
    return
    logger = logging.getLogger('HEC_Handler')
    logger.setLevel(logging.DEBUG)
    splunk_handler = SplunkHecHandler(splunk_host, splunk_token, port=splunk_port, proto=splunk_proto,source=splunk_source)
    logger.addHandler(splunk_handler)
    logger.log(logging.INFO, json_data)





