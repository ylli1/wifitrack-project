# This is the main file of our server. Run this file to start the server.

from flask import Flask, render_template, jsonify, request
import os
import json
from GeoInfo import buildlocationdict
from BuildingName import buildnamedict



careerdict = {}
with open("reer") as f:
    a = f.readlines()
    for line in a:
        data = json.loads(line)
        careerdict[data["hmacaddress"]] = data["career"]
f.close()

devicedict = {}
with open("results/device_dict") as f:
    a = f.readlines()
    for line in a:
        data = json.loads(line)
        devicedict[data["hmacaddress"]] = data["device"]
f.close()

print("Read.")



app = Flask(__name__)



@app.route('/')
def start():
    return render_template("test_api.html")



def GetPeopleDistribution(time_s):
    error_cnt = 0
    results = {}
    time_max = int(time_s)
    if int(time_s[4:]) < 200:
        time_min = time_max - 7800
    else:
        time_min = time_max - 200

    temp = {}
    i = time_max
    while i > time_min:
        try:
            filePath = "PerMinute/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in temp and data["hmacaddress"] in careerdict:
                        temp[data["hmacaddress"]] = data["building"]
        except:
            error_cnt += 1
        i -= 1

    for mac in temp:
        if temp[mac] in buildlocationdict:
            if temp[mac] not in results:
                results[temp[mac]] = {}
                results[temp[mac]]["type"] = "Feature"
                results[temp[mac]]["geometry"] = {}
                results[temp[mac]]["geometry"]["type"] = "Point"
                cds = buildlocationdict[temp[mac]]
                results[temp[mac]]["geometry"]["coordinates"] = [cds[1], cds[0]]
                results[temp[mac]]["properties"] = {}
                results[temp[mac]]["properties"]["building_name"] = buildnamedict[temp[mac]]
                results[temp[mac]]["properties"]["detail"] = {}
                results[temp[mac]]["properties"]["detail"]["student"] = 0
                results[temp[mac]]["properties"]["detail"]["staff"] = 0
                results[temp[mac]]["properties"]["total"] = 0
                                
            if careerdict[mac] == "student":
                results[temp[mac]]["properties"]["detail"]["student"] += 1
                results[temp[mac]]["properties"]["total"] += 1
            elif careerdict[mac] == "staff":
                results[temp[mac]]["properties"]["detail"]["staff"] += 1
                results[temp[mac]]["properties"]["total"] += 1

    print("building,  student,  staff,  total")
    for building in results:
        print(results[building]["properties"]["building_name"],results[building]["properties"]["detail"]["student"],
            results[building]["properties"]["detail"]["staff"],results[building]["properties"]["total"])

    return results

def GetDeviceDistribution(time_s):
    error_cnt = 0
    results = {}
    time_max = int(time_s)
    if int(time_s[4:]) < 200:
        time_min = time_max - 7800
    else:
        time_min = time_max - 200

    temp = {}
    i = time_max
    while i > time_min:
        try:
            filePath = "PerMinute/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in temp and data["hmacaddress"] in devicedict:
                        temp[data["hmacaddress"]] = data["building"]
        except:
            error_cnt += 1
        i -= 1

    for mac in temp:
        if temp[mac] in buildlocationdict:
            if temp[mac] not in results:
                results[temp[mac]] = {}
                results[temp[mac]]["type"] = "Feature"
                results[temp[mac]]["geometry"] = {}
                results[temp[mac]]["geometry"]["type"] = "Point"
                cds = buildlocationdict[temp[mac]]
                results[temp[mac]]["geometry"]["coordinates"] = [cds[1], cds[0]]
                results[temp[mac]]["properties"] = {}
                results[temp[mac]]["properties"]["building_name"] = buildnamedict[temp[mac]]
                results[temp[mac]]["properties"]["detail"] = {}
                results[temp[mac]]["properties"]["detail"]["PC"] = 0
                results[temp[mac]]["properties"]["detail"]["laptop"] = 0
                results[temp[mac]]["properties"]["detail"]["mobile"] = 0
                results[temp[mac]]["properties"]["total"] = 0
                                
            if devicedict[mac] == "laptop":
                results[temp[mac]]["properties"]["detail"]["laptop"] += 1
                results[temp[mac]]["properties"]["total"] += 1
            elif devicedict[mac] == "mobile":
                results[temp[mac]]["properties"]["detail"]["mobile"] += 1
                results[temp[mac]]["properties"]["total"] += 1
            else:
                results[temp[mac]]["properties"]["detail"]["PC"] += 1
                results[temp[mac]]["properties"]["total"] += 1

    print("building,  laptop,  mobile,  PC,  total")
    for building in results:
        print(results[building]["properties"]["building_name"],results[building]["properties"]["detail"]["laptop"],
            results[building]["properties"]["detail"]["mobile"],results[building]["properties"]["detail"]["PC"],
            results[building]["properties"]["total"])

    return results


