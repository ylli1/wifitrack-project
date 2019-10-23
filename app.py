from flask import Flask,render_template,jsonify,request
import sqlite3
import json
from collections import defaultdict
from GeoInfo import buildlocationdict


app = Flask(__name__)


@app.route('/')

def start():
    # if request.method == "POST":
    #     username = request.form.get("trip-start")
        # userage = request.div.get("userage")
    return render_template("test_api.html")



def GetPeopleDistribution(time_s):
    # time_s = "06301327"
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
                results[row[0]]["properties"]["building_name"] =row[0]
                results[row[0]]["properties"]["Student"] = 0
                results[row[0]]["properties"]["Staff"] = 0
                results[row[0]]["properties"]["total"] = 0

            if row[1] == "student":
                results[row[0]]["properties"]["Student"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            elif row[1] == "staff":
                results[row[0]]["properties"]["Staff"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]

    conn.close()

    return results

def GetDeviceDistribution(time_s):
    # time_s = "06301327"
    conn = sqlite3.connect('DB3.sqlite')

    results = {}
    time_max = int(time_s)
    time_min = time_max - 100

    c = conn.execute(
        "SELECT building, device, count(*) FROM BInT LEFT OUTER JOIN Device on BInT.mac = Career.mac WHERE CAST(tm as int) > ? AND CAST(tm as int) <= ? GROUP BY building, device",
        (time_min, time_max))
    for row in c:
        print(row[0])
        print(row[1])
        if row[0] in buildlocationdict:
            if row[0] not in results:
                results[row[0]] = {}
                results[row[0]]["type"] = "Feature"
                results[row[0]]["geometry"] = {}
                results[row[0]]["geometry"]["type"] = "Point"
                cds = buildlocationdict[row[0]]
                results[row[0]]["geometry"]["coordinates"] = [cds[1], cds[0]]
                results[row[0]]["properties"] = {}
                results[row[0]]["properties"]["building_name"] =row[0]
                results[row[0]]["properties"]["PC"] = 0
                results[row[0]]["properties"]["mobile"] = 0
                results[row[0]]["properties"]["laptop"] = 0
                results[row[0]]["properties"]["total"] = 0

            if row[1] == "PC":
                results[row[0]]["properties"]["PC"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            elif row[1] == "laptop":
                results[row[0]]["properties"]["laptop"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]
            else:
                results[row[0]]["properties"]["mobile"] += row[2]
                results[row[0]]["properties"]["total"] += row[2]


    conn.close()

    return results

@app.route('/users/', methods=['POST'])
def add_user():
    type = request.json["mapType"]
    time = request.json["date"]
    # print(time)
    t = time[5:7] + time[8:10] + time[11:13] + time[14:16]
    # print(t)
    # t = "06301900"
    if type == "people":
    # t = time[5:7] + time[8:10] + time[11:13] + time[14:16]

        geojson=GetPeopleDistribution(t)
    else:
        geojson =GetDeviceDistribution(t)

    return  json.dumps(geojson), 201
# json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)


