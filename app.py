from flask import Flask, render_template, jsonify, request
import os
import json
import sqlite3
from GeoInfo import buildlocationdict
from BuildingName import buildnamedict


app = Flask(__name__)


@app.route('/')
def start():
    return render_template("test_api.html")


def GetPeopleDistribution(time_s):
    conn = sqlite3.connect('DB3.sqlite')

    results = {}
    time_max = int(time_s)
    if int(time_s[4:]) < 200:
        time_min = time_max - 7800
    else:
        time_min = time_max - 200

    c = conn.execute(
        "SELECT building, career, count(*) FROM BInT LEFT OUTER JOIN Career on BInT.mac = Career.mac WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? GROUP BY building, career",
        (time_min, time_max))

    for row in c:
        if row[0] in buildlocationdict:
            if row[0] not in results:
                results[row[0]] = {}
                results[row[0]]["type"] = "Feature"
                results[row[0]]["geometry"] = {}
                results[row[0]]["geometry"]["type"] = "Point"
                cds = buildlocationdict[row[0]]
                results[row[0]]["geometry"]["coordinates"] = [cds[1], cds[0]]
                results[row[0]]["properties"] = {}
                results[row[0]]["properties"]["building_name"] = buildnamedict[row[0]]
                results[row[0]]["properties"]["detail"] = {}
                results[row[0]]["properties"]["detail"]["student"] = 0
                results[row[0]]["properties"]["detail"]["staff"] = 0
                results[row[0]]["properties"]["total"] = 0

            if row[1] == "student":
                results[row[0]]["properties"]["detail"]["student"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            elif row[1] == "staff":
                results[row[0]]["properties"]["detail"]["staff"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]

    conn.close()

    return results


def GetDeviceDistribution(time_s):
    conn = sqlite3.connect('DB3.sqlite')

    results = {}
    time_max = int(time_s)
    if int(time_s[4:]) < 200:
        time_min = time_max - 7800
    else:
        time_min = time_max - 200

    c = conn.execute(
        "SELECT building, device, count(*) FROM BInT LEFT OUTER JOIN Device on BInT.mac = Device.mac WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? GROUP BY building, device",
        (time_min, time_max))

    for row in c:
        if row[0] in buildlocationdict:
            if row[0] not in results:
                results[row[0]] = {}
                results[row[0]]["type"] = "Feature"
                results[row[0]]["geometry"] = {}
                results[row[0]]["geometry"]["type"] = "Point"
                cds = buildlocationdict[row[0]]
                results[row[0]]["geometry"]["coordinates"] = [cds[1], cds[0]]
                results[row[0]]["properties"] = {}
                results[row[0]]["properties"]["building_name"] = buildnamedict[row[0]]
                results[row[0]]["properties"]["detail"] = {}
                results[row[0]]["properties"]["detail"]["PC"] = 0
                results[row[0]]["properties"]["detail"]["mobile"] = 0
                results[row[0]]["properties"]["detail"]["laptop"] = 0
                results[row[0]]["properties"]["total"] = 0

            if row[1] == "PC":
                results[row[0]]["properties"]["detail"]["PC"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            elif row[1] == "laptop":
                results[row[0]]["properties"]["detail"]["laptop"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            elif row[1] == "mobile":
                results[row[0]]["properties"]["detail"]["mobile"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]

    conn.close()

    return results


def GetPaths(bn, st, et):
    conn = sqlite3.connect('DB3.sqlite')

    results = {}
    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num
    start_time = int(st)
    end_time = int(et)

    if end_time - start_time < 0:
        time_min = end_time
    elif int(st[4:]) < 200:
        time_min = start_time - 7800
    else:
        time_min = start_time - 200

    c1 = conn.execute(
        "SELECT mac, building FROM BInT WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? AND building = ? ORDER BY tm DESC",
        (time_min, start_time, building_no))

    start_macs = set()
    for row in c1:
        start_macs.add(row[0])

    results[0] = {}
    results[0]["type"] = "Feature"
    results[0]["geometry"] = {}
    results[0]["geometry"]["type"] = "Point"
    cds = buildlocationdict[building_no]
    results[0]["geometry"]["coordinates"] = [cds[1], cds[0]]
    results[0]["properties"] = {}
    results[0]["properties"]["building_type"] = "start"
    results[0]["properties"]["building_name"] = bn
    results[0]["properties"]["total"] = len(start_macs)

    if end_time - start_time <= 200 and end_time - start_time >= 0:
        s_time = start_time
    else:
        if int(et[4:]) < 200:
            s_time = end_time - 7800
        else:
            s_time = end_time - 200

    c2 = conn.execute(
        "SELECT mac, building FROM BInT WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? ORDER BY tm DESC",
        (s_time, end_time))

    end_cnts = {}
    for row in c2:
        if (row[0] in start_macs) and (row[1] != building_no):
            if row[1] in end_cnts:
                end_cnts[row[1]] += 1
            else:
                end_cnts[row[1]] = 1
            # start_macs.discard(row[0])

    for building in end_cnts:
        if building in buildlocationdict:
            results[building] = {}
            results[building]["type"] = "Feature"
            results[building]["geometry"] = {}
            results[building]["geometry"]["type"] = "Point"
            cds = buildlocationdict[building]
            results[building]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[building]["properties"] = {}
            results[building]["properties"]["building_type"] = "destination"
            results[building]["properties"]["building_name"] = buildnamedict[building]
            results[building]["properties"]["change"] = end_cnts[building]

    conn.close()

    return results


def GetPeopleDistribution2(time_s):
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
            filePath = "/Users/jiangchangda/Desktop/COMP90019-Project/Presentation/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in temp and data["career"] != "None" and data[
                        "building"] in buildlocationdict:
                        temp[data["hmacaddress"]] = [data["building"], data["career"]]
            f.close()
        except:
            error_cnt += 1
        i -= 1


    for mac in temp:
        if temp[mac][0] not in results:
            results[temp[mac][0]] = {}
            results[temp[mac][0]]["type"] = "Feature"
            results[temp[mac][0]]["geometry"] = {}
            results[temp[mac][0]]["geometry"]["type"] = "Point"
            cds = buildlocationdict[temp[mac][0]]
            results[temp[mac][0]]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[temp[mac][0]]["properties"] = {}
            results[temp[mac][0]]["properties"]["building_name"] = buildnamedict[temp[mac][0]]
            results[temp[mac][0]]["properties"]["detail"] = {}
            results[temp[mac][0]]["properties"]["detail"]["student"] = 0
            results[temp[mac][0]]["properties"]["detail"]["staff"] = 0
            results[temp[mac][0]]["properties"]["total"] = 0

        if temp[mac][1] == "student":
            results[temp[mac][0]]["properties"]["detail"]["student"] += 1
            results[temp[mac][0]]["properties"]["total"] += 1
        else:
            results[temp[mac][0]]["properties"]["detail"]["staff"] += 1
            results[temp[mac][0]]["properties"]["total"] += 1

    return results


def GetDeviceDistribution2(time_s):
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
            filePath = "/Users/jiangchangda/Desktop/COMP90019-Project/Presentation/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] not in temp and data["device"] != "None" and data[
                        "building"] in buildlocationdict:
                        temp[data["hmacaddress"]] = [data["building"], data["device"]]
            f.close()
        except:
            error_cnt += 1
        i -= 1

    for mac in temp:
        if temp[mac][0] not in results:
            results[temp[mac][0]] = {}
            results[temp[mac][0]]["type"] = "Feature"
            results[temp[mac][0]]["geometry"] = {}
            results[temp[mac][0]]["geometry"]["type"] = "Point"
            cds = buildlocationdict[temp[mac][0]]
            results[temp[mac][0]]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[temp[mac][0]]["properties"] = {}
            results[temp[mac][0]]["properties"]["building_name"] = buildnamedict[temp[mac][0]]
            results[temp[mac][0]]["properties"]["detail"] = {}
            results[temp[mac][0]]["properties"]["detail"]["PC"] = 0
            results[temp[mac][0]]["properties"]["detail"]["laptop"] = 0
            results[temp[mac][0]]["properties"]["detail"]["mobile"] = 0
            results[temp[mac][0]]["properties"]["total"] = 0

        if temp[mac][1] == "laptop":
            results[temp[mac][0]]["properties"]["detail"]["laptop"] += 1
            results[temp[mac][0]]["properties"]["total"] += 1
        elif temp[mac][1] == "mobile":
            results[temp[mac][0]]["properties"]["detail"]["mobile"] += 1
            results[temp[mac][0]]["properties"]["total"] += 1
        else:
            results[temp[mac][0]]["properties"]["detail"]["PC"] += 1
            results[temp[mac][0]]["properties"]["total"] += 1

    return results


def GetPaths2(bn, st, et):
    error_cnt = 0
    results = {}
    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num
    start_time = int(st)
    end_time = int(et)

    if end_time - start_time < 0:
        time_min = end_time
    elif int(st[4:]) < 200:
        time_min = start_time - 7800
    else:
        time_min = start_time - 200

    i = start_time
    macs = set()
    while i > time_min:
        try:
            filePath = "/Users/jiangchangda/Desktop/COMP90019-Project/Presentation/0" + str(i)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["building"] == building_no:
                        macs.add(data["hmacaddress"])
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
    results[0]["properties"]["total"] = len(macs)

    j = end_time
    cnt_res = {}
    if end_time - start_time <= 200 and end_time - start_time >= 0:
        s_time = start_time
    else:
        if int(et[4:]) < 200:
            s_time = end_time - 7800
        else:
            s_time = end_time - 200
    while j > s_time:
        try:
            filePath = "/Users/jiangchangda/Desktop/COMP90019-Project/Presentation/0" + str(j)
            with open(filePath) as f:
                a = f.readlines()
                for line in a:
                    data = json.loads(line)
                    if data["hmacaddress"] in macs and data["building"] != building_no:
                        if data["building"] not in cnt_res:
                            cnt_res[data["building"]] = 1
                        else:
                            cnt_res[data["building"]] += 1
                        macs.discard(data["hmacaddress"])
            f.close()
        except:
            error_cnt += 1
        j -= 1

    for building in cnt_res:
        if building in buildlocationdict and cnt_res[building] >= 5:
            results[building] = {}
            results[building]["type"] = "Feature"
            results[building]["geometry"] = {}
            results[building]["geometry"]["type"] = "Point"
            cds = buildlocationdict[building]
            results[building]["geometry"]["coordinates"] = [cds[1], cds[0]]
            results[building]["properties"] = {}
            results[building]["properties"]["building_type"] = "destination"
            results[building]["properties"]["building_name"] = buildnamedict[building]
            results[building]["properties"]["change"] = cnt_res[building]

    return results


@app.route('/users/', methods=['POST'])
def add_user():
    map_type = request.json["mapType"]

    if map_type == "people":
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        if (int(t) < 5182500 and int(t) >= 5100200) or (int(t) < 6192500 and int(t) >= 6160200):
            geojson = GetPeopleDistribution2(t)
        else:
            geojson = GetPeopleDistribution(t)

    elif map_type == "path":
        building_name = request.json["building"]
        start_time = request.json["pathStartTime"]
        end_time = request.json["pathEndTime"]
        st = start_time[5:7] + start_time[8:10] + start_time[11:13] + start_time[14:16]
        et = end_time[5:7] + end_time[8:10] + end_time[11:13] + end_time[14:16]
        if (int(et) < 5182500 and int(st) >= 5100200) or (int(et) < 6192500 and int(st) >= 6160200):
            geojson = GetPaths2(building_name, st, et)
        else:
            geojson = GetPaths(building_name, st, et)

    else:
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        if (int(t) < 5182500 and int(t) >= 5100200) or (int(t) < 6192500 and int(t) >= 6160200):
            geojson = GetDeviceDistribution2(t)
        else:
            geojson = GetDeviceDistribution(t)

    return json.dumps(geojson), 201


if __name__ == '__main__':
    app.run(debug=True)
