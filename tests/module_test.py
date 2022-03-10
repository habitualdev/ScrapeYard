#!/usr/bin/python3
import sys
import threading
import importlib
import time
from manager.config import get_config
import redis
import json


parsed_yaml = get_config()
redis_host = parsed_yaml['Databases']['Redis']['Host']
redis_port = parsed_yaml['Databases']['Redis']['Port']


def module_test(test_module):
    r = redis.Redis(host=redis_host, port=redis_port)
    try:
        print("Redis database information: ")
        print(r.info(), "\n")
    except:
        print("Redis database not accessible. Check Redis settings inside config.yaml, or if the database is running.\n")
        return
    module = importlib.import_module(test_module)
    try:
        type(module.QueryClass)
    except:
        print("No QueryClass class to instantiate. \n")
        return
    thread = threading.Thread(target=module.QueryClass, daemon=True)
    thread.start()
    time.sleep(1)
    json_data = r.lpop("data")
    if json_data is None:
        print("No data returned.")
        return
    else:
        print("Data returned/ingested:")
        print(" -- ", str(json_data)[1:], "\n")
        print("JSON format test:")
        try:
            json.loads(json_data)
            print(" -- JSON parses properly", "\n")
        except:
            print(" -- JSON not parsable.", "\n")
    print("Flushing Redis database of any testing data.", "\n")
    r.flushall()


if __name__ == '__main__':
    arg = sys.argv[1]
    print("Testing %s module...\n" % arg)
    module_test(arg)
    print("---------------------------------------------------------")
