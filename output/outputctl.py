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

    redis_creds = parsed_yaml['Databases']['Redis']['Credentials']
    redis_host = parsed_yaml['Databases']['Redis']['Host']
    redis_port = parsed_yaml['Databases']['Redis']['Port']
    redis_username = str(redis_creds).split(":")[0]
    redis_password = str(redis_creds).split(":")[1]

    mongo_creds = parsed_yaml['Databases']['Mongodb']['Credentials']
    mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
    mongo_port = parsed_yaml['Databases']['Mongodb']['Port']
    mongo_username = str(mongo_creds).split(":")[0]
    mongo_password = str(mongo_creds).split(":")[1]

    ### GET DATA FROM REDIS ###
    while True:
        if not os.path.exists("outputctl.lck"):
            break
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, username=redis_username)
        json_data = r.lpop("data")
        if json_data == "":
            time.sleep(1)
            continue
        r.close()

        ### SEND DATA TO MONGODB ###
        uri = "mongodb://%s:%s@%s" % (urllib.parse.quote_plus(mongo_username), urllib.parse.quote_plus(mongo_password), mongo_host)
        m = MongoClient(uri)
        mdb = m.data
        mdb.ScrapeYard.insert_one(json_data)

        ### SEND TO ENDPOINTS ###
        for mod in parsed_yaml["Modules"]["Output"]:
            try:
                print("output." + mod + " reloaded...")
                module = importlib.import_module("output." + mod)
                try:
                    with open("output." + mod + ".lck", "w") as f:
                        f.write(datetime.datetime.now().strftime("%H:%M:%S"))
                    thread = threading.Thread(target=module.__init__, args=json_data)
                    thread.start()
                except:
                    error_string = "Unable to start the module: " + mod
                    logging.log(logging.ERROR, error_string)
            except:
                error_string = "Unable to load the module: " + mod
                logging.log(logging.ERROR, error_string)