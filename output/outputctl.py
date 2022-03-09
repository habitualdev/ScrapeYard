import base64
import json
import os.path
import time
import urllib.parse
import manager.config
import importlib
import threading
import logging
import redis
import datetime
from pymongo import MongoClient


def __init__():
    parsed_yaml = manager.config.get_config()

    redis_host = parsed_yaml['Databases']['Redis']['Host']
    redis_port = parsed_yaml['Databases']['Redis']['Port']

    mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
    mongo_port = parsed_yaml['Databases']['Mongodb']['Port']

    ### GET DATA FROM REDIS ###
    while True:
        if not os.path.exists("outputctl.lck"):
            break
        r = redis.Redis(host=redis_host, port=redis_port)
        json_data = r.lpop("data")
        if json_data is None:
            print("No data in redis.")
            time.sleep(1)
            r.close()
        else:
            ### SEND DATA TO MONGODB ###
            m = MongoClient(port=mongo_port)
            mdb = m["ScrapeYard"][json.loads(json_data)["Module"]]
            mdb.insert_one(json.loads(json_data)["Data"])

            ### SEND TO ENDPOINTS ###
            for mod in parsed_yaml["Modules"]["Output"]:
                try:
                    print("output." + mod + " reloaded...")
                    module = importlib.import_module("output." + mod)
                    try:
                        with open("output." + mod + ".lck", "w") as f:
                            f.write(datetime.datetime.now().strftime("%H:%M:%S"))
                        thread = threading.Thread(target=module.__init__, args=str(json_data))
                        thread.start()
                    except:
                        error_string = "Unable to start the module: " + mod
                        logging.log(logging.ERROR, error_string)
                except:
                    error_string = "Unable to load the module: " + mod
                    logging.log(logging.ERROR, error_string)
            r.close()