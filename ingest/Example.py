import time
from os.path import exists
import redis
import manager.config


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
            if not exists("ingest.Example.lck"):
                break

    def load_redis(self, parsed_yaml):
        redis_host = parsed_yaml['Databases']['Redis']['Host']
        redis_port = parsed_yaml['Databases']['Redis']['Port']
        r = redis.Redis(host=redis_host, port=redis_port)
        self.retrieve_data()
        try:
            r.rpush("data", self.data)
        except:
            print("Example : Unable to push to Redis stack")

    def retrieve_data(self):
        self.data = '{"Module":"Example", "Data": {"name":"John", "age":30, "car":"civic"}}'
