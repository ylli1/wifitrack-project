# Transfer changedon/timestamp to datetime.
# According to datetime, write each record that belongs to a specific minute to a file named as month+day+hour+minute.

import os
import json
import datetime
import multiprocessing

def perminute(i,):
    with open("split/"+i) as f:
        a = f.readlines()
        for line in a:
            data = json.loads(line)
            temp = {}
            temp["hmacaddress"] = data["hmacaddress"]
            temp["building"] = data["building"]
            temp_json = json.dumps(temp)
            temp_line = str(temp_json)+"\n"

            dateArray = datetime.datetime.fromtimestamp(int(data["changedon"]))
            dateStr = str(dateArray)
            filename = dateStr[5:7]+dateStr[8:10]+dateStr[11:13]+dateStr[14:16]

            with open('PerMinute/'+filename, 'a') as o:
                o.writelines(temp_line)


pool = multiprocessing.Pool(8)

dic = (os.listdir("split"))
for file in dic:
    pool.apply_async(perminute, (file,))

pool.close()
pool.join()
