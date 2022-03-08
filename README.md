# ScrapeYard

A modular framework for querying novel data endpoints, sending the data to either splunk or elasticsearch
and managing them with simple YAML configurations. Designed with simplicity in mind, while keeping in mind 
that different endpoints may require different "craziness" in order to work. Modules may be as complex as
needed without impact overall framework simplicity. 




## YAML breakdown

```
Manager:
  UpdatePeriod: 300     --- How often the YAML is re-read for configuration changes.
Modules:
  Ingest:               --- Modules (placed inside the "ingest" directory) that get run
    - LiveMap
    - PowerOutage
  Output:               --- Modules (placed inside the "output" directory) that get run
    - Splunk
    - Elasticsearch
Databases:              --- Database information. Redis and mongodb are both required.
  Redis:
    Host: '127.0.0.1'
    Port: '6379'
    Credentials: 'username:password'
  Mongodb:
    Host: '127.0.0.1'
    Port: '27019'
    Credentials: 'username:password'
```


## Minimum required code for a module
```
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
        if not exists("ingest.MODULE_NAME.lck"):
            break


def get_data():
    print("PO test")
```

## Sample Code Dissected:
 - ``` QueryTime = 10```
   - The time in seconds between each loop
 - ```def __init__():```
   - The function that is called by the manager. Is required for the module to be properly called.
 - ``` n = QueryTime```
   - Sets the counter to "QueryTime" in order to run once before reseting the counter to zero and starting the loop
 - ``` if not exists("ingest.MODULE_NAME.lck"): ```
   - Looks for the setting update file. If it does not exist, exit out of the module. 