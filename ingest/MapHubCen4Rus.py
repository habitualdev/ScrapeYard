import base64
import json
import time
from os.path import exists
import redis
from pymongo import MongoClient

import manager.config
import requests
import ast


def get_points():
    entry_list = []
    raw_json = requests.post("https://maphub.net/json/map_load/176607","{}").json()["geojson"]["features"]

    for entry in raw_json:
        entry_list.append(entry["properties"])

    return  entry_list

class QueryClass:
    def __init__(self):
        self.data = ""
        self.QueryTime = 10
        self.n = self.QueryTime
        parsed_yaml = manager.config.get_config()
        while True:
            if self.n >= self.QueryTime:
                self.n = 0
                self.load_redis(parsed_yaml)
            time.sleep(1)
            self.n += 1
            if not exists("ingest.MapHubCen4Rus.lck"):
                break

    def load_redis(self, parsed_yaml):
        redis_host = parsed_yaml['Databases']['Redis']['Host']
        redis_port = parsed_yaml['Databases']['Redis']['Port']
        mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
        mongo_port = parsed_yaml['Databases']['Mongodb']['Port']
        r = redis.Redis(host=redis_host, port=redis_port)
        self.retrieve_data()
        for record in self.data:
            m = MongoClient(host=mongo_host, port=mongo_port)
            try:
                existing_entries = []
                mdb = m["ScrapeYard"]["MapHubCen4Rus"]
                for x in mdb.find({}, {"title": json.loads(json.dumps(record))["title"]}):
                    existing_entries.append(x)
                if len(existing_entries) == 0:
                    try:
                        print(json.loads(json.dumps(record))["title"])
                        r.rpush("data",
                                '{"Module":"MapHubCen4Rus", "Data": ' + json.dumps(record) + ",\"TimeStamp\":\"" + str(
                                    time.time()) + '"}')
                    except:
                        print(" MapHubCen4Rus: Unable to push to Redis stack")

                else:
                    print("Entry exists.")
            except Exception as e:
                # print(json_data)
                print(e)


    def retrieve_data(self):
        self.data = get_points()
