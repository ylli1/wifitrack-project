from flask import Flask,render_template,jsonify,request
import sqlite3
import json
from collections import defaultdict
from GeoInfo import buildlocationdict
from BuildingName import buildnamedict


app = Flask(__name__)


@app.route('/')

def start():
    # if request.method == "POST":
    #     username = request.form.get("trip-start")
        # userage = request.div.get("userage")
    return render_template("test_api.html")


def GetPeopleDistribution(time_s):
    conn = sqlite3.connect('DB3.sqlite')

    results = {}
    time_max = int(time_s)
    time_min = time_max - 100

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
    time_min = time_max - 100

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
    time_min = start_time - 200
    end_time = int(et)

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

    c2 = conn.execute(
        "SELECT mac, building FROM BInT WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? ORDER BY tm DESC",
        (start_time, end_time))

    end_cnts = {}
    for row in c2:
        if (row[0] in start_macs) and (row[1] != building_no):
            if row[1] in end_cnts:
                end_cnts[row[1]] += 1
            else:
                end_cnts[row[1]] = 1
            #start_macs.discard(row[0])

    for building in end_cnts:
        results[building] = {}
        results[building]["type"] = "Feature"
        results[building]["geometry"] = {}
        results[building]["geometry"]["type"] = "Point"
        cds = buildlocationdict[building_no]
        results[building]["geometry"]["coordinates"] = [cds[1], cds[0]]
        results[building]["properties"] = {}
        results[building]["properties"]["building_type"] = "destination"
        results[building]["properties"]["building_name"] = buildnamedict[building]
        results[building]["properties"]["change"] = end_cnts[building]

print(results)

    conn.close()

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
        geojson = GetPaths(building_name, st, et)

    else:
        time = request.json["date"]
        t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
        geojson = GetDeviceDistribution(t)

    return  json.dumps(geojson), 201
# json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)
