import os
import time
from python_on_whales import docker
import re
from tqdm import tqdm

def start_database():
    ps = docker.ps()
    names = []
    for container in ps:
        names.append(container.name)
    re_mongo = re.compile("scrapeyard_mongodb")
    re_redis = re.compile("scrapeyard_redis")
    if (len(list(filter(re_mongo.match, names))) == 1) and (len(list(filter(re_redis.match, names))) == 1):
        print("database containers found, continuing...")
        return
    else:
        print("database containers not found, creating...")
        os.system("docker-compose up -d")
        print("Waiting  5 seconds to ensure containers are built")
        for i in tqdm(range (5)):
            time.sleep(1)