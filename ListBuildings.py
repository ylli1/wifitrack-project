# This file is used to list all the buildings in Parkville that appear in the dataset.

import os
import json
from GeoInfo import buildlocationdict
from BuildingName import buildnamedict

Parkville = []
buildings = []

filePath = 'split/'
dic = (os.listdir(filePath))
for filename in dic:
    with open(filePath+filename) as f:
        a = f.readlines()
        for line in a:
            data = json.loads(line)
            if data["building"] not in buildings:
                buildings.append(data["building"])
            if data["campus"] == "Parkville Indoor":
                if data["building"] not in Parkville:
                    Parkville.append(data["building"])
    f.close()

print("all:", len(buildings))
print("Parkville:", len(Parkville))
for building in Parkville:
    print(building)
