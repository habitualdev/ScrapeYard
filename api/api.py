import json
import os
import markdown
import redis
from flask import Flask
from flask import send_file
import markdown.extensions.fenced_code
from pymongo import MongoClient
import manager

def get_modules():
    f = []
    module_list = {}
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
        f.extend(filenames)
        break
    file_list = [k for k in f if '.lck' in k]
    for file in file_list:
        with open(file) as fd:
            time_text = fd.read()
            module_list[str(file).replace(".lck", "")] = time_text
    return json.dumps(module_list)

def redis_stats():
    parsed_yaml = manager.config.get_config()
    redis_host = parsed_yaml['Databases']['Redis']['Host']
    redis_port = parsed_yaml['Databases']['Redis']['Port']
    r = redis.Redis(host=redis_host, port=redis_port)
    return json.dumps({"redis": r.info("Keyspace")})


def mongo_stats():
    parsed_yaml = manager.config.get_config()
    mongo_host = parsed_yaml['Databases']['Mongodb']['Host']
    mongo_port = parsed_yaml['Databases']['Mongodb']['Port']
    module_list = []
    m = MongoClient(host=mongo_host, port=mongo_port)

    for modules in parsed_yaml['Modules']['Ingest']:
        module_list.append(modules)

    total_docs = []
    for mod in module_list:
        try:
            mdb = m["ScrapeYard"][mod]
            total_docs.append({mod: mdb.count_documents({})})
        except Exception as e:
            print(e)
    return json.dumps(total_docs)


def start():
    app = Flask(__name__)

    @app.route("/")
    def documentation():
        with open("README.md") as f:
            md_template_string = markdown.markdown(f.read(), extensions=["fenced_code"])
        return md_template_string

    @app.route("/api")
    def blank():
        return ""

    @app.route("/api/mongodb/counts")
    def get_mongo_counts():
        return mongo_stats()

    @app.route("/api/redis/stats")
    def get_redis_stats():
        return redis_stats()


    @app.route("/api/modules")
    def hello_world():
        return get_modules()

    @app.route("/assets/ScrapeYardFlow.png")
    def get_flow():
        return send_file(os.getcwd() + "/assets/ScrapeYardFlow.png", mimetype='image/png')

    app.run()