def GetPathsTo(bn, st, et):
    error_cnt = 0
    results = {}
    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num
    start_time = int(st)
    end_time = int(et)

    if int(st[4:]) < 200:
        time_min = start_time - 7800
    else:
        time_min = start_time - 200
    i = start_time
    macs = {}
    total = 0

    while i > time_min:
        try:
            filePath = "PerMinute/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in macs:
                        macs[data["hmacaddress"]] = 0
                        if data["building"] == building_no:
                            macs[data["hmacaddress"]] = 1
                            total += 1
            f.close()
        except:
            error_cnt += 1
        i -= 1

    results[0] = {}
    results[0]["type"] = "Feature"
    results[0]["geometry"] = {}
    results[0]["geometry"]["type"] = "Point"
    cds = buildlocationdict[building_no]
    results[0]["geometry"]["coordinates"] = [cds[1], cds[0]]
    results[0]["properties"] = {}
    results[0]["properties"]["building_type"] = "start"
    results[0]["properties"]["building_name"] = bn
    results[0]["properties"]["total"] = total

    print("total:", total)

    j = end_time
    cnt_res = {}
    if end_time - start_time <= 200:
        s_time = start_time
    else:
        if int(et[4:]) < 200:
            s_time = end_time - 7800
        else:
            s_time = end_time - 200

    while j > s_time:
        try:
            filePath = "PerMinute/0" + str(j)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] in macs and macs[data["hmacaddress"]] == 1:
                        if data["building"] != building_no:
                            if data["building"] not in cnt_res:
                                cnt_res[data["building"]] = 1
                            else:
                                cnt_res[data["building"]] += 1
                        macs[data["hmacaddress"]] = 0
            f.close()
        except:
            error_cnt += 1
        j -= 1

    sorted_res = sorted(cnt_res.items(), key=lambda item:item[1], reverse=True)

    idx = 1
    for (building, cnt) in sorted_res:
        if building in buildlocationdict and cnt_res[building] >= 5:
            results[idx] = {}
            results[idx]["type"] = "Feature"
            results[idx]["geometry"] = {}
            results[idx]["geometry"]["type"] = "Point"
            cds = buildlocationdict[building]
            results[idx]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[idx]["properties"] = {}
            results[idx]["properties"]["building_type"] = "destination"
            results[idx]["properties"]["building_name"] = buildnamedict[building]
            results[idx]["properties"]["change"] = cnt_res[building]
            idx += 1

            print(buildnamedict[building], cnt_res[building])

    return results


def GetPathFrom(bn, st, et):
    error_cnt = 0
    results = {}
    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num
    start_time = int(st)
    end_time = int(et)

    i = start_time
    macs = {}
    total = 0

    while i > end_time:
        try:
            filePath = "PerMinute/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in macs:
                        macs[data["hmacaddress"]] = 0
                        if data["building"] == building_no:
                            macs[data["hmacaddress"]] = 1
                            total += 1
            f.close()
        except:
            error_cnt += 1
        i -= 1

    results[0] = {}
    results[0]["type"] = "Feature"
    results[0]["geometry"] = {}
    results[0]["geometry"]["type"] = "Point"
    cds = buildlocationdict[building_no]
    results[0]["geometry"]["coordinates"] = [cds[1], cds[0]]
    results[0]["properties"] = {}
    results[0]["properties"]["building_type"] = "start"
    results[0]["properties"]["building_name"] = bn
    results[0]["properties"]["total"] = total
    print("total:", total)

    if int(et[4:]) < 200:
        s_time = end_time - 7800
    else:
        s_time = end_time - 200
    j = end_time
    cnt_res = {}

    while j > s_time:
        try:
            filePath = "PerMinute/0" + str(j)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] in macs and macs[data["hmacaddress"]] == 1:
                        if data["building"] != building_no:
                            if data["building"] not in cnt_res:
                                cnt_res[data["building"]] = 1
                            else:
                                cnt_res[data["building"]] += 1
                        macs[data["hmacaddress"]] = 0
            f.close()
        except:
            error_cnt += 1
        j -= 1

    sorted_res = sorted(cnt_res.items(), key=lambda item:item[1], reverse=True)

    idx = 1
    for (building, cnt) in sorted_res:
        if building in buildlocationdict and cnt_res[building] >= 5:
            results[idx] = {}
            results[idx]["type"] = "Feature"
            results[idx]["geometry"] = {}
            results[idx]["geometry"]["type"] = "Point"
            cds = buildlocationdict[building]
            results[idx]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[idx]["properties"] = {}
            results[idx]["properties"]["building_type"] = "destination"
            results[idx]["properties"]["building_name"] = buildnamedict[building]
            results[idx]["properties"]["change"] = cnt_res[building]
            idx += 1

            print(buildnamedict[building], cnt_res[building])

    return results


@app.route('/users/', methods=['POST'])
def add_user():
    map_type = request.json["mapType"]

    if map_type == "people":
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        geojson = GetPeopleDistribution(t)

    elif map_type == "path":
        building_name = request.json["building"]
        start_time = request.json["pathStartTime"]
        end_time = request.json["pathEndTime"]
        st = start_time[5:7] + start_time[8:10] + start_time[11:13] + start_time[14:16]
        et = end_time[5:7] + end_time[8:10] + end_time[11:13] + end_time[14:16]
        if int(st) <= int(et):
            geojson = GetPathsTo(building_name, st, et)
        else:
            geojson = GetPathsFrom(building_name, st, et)

    else:
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        geojson = GetDeviceDistribution(t)

    return json.dumps(geojson), 201



if __name__ == '__main__':
    app.run(debug=True)
