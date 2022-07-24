#!/usr/bin/python3
import os
import pytest
import threading
import importlib
import time
from manager.config import get_config
import redis
import json
from yaml import CLoader as Loader, CDumper as Dumper
import yaml


parsed_yaml = get_config()
redis_host = parsed_yaml['Databases']['Redis']['Host']
redis_port = parsed_yaml['Databases']['Redis']['Port']


def module_test(test_module):
    with open("ingest_test_report.txt", "a") as f:
        r = redis.Redis(host=redis_host, port=redis_port)
        try:
            r.info()
            f.write("Redis connection successful\n")
            f.write("\n")
            print("Redis connection successful\n")
        except:
            f.write("Redis database not accessible. Check Redis settings inside config.yaml, or if the database is running.\n")
            print("Redis database not accessible. Check Redis settings inside config.yaml, or if the database is running.\n")
            return False
        module = importlib.import_module("ingest." + test_module)
        try:
            type(module.QueryClass)
        except:
            f.write("No QueryClass class to instantiate. \n")
            print("No QueryClass class to instantiate. \n")
            return False
        thread = threading.Thread(target=module.QueryClass, daemon=True)
        thread.start()
        json_data = r.lpop("data")
        if json_data is None:
            f.write("No data returned.")
            print("No data returned.")
            return False
        else:
            f.write("Data returned/ingested:")
            f.write(" -- " + str(json_data)[1:])
            f.write("\n")
            f.write("JSON format test:")
            print("Data returned/ingested:")
            print(" -- ", str(json_data)[1:], "\n")
            print("JSON format test:")
            try:
                json.loads(json_data)
                f.write(" -- JSON parses properly \n")
                print(" -- JSON parses properly", "\n")
            except:
                f.write(" -- JSON not parsable. \n")
                print(" -- JSON not parsable.", "\n")
                return False
        f.write("Flushing Redis database of any testing data. \n")
        print("Flushing Redis database of any testing data.", "\n")
        r.flushall()
        return True


def test_ingest_module():
    try:
        os.remove("ingest_test_report.txt")
    except:
        print("No previous report, continuing...")
    with open("config.yaml", "r") as f:
        yaml_raw = f.read()
    yaml_parsed = yaml.load(yaml_raw, Loader=Loader)
    for mod in yaml_parsed["Modules"]["Ingest"]:
        with open("ingest_test_report.txt", "a") as f:
            f.write("Testing %s module...\n" % mod)
            print("Testing %s module...\n" % mod)
            assert module_test(mod)
            f.write("---------------------------------------------------------")
            print("---------------------------------------------------------")
        time.sleep(2)
