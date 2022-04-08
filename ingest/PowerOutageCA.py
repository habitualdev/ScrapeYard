import hashlib
import json
import time
from os.path import exists
import redis
import manager.config
import requests


##	WebStateRecord [](
##		StateName     string `json:"StateName"`
##		StateStatus   string `json:"StateStatus"`
##		OutageCount   int    `json:"OutageCount"`
##		CustomerCount int    `json:"CustomerCount"`
## )

def get_records():
    web_records = requests.get("https://poweroutage.com/api/web/states?key=18561563181588&countryid=ca")
    return web_records.json()["WebStateRecord"]


class QueryClass:
    def __init__(self):
        with open("ingest.PowerOutageCA.lck") as f:
            self.start_time = f.read()
        self.data = ""
        self.QueryTime = 300
        self.n = self.QueryTime
        parsed_yaml = manager.config.get_config()
        while True:
            if self.n >= self.QueryTime:
                self.n = 0
                self.load_redis(parsed_yaml)
            time.sleep(1)
            self.n += 1
            if not exists("ingest.PowerOutageUS.lck"):
                break
            with open("ingest.PowerOutageCA.lck") as f:
                    if f.read() != self.start_time:
                        break


    def load_redis(self, parsed_yaml):
        redis_host = parsed_yaml['Databases']['Redis']['Host']
        redis_port = parsed_yaml['Databases']['Redis']['Port']
        r = redis.Redis(host=redis_host, port=redis_port)
        self.retrieve_data()
        for record in self.data:
            try:
                r.rpush("data", '{"Module":"PowerOutageCA", "Data": ' + str(record).replace("\'", "\"")[:-1] + ",\"TimeStamp\":\"" + str(time.time()) + '"}}')
            except:
                print("PowerOutageUS : Unable to push to Redis stack")

    def retrieve_data(self):
        self.data = get_records()


