import datetime
import importlib
import logging
import threading
import yaml
import output.outputctl
from yaml import CLoader as Loader, CDumper as Dumper


def get_config():
    with open("config.yaml", "r") as f:
        yaml_raw = f.read()
    yaml_parsed = yaml.load(yaml_raw, Loader=Loader)
    return yaml_parsed


def run_modules(yaml_parsed):

    for mod in yaml_parsed["Modules"]["Ingest"]:
        try:
            print("ingest." + mod + " reloaded...")
            module = importlib.import_module("ingest." + mod)
            try:
                with open("ingest." + mod + ".lck", "w") as f:
                    f.write(datetime.datetime.now().strftime("%H:%M:%S"))
                thread = threading.Thread(target=module.QueryClass)
                thread.start()
            except:
                error_string = "Unable to start the module: " + mod
                logging.log(logging.ERROR, error_string)
        except:
            error_string = "Unable to load the module: " + mod
            logging.log(logging.ERROR, error_string)
    try:
        with open("outputctl" + ".lck", "w") as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S"))
        thread = threading.Thread(target=output.outputctl.__init__)
        thread.start()
    except:
        error_string = "Unable to start the module: " + mod
        logging.log(logging.ERROR, error_string)

