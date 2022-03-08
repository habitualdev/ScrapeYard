import time
from os.path import exists
import redis
import manager.config


# Query Time - in seconds #
QueryTime = 10


def __init__():
    parsed_yaml = manager.config.get_config()
    n = QueryTime
    while True:
        if n >= QueryTime:
            n = 0
            get_data(parsed_yaml)
        time.sleep(1)
        n += 1
        if not exists("ingest.PowerOutage.lck"):
            break


def get_data(parsed_yaml):
    redis_creds = parsed_yaml['Databases']['Redis']['Credentials']
    redis_host = parsed_yaml['Databases']['Redis']['Host']
    redis_port = parsed_yaml['Databases']['Redis']['Port']
    redis_username = str(redis_creds).split(":")[0]
    redis_password = str(redis_creds).split(":")[1]

    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, username=redis_username)

    data = retrieve_data()
    try:
        r.rpush("data", data)
    except:
        print("PowerOutage : Unable to push to Redis stack")


def retrieve_data():
    data = " "
    return data