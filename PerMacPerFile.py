# Write each record that belongs to a specific mac address to a file named as the mac address.

import os
import json
import multiprocessing

def permac(i,):
    with open("split/"+i) as f:
        a = f.readlines()
        for line in a:
            data = json.loads(line)
            thisMac = data["hmacaddress"]
            temp = {}
            temp["changedon"] = data["changedon"]
            temp["hapmacaddress"] = data["hapmacaddress"]
            temp["building"] = data["building"]
            temp_json = json.dumps(temp)
            temp_line = str(temp_json)+"\n"

            with open('classify/'+thisMac, 'a') as o:
                o.writelines(temp_line)


pool = multiprocessing.Pool(8)

dic = (os.listdir("split"))
for file in dic:
    pool.apply_async(permac, (file,))

pool.close()
pool.join()
