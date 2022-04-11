import base64
import hashlib
import json
import time
from os.path import exists
import redis
from pymongo import MongoClient

import manager.config
import requests
import ast


def get_points():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    raw_json = requests.get("https://cvetrends.com/api/cves/24hrs", headers=headers).json()['data']
    return raw_json

class QueryClass:
    def __init__(self):
        with open("ingest.CveTrendsGithub.lck") as f:
            self.start_time = f.read()
        self.data = ""
        self.QueryTime = 1800
        self.n = self.QueryTime
        parsed_yaml = manager.config.get_config()
        while True:
            if self.n >= self.QueryTime:
                self.n = 0
                self.load_redis(parsed_yaml)
            time.sleep(1)
            self.n += 1
            if not exists("ingest.CveTrendsGithub.lck"):
                break
            with open("ingest.CveTrendsGithub.lck") as f:
                if f.read() != self.start_time:
                    break

    def load_redis(self, parsed_yaml):
        redis_host = parsed_yaml['Databases']['Redis']['Host']
        redis_port = parsed_yaml['Databases']['Redis']['Port']
        mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
        mongo_port = parsed_yaml['Databases']['Mongodb']['Port']
        r = redis.Redis(host=redis_host, port=redis_port)
        self.retrieve_data()
        for record in self.data:
            for entry in record["github_repos"]:
                m = MongoClient(host=mongo_host, port=mongo_port)
                try:
                    existing_entries = []
                    mdb = m["ScrapeYard"]["CveTrendsGithub"]
                    for x in mdb.find({"CVE": record["cve"], "Severity": str(record["cvssv3_base_score"]), "created": entry["created"], "description": entry["description"],  "name": entry["name"], "url": entry["url"]}):
                        existing_entries.append(x)
                    if len(existing_entries) == 0:
                        try:
                            r.rpush("data",
                                    '{"Module":"CveTrendsGithub", "Data": ' + json.dumps({"CVE": record["cve"], "Severity": str(record["cvssv3_base_score"]), "created": entry["created"], "description": entry["description"],  "name": entry["name"], "url": entry["url"]}) + ",\"TimeStamp\":\"" + str(time.time()) + '"}')
                        except:
                            print(" CveTrendsGithub: Unable to push to Redis stack")

                except Exception as e:
                    print(e)


    def retrieve_data(self):
        self.data = get_points()
