#!/usr/bin/python3
import os
import threading
import time
import api.api
import data.dockerctl
import manager.config


def main():
    threading.Thread(target=api.api.start).start()
    data.dockerctl.start_database()
    while True:
        run_loop()


def run_loop():
    parsed_yaml = manager.config.get_config()
    manager.config.run_modules(parsed_yaml)
    time.sleep(parsed_yaml["Manager"]["UpdatePeriod"])
    files_in_directory = os.listdir(".")
    filtered_files = [file for file in files_in_directory if file.endswith(".lck")]
    for file in filtered_files:
        path_to_file = os.path.join(".", file)
        os.remove(path_to_file)


if __name__ == "__main__":
    main()
