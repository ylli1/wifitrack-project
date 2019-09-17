import os
import json
filePath = 'C:/comproj/mac/'
dic = (os.listdir(filePath))
device_dict = {}
for i in range(len(dic)):
    with open(filePath+dic[i]) as f:
        a = f.readlines()
        hapmacaddress = ""
        pc_flag = 1
        outdoor_cnt = 0
        for line in a:
            data = json.loads(line)
            if hapmacaddress == "":
                hapmacaddress = data["hapmacaddress"]
            elif hapmacaddress != data["hapmacaddress"]:
                pc_flag = 0
            if data["campus"][-7:] == "Outdoor":
                outdoor_cnt += 1
        if outdoor_cnt == 0 and pc_flag == 1:
            device_dict[dic[i]] = "PC"
        elif outdoor_cnt != 0:
            device_dict[dic[i]] = "mobile"
        else:
            device_dict[dic[i]] = "laptop"
f.close()
o = open('device_dict', 'a')
addresses = device_dict.keys()
for address in addresses:
    temp = {}
    temp["hmacaddress"] = address
    temp["device"] = device_dict[address]
    temp_json = json.dumps(temp)
    o.write(str(temp_json)+"\n")
o.close()
