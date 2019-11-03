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

        if building_name == "Melbourne Law School" and st == "05170900" and et == "05171000":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960075, -37.802353]}, "properties": {"building_type": "start", "building_name": "Melbourne Law School", "total": 1370}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958826, -37.801584]}, "properties": {"building_type": "destination", "building_name": "The Spot", "change": 24}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959335, -37.801354]}, "properties": {"building_type": "destination", "building_name": "Business and Economics", "change": 17}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960813, -37.80394]}, "properties": {"building_type": "destination", "building_name": "Kwong Lee Dow Building", "change": 9}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959885, -37.803783]}, "properties": {"building_type": "destination", "building_name": "11 Barry Street", "change": 9}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960854, -37.803687]}, "properties": {"building_type": "destination", "building_name": "Melbourne Graduate School of Education", "change": 8}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.800175]}, "properties": {"building_type": "destination", "building_name": "Alan Gilbert Building", "change": 6}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958044, -37.800534]}, "properties": {"building_type": "destination", "building_name": "766 Elizabeth Street", "change": 5}}, "8": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961895, -37.802067]}, "properties": {"building_type": "destination", "building_name": "Building 249", "change": 5}}}
        elif building_name == "Melbourne Law School" and st == "05171500" and et == "05171600":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960075, -37.802353]}, "properties": {"building_type": "start", "building_name": "Melbourne Law School", "total": 4374}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958826, -37.801584]}, "properties": {"building_type": "destination", "building_name": "The Spot", "change": 100}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959335, -37.801354]}, "properties": {"building_type": "destination", "building_name": "Business and Economics", "change": 76}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960813, -37.80394]}, "properties": {"building_type": "destination", "building_name": "Kwong Lee Dow Building", "change": 36}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960854, -37.803687]}, "properties": {"building_type": "destination", "building_name": "Melbourne Graduate School of Education", "change": 20}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961188, -37.798871]}, "properties": {"building_type": "destination", "building_name": "Electrical and Electronic Engineering", "change": 19}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959885, -37.803783]}, "properties": {"building_type": "destination", "building_name": "11 Barry Street", "change": 18}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959432, -37.801471]}, "properties": {"building_type": "destination", "building_name": "Building 326", "change": 16}}, "8": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961895, -37.802067]}, "properties": {"building_type": "destination", "building_name": "Building 249", "change": 13}}, "9": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962754, -37.796739]}, "properties": {"building_type": "destination", "building_name": "Redmond Barry Building", "change": 12}}, "10": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958458, -37.79871]}, "properties": {"building_type": "destination", "building_name": "Old Microbiology", "change": 8}}, "11": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963735, -37.798047]}, "properties": {"building_type": "destination", "building_name": "Peter Hall Building", "change": 8}}, "12": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960115, -37.797765]}, "properties": {"building_type": "destination", "building_name": "Old Arts", "change": 8}}, "13": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963962, -37.798948]}, "properties": {"building_type": "destination", "building_name": "Sidney Myer Asia Centre", "change": 8}}, "14": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963737, -37.803836]}, "properties": {"building_type": "destination", "building_name": "Building 246", "change": 7}}, "15": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961581, -37.79901]}, "properties": {"building_type": "destination", "building_name": "Old Metallurgy", "change": 7}}, "16": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.965548, -37.801704]}, "properties": {"building_type": "destination", "building_name": "Building 385", "change": 7}}, "17": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958899, -37.79946]}, "properties": {"building_type": "destination", "building_name": "Medical Building", "change": 7}}, "18": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959486, -37.798974]}, "properties": {"building_type": "destination", "building_name": "Brownless Biomedical Library", "change": 7}}, "19": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.964019, -37.796879]}, "properties": {"building_type": "destination", "building_name": "David Caro", "change": 7}}, "20": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962672, -37.797286]}, "properties": {"building_type": "destination", "building_name": "Glyn Davis Building", "change": 7}}, "21": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959524, -37.797642]}, "properties": {"building_type": "destination", "building_name": "Arts West - North Wing", "change": 7}}, "22": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958918, -37.801033]}, "properties": {"building_type": "destination", "building_name": "General Practice and Melbourne School of Health Sciences", "change": 7}}, "23": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959364, -37.798489]}, "properties": {"building_type": "destination", "building_name": "Baillieu Library", "change": 6}}, "24": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959589, -37.797255]}, "properties": {"building_type": "destination", "building_name": "Babel", "change": 5}}, "25": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.800175]}, "properties": {"building_type": "destination", "building_name": "Alan Gilbert Building", "change": 5}}, "26": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958554, -37.798268]}, "properties": {"building_type": "destination", "building_name": "Kenneth Myer Building", "change": 5}}}

        elif building_name == "Melbourne Law School" and st == "05172000" and et == "05172100":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960075, -37.802353]}, "properties": {"building_type": "start", "building_name": "Melbourne Law School", "total": 2261}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959885, -37.803783]}, "properties": {"building_type": "destination", "building_name": "11 Barry Street", "change": 18}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960854, -37.803687]}, "properties": {"building_type": "destination", "building_name": "Melbourne Graduate School of Education", "change": 12}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960813, -37.80394]}, "properties": {"building_type": "destination", "building_name": "Kwong Lee Dow Building", "change": 11}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959335, -37.801354]}, "properties": {"building_type": "destination", "building_name": "Business and Economics", "change": 11}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958826, -37.801584]}, "properties": {"building_type": "destination", "building_name": "The Spot", "change": 8}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963808, -37.799944]}, "properties": {"building_type": "destination", "building_name": "757 Swanston", "change": 6}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963152, -37.803548]}, "properties": {"building_type": "destination", "building_name": "Lincoln Square Building B", "change": 5}}}
        elif building_name == "Union House" and st == "05231200" and et == "05231100":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96098, -37.796912]}, "properties": {"building_type": "start", "building_name": "Union House", "total": 1431}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962672, -37.797286]}, "properties": {"building_type": "destination", "building_name": "Glyn Davis Building", "change": 47}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959364, -37.798489]}, "properties": {"building_type": "destination", "building_name": "Baillieu Library", "change": 38}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959524, -37.797642]}, "properties": {"building_type": "destination", "building_name": "Arts West - North Wing", "change": 31}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962156, -37.79797]}, "properties": {"building_type": "destination", "building_name": "Chemistry", "change": 26}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963962, -37.798948]}, "properties": {"building_type": "destination", "building_name": "Sidney Myer Asia Centre", "change": 24}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962754, -37.796739]}, "properties": {"building_type": "destination", "building_name": "Redmond Barry Building", "change": 20}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963735, -37.798047]}, "properties": {"building_type": "destination", "building_name": "Peter Hall Building", "change": 18}}, "8": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.797785]}, "properties": {"building_type": "destination", "building_name": "Arts West - West Wing", "change": 18}}, "9": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962865, -37.799342]}, "properties": {"building_type": "destination", "building_name": "Eastern Resource Centre", "change": 17}}, "10": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960115, -37.797765]}, "properties": {"building_type": "destination", "building_name": "Old Arts", "change": 17}}, "11": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958899, -37.79946]}, "properties": {"building_type": "destination", "building_name": "Medical Building", "change": 17}}, "12": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.964019, -37.796879]}, "properties": {"building_type": "destination", "building_name": "David Caro", "change": 16}}, "13": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959385, -37.796212]}, "properties": {"building_type": "destination", "building_name": "Biosciences 1", "change": 15}}, "14": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958105, -37.79996]}, "properties": {"building_type": "destination", "building_name": "Peter Doherty Institute", "change": 13}}, "15": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961508, -37.799474]}, "properties": {"building_type": "destination", "building_name": "Engineering Block A", "change": 12}}, "16": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960636, -37.796016]}, "properties": {"building_type": "destination", "building_name": "Beaurepaire Centre", "change": 12}}, "17": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958826, -37.801584]}, "properties": {"building_type": "destination", "building_name": "The Spot", "change": 11}}, "18": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960589, -37.797353]}, "properties": {"building_type": "destination", "building_name": "Old Physics", "change": 8}}, "19": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962965, -37.797897]}, "properties": {"building_type": "destination", "building_name": "Old Geology", "change": 8}}, "20": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960072, -37.796317]}, "properties": {"building_type": "destination", "building_name": "University House", "change": 8}}, "21": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960075, -37.802353]}, "properties": {"building_type": "destination", "building_name": "Melbourne Law School", "change": 7}}, "22": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961654, -37.797485]}, "properties": {"building_type": "destination", "building_name": "Raymond Priestley", "change": 7}}, "23": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958918, -37.801033]}, "properties": {"building_type": "destination", "building_name": "General Practice and Melbourne School of Health Sciences", "change": 7}}, "24": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96339, -37.797432]}, "properties": {"building_type": "destination", "building_name": "Elisabeth Murdoch", "change": 7}}, "25": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.800175]}, "properties": {"building_type": "destination", "building_name": "Alan Gilbert Building", "change": 7}}, "26": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960683, -37.799267]}, "properties": {"building_type": "destination", "building_name": "John Medley", "change": 7}}, "27": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960852, -37.799822]}, "properties": {"building_type": "destination", "building_name": "Engineering Block B", "change": 6}}, "28": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963482, -37.798621]}, "properties": {"building_type": "destination", "building_name": "Alice Hoy", "change": 6}}, "29": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959589, -37.797255]}, "properties": {"building_type": "destination", "building_name": "Babel", "change": 6}}, "30": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959486, -37.798974]}, "properties": {"building_type": "destination", "building_name": "Brownless Biomedical Library", "change": 5}}, "31": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961581, -37.79901]}, "properties": {"building_type": "destination", "building_name": "Old Metallurgy", "change": 5}}}

        elif building_name == "Redmond Barry Building" and st == "05081000" and et == "05081100":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962754, -37.796739]}, "properties": {"building_type": "start", "building_name": "Redmond Barry Building", "total": 1384}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962672, -37.797286]}, "properties": {"building_type": "destination", "building_name": "Glyn Davis Building", "change": 84}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96098, -37.796912]}, "properties": {"building_type": "destination", "building_name": "Union House", "change": 42}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959364, -37.798489]}, "properties": {"building_type": "destination", "building_name": "Baillieu Library", "change": 31}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.964019, -37.796879]}, "properties": {"building_type": "destination", "building_name": "David Caro", "change": 31}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963735, -37.798047]}, "properties": {"building_type": "destination", "building_name": "Peter Hall Building", "change": 23}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96194, -37.801349]}, "properties": {"building_type": "destination", "building_name": "207-221 Bouverie Street", "change": 20}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.797785]}, "properties": {"building_type": "destination", "building_name": "Arts West - West Wing", "change": 18}}, "8": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963962, -37.798948]}, "properties": {"building_type": "destination", "building_name": "Sidney Myer Asia Centre", "change": 18}}, "9": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962156, -37.79797]}, "properties": {"building_type": "destination", "building_name": "Chemistry", "change": 15}}, "10": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959524, -37.797642]}, "properties": {"building_type": "destination", "building_name": "Arts West - North Wing", "change": 14}}, "11": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960115, -37.797765]}, "properties": {"building_type": "destination", "building_name": "Old Arts", "change": 12}}, "12": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962865, -37.799342]}, "properties": {"building_type": "destination", "building_name": "Eastern Resource Centre", "change": 9}}, "13": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.965015, -37.797118]}, "properties": {"building_type": "destination", "building_name": "Earth Sciences", "change": 7}}, "14": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959335, -37.801354]}, "properties": {"building_type": "destination", "building_name": "Business and Economics", "change": 6}}, "15": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961508, -37.799474]}, "properties": {"building_type": "destination", "building_name": "Engineering Block A", "change": 6}}, "16": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960636, -37.796016]}, "properties": {"building_type": "destination", "building_name": "Beaurepaire Centre", "change": 5}}, "17": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959385, -37.796212]}, "properties": {"building_type": "destination", "building_name": "Biosciences 1", "change": 5}}}

        elif building_name == "Redmond Barry Building" and st == "05151000" and et == "05151100":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962754, -37.796739]}, "properties": {"building_type": "start", "building_name": "Redmond Barry Building", "total": 1309}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962672, -37.797286]}, "properties": {"building_type": "destination", "building_name": "Glyn Davis Building", "change": 81}}, "2": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96098, -37.796912]}, "properties": {"building_type": "destination", "building_name": "Union House", "change": 40}}, "3": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.964019, -37.796879]}, "properties": {"building_type": "destination", "building_name": "David Caro", "change": 31}}, "4": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963735, -37.798047]}, "properties": {"building_type": "destination", "building_name": "Peter Hall Building", "change": 26}}, "5": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959275, -37.797785]}, "properties": {"building_type": "destination", "building_name": "Arts West - West Wing", "change": 20}}, "6": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959364, -37.798489]}, "properties": {"building_type": "destination", "building_name": "Baillieu Library", "change": 17}}, "7": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963962, -37.798948]}, "properties": {"building_type": "destination", "building_name": "Sidney Myer Asia Centre", "change": 17}}, "8": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962865, -37.799342]}, "properties": {"building_type": "destination", "building_name": "Eastern Resource Centre", "change": 10}}, "9": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959486, -37.798974]}, "properties": {"building_type": "destination", "building_name": "Brownless Biomedical Library", "change": 10}}, "10": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.959524, -37.797642]}, "properties": {"building_type": "destination", "building_name": "Arts West - North Wing", "change": 10}}, "11": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962156, -37.79797]}, "properties": {"building_type": "destination", "building_name": "Chemistry", "change": 9}}, "12": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960115, -37.797765]}, "properties": {"building_type": "destination", "building_name": "Old Arts", "change": 8}}, "13": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.963808, -37.799944]}, "properties": {"building_type": "destination", "building_name": "757 Swanston", "change": 7}}, "14": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.965015, -37.797118]}, "properties": {"building_type": "destination", "building_name": "Earth Sciences", "change": 6}}, "15": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962031, -37.796538]}, "properties": {"building_type": "destination", "building_name": "Baldwin Spencer Building", "change": 6}}, "16": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961654, -37.797485]}, "properties": {"building_type": "destination", "building_name": "Raymond Priestley", "change": 6}}, "17": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.961508, -37.799474]}, "properties": {"building_type": "destination", "building_name": "Engineering Block A", "change": 6}}, "18": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962965, -37.797897]}, "properties": {"building_type": "destination", "building_name": "Old Geology", "change": 6}}, "19": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.958899, -37.79946]}, "properties": {"building_type": "destination", "building_name": "Medical Building", "change": 5}}, "20": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.960636, -37.796016]}, "properties": {"building_type": "destination", "building_name": "Beaurepaire Centre", "change": 5}}}

        elif building_name == "Redmond Barry Building" and st == "06121000" and et == "06121100":
            gj = {"0": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.962754, -37.796739]}, "properties": {"building_type": "start", "building_name": "Redmond Barry Building", "total": 359}}, "1": {"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.964019, -37.796879]}, "properties": {"building_type": "destination", "building_name": "David Caro", "change": 8}}}


    else:
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        if (int(t) < 5182500 and int(t) >= 5100200) or (int(t) < 6192500 and int(t) >= 6160200):
            geojson = GetDeviceDistribution2(t)
        else:
            geojson = GetDeviceDistribution(t)

    return json.dumps(gj), 201


if __name__ == '__main__':
    app.run(debug=True)
