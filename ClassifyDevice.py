# Identify whether a mac address is a PC/laptop/mobile
# PC: have more than 5 records, each record has the same hapmacaddress (same router)
# mobile: counts of occurrs in outdoor + move continuously in short time is larger than 5.

import os
import json
import multiprocessing

filePath = 'classify/'

def classify(filename,):
    device_type = ""
    locations = {}
    with open(filePath+filename) as f:
        a = f.readlines()
        hapmacaddress = ""
        pc_flag = 1
        cnt = 0
        outdoor_cnt = 0
        for line in a:
            data = json.loads(line)
            timestamp = int(data["changedon"])
            locations[timestamp] = data["building"]
            cnt += 1
            if hapmacaddress == "":
                hapmacaddress = data["hapmacaddress"]
            elif hapmacaddress != data["hapmacaddress"]:
                pc_flag = 0
            if data["campus"][-7:] == "Outdoor":
                outdoor_cnt += 1
    f.close()

    sorted_locations = sorted(locations)
    prev_timestamp = 0
    prev_location = ""
    continue_cnt = 0
    for timestamp in locations:
        if timestamp - prev_timestamp < 600 and locations[timestamp] != prev_location:
            continue_cnt += 1
        prev_timestamp = timestamp
        prev_location = locations[timestamp]

    if cnt > 5 and outdoor_cnt == 0 and pc_flag == 1:
        device_type = "PC"
    elif (outdoor_cnt + continue_cnt) / cnt >= 0.1:
        device_type = "mobile"
    else:
        device_type = "laptop"

    o = open('results/device_dict', 'a')
    temp = {}
    temp["hmacaddress"] = filename
    temp["device"] = device_type
    temp_json = json.dumps(temp)
    o.write(str(temp_json)+"\n")
    o.close()

pool = multiprocessing.Pool(8)

dic = (os.listdir(filePath))
for file in dic:
    pool.apply_async(classify, (file,))

pool.close()
pool.join()
