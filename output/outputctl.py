import json
import os.path
import time
import manager.config
import importlib
import threading
import logging
import redis
import datetime
from pymongo import MongoClient

class OutputCtl:
    def __init__(self):
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
                time.sleep(1)
                r.close()
            else:
                ### SEND DATA TO MONGODB ###
                m = MongoClient(host=mongo_host, port=mongo_port)
                try:
                    mdb = m["ScrapeYard"][json.loads(json_data)["Module"]]
                    mdb.insert_one(json.loads(json_data)["Data"])
                except Exception as e:
                    print(e)

                ### SEND TO ENDPOINTS ###
                try:
                    for mod in parsed_yaml["Modules"]["Output"]:
                        try:
                            print("output." + mod + " reloaded...")
                            module = importlib.import_module("output." + mod)
                            try:
                                with open("output." + mod + ".lck", "x") as f:
                                    f.write(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                                thread = threading.Thread(target=module.__init__, args=str(json_data))
                                thread.start()
                            except:
                                error_string = "Unable to start the module: " + mod
                                logging.log(logging.ERROR, error_string)
                        except:
                            error_string = "Unable to load the module: " + mod
                            logging.log(logging.ERROR, error_string)
                except:
                    continue
