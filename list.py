import datetime

def time_transfer(timeStamp):
    return datetime.datetime.fromtimestamp(timeStamp)

import os
import json
filePath = 'classify/'
locations = {}
with open (filePath) as f:
    a = f.readlines()
    for line in a:
        data = json.loads(line.replace("'","\""))
        timeStamp = int(data["changedon"])
        locations[timeStamp] = "\t"+data["campus"]+"\t"+data["building"]+"\t"+data["floor"]
sorted_locations = sorted(locations)
for timestamp in sorted_locations:
    print(time_transfer(timestamp),locations[timestamp])