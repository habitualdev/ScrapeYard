import os
import time
from os.path import exists
import redis
import manager.config
import requests
import json
from pymongo import MongoClient


maltiverse_token = os.getenv("MALTIVERSE_API")

def get_urls(maltiverse_auth):
    entries = []
    header = {'Authorization': 'Bearer ' + maltiverse_auth}
    url_raw_json = requests.get("https://api.maltiverse.com/search?query=type:url&from=0&size=5000&format"
                                "=json&sort=creation_time_desc&range=now-1h&range_field=creation_time",
                                headers=header)
    entries.append(url_raw_json.json()["hits"])
    hostname_raw_json = requests.get("https://api.maltiverse.com/search?query=type:hostname&from=0&size=5000&format"
                                     "=json&sort=creation_time_desc&range=now-1h&range_field=creation_time",
                                     headers=header).json()
    entries.append(hostname_raw_json["hits"])
    ip_raw_json = requests.get(
                                    "https://api.maltiverse.com/search?query=type:ip&from=0&size=5000&format"
                                    "=json&sort=creation_time_desc&range=now-1h&range_field=creation_time",
                                    headers=header).json()
    entries.append(ip_raw_json["hits"])
    sample_raw_json = requests.get(
                                    "https://api.maltiverse.com/search?query=type:sample&from=0&size=5000&format"
                                    "=json&sort=creation_time_desc&range=now-1h&range_field=creation_time",
                                    headers=header).json()
    entries.append(sample_raw_json["hits"])
    return entries

class QueryClass:
    def __init__(self):
        with open("ingest.Maltiverse.lck") as f:
            self.start_time = f.read()
        self.data = ""
        self.QueryTime = 3600
        self.n = self.QueryTime
        parsed_yaml = manager.config.get_config()
        while True:
            if self.n >= self.QueryTime:
                self.n = 0
                self.load_redis(parsed_yaml)
            time.sleep(1)
            self.n += 1
            if not exists("ingest.Maltiverse.lck"):
                break
            with open("ingest.Maltiverse.lck") as f:
                if f.read() != self.start_time:
                    break

    def load_redis(self, parsed_yaml):
        redis_host = parsed_yaml['Databases']['Redis']['Host']
        redis_port = parsed_yaml['Databases']['Redis']['Port']
        mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
        mongo_port = parsed_yaml['Databases']['Mongodb']['Port']
        r = redis.Redis(host=redis_host, port=redis_port)
        self.retrieve_data()

        for entry_set in self.data:
            m = MongoClient(host=mongo_host, port=mongo_port)
            for entry in entry_set["hits"]:
                existing_entries = []
                mdb = m["ScrapeYard"]["Maltiverse"]
                try:
                    for x in mdb.find(entry):
                        existing_entries.append(x)
                    if len(existing_entries) == 0:
                        try:
                            r.rpush("data",
                                    '{"Module":"Maltiverse", "Data": ' + json.dumps(entry) + ",\"TimeStamp\":\"" + str(
                                        time.time()) + '"}')
                        except Exception as e:
                            print("Maltiverse : Unable to push to Redis stack : " + str(e))
                except Exception as e:
                    print("Maltiverse : Unable to push to MongoDB : " + str(e))

    def retrieve_data(self):
        self.data = get_urls(maltiverse_token)
