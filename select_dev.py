import os
import json
from collections import defaultdict

time='04301408'
devjs = defaultdict(defaultdict)
dic = (os.listdir("test"))
with open("test/"+time) as f: # split file in time
    a = f.readlines()
    mc=[]# store mac address
    bd=[]# store building name
    for line in a:
        data = json.loads(line)
        bd.append(data["building"])
        mc.append(data["hmacaddress"])
    f.close()


with open("device_dict") as f:
    a = f.readlines()
    reer=[]# device list
    for line in a:
        data = json.loads(line)
        for i in range(len(mc)):

            if mc[i]==data["hmacaddress"]:
                print(data["device"])
                if data["device"] == 'mobile':

                    reer.append(0)
                elif data["device"] == "laptop":

                    reer.append(1)
                else:
                    reer.append(2)
    f.close()

for i in range(0,len(bd)):
    if bd[i] in devjs:
        if reer[i]==0:
            devjs[bd[i]]["mobile"] +=1
        elif reer[i]==1:
            devjs[bd[i]]["laptop"] += 1
        else:
            devjs[bd[i]]["PC"] += 1
    else:
        devjs[bd[i]]["mobile"]=0
        devjs[bd[i]]["laptop"] = 0
        devjs[bd[i]]["PC"] = 0

        if reer[i]==0:
            devjs[bd[i]]["mobile"] +=1
        elif reer[i]==1:
            devjs[bd[i]]["laptop"] += 1
        else:
            devjs[bd[i]]["PC"] += 1

print(devjs)
print(len(devjs))








