import time
from os.path import exists

# Query Time - in seconds #
QueryTime = 10

def __init__():
    n = QueryTime
    while True:
        if n >= QueryTime:
            n = 0
            get_data()
        time.sleep(1)
        n += 1
        if not exists("ingest.PowerOutage.lck"):
            break


def get_data():
    print("PO test")

