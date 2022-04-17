import datetime
import importlib
import logging
import os.path
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
    thread_list = []
    for thread in threading.enumerate():
        thread_list.append(thread.name)

    for mod in yaml_parsed["Modules"]["Ingest"]:  # Read the parsed YAML to see what modules should be run.
        try:
            module = importlib.import_module("ingest." + mod)
            try:
                if not os.path.exists("ingest." + mod + ".lck"):
                    print("ingest." + mod + " reloaded...")  # Print the module to be loaded to stdout
                    with open("ingest." + mod + ".lck", "w") as f:  # Drop a lock file for simple checking
                        f.write(datetime.datetime.now().strftime("%H:%M:%S"))  # Write the time loaded to the lock file
                    thread = threading.Thread(target=module.QueryClass, name=mod)  # start a separate thread
                    thread.start()
                elif os.path.exists("ingest." + mod + ".lck"):
                    if mod not in thread_list:  # If the module is not running, start it.
                        thread = threading.Thread(target=module.QueryClass, name=mod)
                        thread.start()
            except:
                error_string = "Unable to start the module: " + mod  # To see if QueryClass fails
                logging.log(logging.ERROR, error_string)
        except:
            error_string = "Unable to load the module: " + mod  # To see if importlib fails
            logging.log(logging.ERROR, error_string)
    try:
        if not os.path.exists("outputctl" + ".lck"):
            with open("outputctl" + ".lck", "w") as f:
                f.write(datetime.datetime.now().strftime("%H:%M:%S"))
            thread = threading.Thread(target=output.outputctl.OutputCtl)
            thread.start()
    except:
        error_string = "Unable to start the module: " + mod  # To check if OutputCtl fails
        logging.log(logging.ERROR, error_string)

