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
    for mod in yaml_parsed["Modules"]["Ingest"]:  # Read the parsed YAML to see what modules should be run.
        try:
            print("ingest." + mod + " reloaded...")  # Print the module to be loaded to stdout for logging purposes
            module = importlib.import_module("ingest." + mod)
            try:
                with open("ingest." + mod + ".lck", "w") as f:  # Drop a lock file for simple inter-thread communication
                    f.write(datetime.datetime.now().strftime("%H:%M:%S"))  # Write the time loaded to the lock file
                thread = threading.Thread(target=module.QueryClass)  # start a separate thread for the module
                thread.start()
            except:
                error_string = "Unable to start the module: " + mod  # To see if QueryClass fails
                logging.log(logging.ERROR, error_string)
        except:
            error_string = "Unable to load the module: " + mod  # To see if importlib fails
            logging.log(logging.ERROR, error_string)
    try:
        with open("outputctl" + ".lck", "w") as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S"))
        thread = threading.Thread(target=output.outputctl.OutputCtl)
        thread.start()
    except:
        error_string = "Unable to start the module: " + mod  # To check if OutputCtl fails
        logging.log(logging.ERROR, error_string)

