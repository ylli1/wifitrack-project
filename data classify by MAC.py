import os
import json
res = {}
i = 0
j = 0
filename = []
filePath = 'test_class/'
dic = (os.listdir(filePath))
# print(dic)
# print(dic[0])
while i < len(dic):
    with open (filePath+dic[i]) as f:
        a = f.readlines()
        for line in a:
            data = json.loads(line)
            thisMac = data["hmacaddress"]
            temp = {}
            temp["changedon"] = data["changedon"]
            temp["hapmacaddress"] = data["hapmacaddress"]
            temp["campus"] = data["campus"]
            temp["building"] = data["building"]
            temp["floor"] = data["floor"]
            temp_json = json.dumps(temp)
            temp_line = str(temp_json)+"\n"
            if thisMac in res:
                res[thisMac].append(temp_line)
            else:
                res[thisMac] = [temp_line]
                filename.append(thisMac)
    # linecount = 1
    while j < len(filename):
        for lines in res.values():
            o = open('classified/'+str(filename[j]), 'a')
            for line in lines:
                o.write(line)
            # linecount += 1
            o.close()
            j = j+1
    j = 0
    i = i+1
    filename.clear()
    res.clear()
