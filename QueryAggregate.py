import os
import json
from GeoInfo import buildlocationdict
from BuildingName import buildnamedict

day_dict = {
    "Monday": ["0507", "0514", "0521", "0528", "0604", "0611", "0618", "0625"],
    "Tuesday": ["0501","0508", "0515", "0522", "0529", "0605", "0612", "0619", "0626"],
    "Wednesday": ["0502","0509", "0516", "0523", "0530", "0606", "0613", "0620", "0627"],
    "Thursday": ["0503","0510", "0517", "0524", "0531", "0606", "0614", "0621", "0628"],
    "Friday": ["0504","0511", "0518", "0525", "0601", "0607", "0615", "0622", "0629"],
    "Saturday": ["0505","0512", "0519", "0526", "0602", "0608", "0616", "0623", "0630"],
    "Sunday": ["0506","0513", "0520", "0527", "0603", "0610", "0617", "0624"]
}

teaching_dict = {
    "Monday": ["0507", "0514", "0521"],
    "Tuesday": ["0508", "0515", "0522"],
    "Wednesday": ["0509", "0516", "0523"],
    "Thursday": ["0510", "0517", "0524"],
    "Friday": ["0511", "0518", "0525"],
    "Saturday": ["0512", "0519", "0526"],
    "Sunday": ["0513", "0520", "0527"]
}

exam_dict = {
    "Monday": [ "0604", "0611", "0618"],
    "Tuesday": ["0605", "0612", "0619"],
    "Wednesday": ["0606", "0613", "0620"],
    "Thursday": ["0607", "0614", "0621"],
    "Friday": ["0608", "0615", "0622"],
    "Saturday": ["0609", "0616", "0623"],
    "Sunday": ["0610", "0617", "0624"]
}



def GetAggregatePathsTo(wt, wd, bn, st, et):
    error_cnt = 0
    results = {}
    cnt_res = {}

    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num

    results[0] = {}
    results[0]["type"] = "Feature"
    results[0]["geometry"] = {}
    results[0]["geometry"]["type"] = "Point"
    cds = buildlocationdict[building_no]
    results[0]["geometry"]["coordinates"] = [cds[1], cds[0]]
    results[0]["properties"] = {}
    results[0]["properties"]["building_type"] = "start"
    results[0]["properties"]["building_name"] = bn
    results[0]["properties"]["total"] = 0

    if wt == "teaching":
        days = teaching_dict[wd]
    elif wt == "exam":
        days = exam_dict[wd]
    else:
        days = day_dict[wd]

    for day in days:
        start_time = int(day) * 10000 + int(st)
        end_time = int(day) * 10000 + int(et)
        if int(st) < 200:
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

        results[0]["properties"]["total"] += total

        j = end_time
        if end_time - start_time <= 200:
            s_time = start_time
        else:
            if int(et) < 100:
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

    print("total:", results[0]["properties"]["total"])

    sorted_res = sorted(cnt_res.items(), key=lambda item:item[1], reverse=True)

    idx = 1
    for (building, cnt) in sorted_res:
        if building in buildlocationdict and cnt_res[building] >= 20:
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



def GetAggregatePathsFrom(wt, wd, bn, st, et):
    error_cnt = 0
    results = {}
    cnt_res = {}

    for num in buildnamedict:
        if buildnamedict[num] == bn:
            building_no = num

    results[0] = {}
    results[0]["type"] = "Feature"
    results[0]["geometry"] = {}
    results[0]["geometry"]["type"] = "Point"
    cds = buildlocationdict[building_no]
    results[0]["geometry"]["coordinates"] = [cds[1], cds[0]]
    results[0]["properties"] = {}
    results[0]["properties"]["building_type"] = "start"
    results[0]["properties"]["building_name"] = bn
    results[0]["properties"]["total"] = 0

    if wt == "teaching":
        days = teaching_dict[wd]
    elif wt == "exam":
        days = exam_dict[wd]
    else:
        days = day_dict[wd]

    for day in days:
        start_time = int(day) * 10000 + int(st)
        end_time = int(day) * 10000 + int(et)
        total = 0
        macs = {}

        i = start_time

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

        results[0]["properties"]["total"] += total

        if int(et) < 200:
            s_time = end_time - 7800
        else:
            s_time = end_time - 200
        j = end_time

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

    print("total:", results[0]["properties"]["total"])

    sorted_res = sorted(cnt_res.items(), key=lambda item:item[1], reverse=True)

    idx = 1
    for (building, cnt) in sorted_res:
        if building in buildlocationdict and cnt_res[building] >= 20:
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


while True:
    print("input a week type: (teaching/exam/all)")
    week_type = input()
    print("input a day: (Monday/Tuesday/...)")
    week_day = input()
    print("input a building name: (see in BuildingName.py)")
    bn = input()
    print("input start time: (hour + minute: HHMM)")
    st = input()
    print("input end time: (hour + minute: HHMM)")
    et = input()

    if int(st) <= int(et):
        geojson = GetAggregatePathsTo(week_type, week_day, bn, st, et)
    else:
        geojson = GetAggregatePathsFrom(week_type, week_day, bn, st, et)
