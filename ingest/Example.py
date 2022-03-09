import time
from os.path import exists
import redis
import manager.config

# Query Time - in seconds #
QueryTime = 10


def __init__():
    n = QueryTime
    parsed_yaml = manager.config.get_config()
    while True:
        if n >= QueryTime:
            n = 0
            get_data(parsed_yaml)
        time.sleep(1)
        n += 1
        if not exists("ingest.Example.lck"):
            break


def get_data(parsed_yaml):

    redis_host = parsed_yaml['Databases']['Redis']['Host']
    redis_port = parsed_yaml['Databases']['Redis']['Port']
    r = redis.Redis(host=redis_host, port=redis_port)

    data = retrieve_data()
    try:
        r.rpush("data", data)
    except:
        print("Example : Unable to push to Redis stack")


def retrieve_data():
    data = '{"Module":"Example", "Data": {"name":"John", "age":30, "car":"civic"}}'
    return data
