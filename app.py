from flask import Flask,render_template,jsonify,request
import sqlite3
import json
from collections import defaultdict

app = Flask(__name__)


@app.route('/')

def start():
    # if request.method == "POST":
    #     username = request.form.get("trip-start")
        # userage = request.div.get("userage")
    return render_template("test_api.html")

def geodev(property):
    geojson = [{
        data: {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": property[data]["coordinates"]
            },
            "properties":
                {
                    "building_name": data,
                    "detail": {
                        "PC": property[data]["PC"],
                        "laptop": property[data]["laptop"],
                        "mobile": property[data]["mobile"],
                    },
                    "total": property[data]["total"],
                }
        }
    } for data in property]

    return geojson

def geocareer(property):
    geojson =[{
        data: {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": property[data]["coordinates"]
            },
            "properties":
                {
                    "building_name": data,
                    "detail": {
                        "student": property[data]["student"],
                        "staff": property[data]["staff"],
                    },
                    "total": property[data]["total"],
                }
        }
    } for data in property]

    return geojson

@app.route('/users/', methods=['POST'])
def add_user():
    conn = sqlite3.connect('DB3.sqlite')
    cursor = conn.cursor()
    type = request.json["mapType"]
    time=request.json["date"]
    print(time)
    t=time[5:7]+time[8:10]+time[11:13]+time[14:16]
    # te=time[5:7]+time[8:10]+time[11:13]+time[14:16]
    # print(t)
    if type=="people":
        cursor.execute("select building,career from BInT, Career where BInt.mac = Career.mac and tm= "+t+" ")
        # data="po"
        data = cursor.fetchall()
        recordBudList=[]
        property=defaultdict(defaultdict)
        count=0

        for line in data:
            # print(line[0])
            if line[0] in recordBudList:

                if line[1]=="staff":
                    property[line[0]]["staff"] +=1
                else:
                    property[line[0]]["student"]+=1

                property[line[0]]["total"]+=1

            else:
                recordBudList.append(line[1])
                property[line[0]]["staff"] = 0
                property[line[0]]["student"] = 0
                property[line[0]]["total"]=0
                property[line[0]]["coordinates"] = []

                if line[1]=="staff":
                    property[line[0]]["staff"] +=1
                else:
                    property[line[0]]["student"]+=1

                property[line[0]]["total"] += 1


            # print(property[data]["staff"])

        geojson = geocareer(property)


    else:
        cursor.execute("select building,device from BInT, Device where BInt.mac = Device.mac and tm=t ")
        data = cursor.fetchall()
        recordBudList = []
        property = defaultdict(defaultdict)
        count = 0
        for line in data:
            # print(line[0])
            if line[0] in recordBudList:

                if line[1] == "laptop":
                    property[line[0]]["laptop"] += 1
                elif line[1] == "PC":
                    property[line[0]]["PC"] += 1
                else:
                    property[line[0]]["mobile"] += 1
                property[line[0]]["total"] += 1


            else:
                recordBudList.append(line[1])
                property[line[0]]["laptop"] = 0
                property[line[0]]["PC"] = 0
                property[line[0]]["mobile"] = 0
                property[line[0]]["total"] = 0
                property[line[0]]["coordinates"]=[]

                if line[1] == "laptop":
                    property[line[0]]["laptop"] += 1
                elif line[1] == "PC":
                    property[line[0]]["PC"] += 1
                else:
                    property[line[0]]["mobile"] += 1

                property[line[0]]["total"] += 1

        geojson=geodev(property)

    return  json.dumps(geojson), 201
# json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)


