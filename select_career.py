import os
import json
from collections import defaultdict

time='04301408'

careerjs = defaultdict(defaultdict)

dic = (os.listdir("test"))
with open("test/"+time) as f:
    a = f.readlines()
    mc=[]
    bd=[]
    for line in a:
        data = json.loads(line)
        bd.append(data["building"])

        mc.append(data["hmacaddress"])
    f.close()


with open("reer.json") as f:
    a = f.readlines()
    reer=[]
    for line in a:
        data = json.loads(line)
        for i in range(len(mc)):
            if mc[i]==data["hmacaddress"]:
                print(data["career"])
                if data["career"] == "staff":

                    reer.append(0)
                else:

                    reer.append(1)
            else:
                reer.append(1)
    f.close()

for i in range(0,len(bd)):
    if bd[i] in careerjs:
        if reer[i]==0:
            careerjs[bd[i]]["staff"] +=1
        else:
            careerjs[bd[i]]["student"] += 1
    else:
        careerjs[bd[i]]["staff"]=0
        careerjs[bd[i]]["student"] = 0

        if reer[i]==0:
            careerjs[bd[i]]["staff"] +=1
        else:
            careerjs[bd[i]]["student"] += 1

# print(careerjs)
# print(len(careerjs))








