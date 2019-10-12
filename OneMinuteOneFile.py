import os
import json
import datetime
filePath = 'split/'
dic = (os.listdir(filePath))

for i in range(len(dic)):
    with open(filePath+dic[i]) as f:
        a = f.readlines()
        for line in a:
            data = json.loads(line)
            temp = {}
            #temp["changedon"] = data["changedon"]
            temp["hmacaddress"] = data["hmacaddress"]
            temp["campus"] = data["campus"]
            temp["building"] = data["building"]
            temp["floor"] = data["floor"]
            temp_json = json.dumps(temp)
            temp_line = str(temp_json)+"\n"

            dateArray = datetime.datetime.fromtimestamp(int(data["changedon"]))
            dateStr = str(dateArray)
            filename = dateStr[5:7]+dateStr[8:10]+dateStr[11:13]+dateStr[14:16]

            o = open('PerMinute/'+filename, 'a')
            o.write(temp_line)
            o.close()
    f.close()