# This file is used to calculate the percentage of each type in our results.

import json

PC_cnt = 0
laptop_cnt = 0
mobile_cnt = 0
with open("results/device_dict") as f:
    a = f.readlines()
    for line in a:
        data = json.loads(line)
        if data["device"] == "PC":
            PC_cnt += 1
        elif data["device"] == "laptop":
            laptop_cnt += 1
        else:
            mobile_cnt += 1
f.close()
total_cnt = PC_cnt+laptop_cnt+mobile_cnt
print("total:\t",total_cnt)
print("PC:\t",PC_cnt,"\t", PC_cnt/total_cnt)
print("laptop:\t",laptop_cnt,"\t", laptop_cnt/total_cnt)
print("mobile:\t",mobile_cnt,"\t", mobile_cnt/total_cnt)

staff_cnt = 0
student_cnt = 0
with open("reer") as f:
    a = f.readlines()
    for line in a:
        data = json.loads(line)
        if data["career"] == "staff":
            staff_cnt += 1
        else:
            student_cnt += 1
f.close()
total_cnt = staff_cnt+student_cnt
print("total:\t",total_cnt)
print("staff:\t",staff_cnt,"\t", staff_cnt/total_cnt)
print("student:\t",student_cnt,"\t", student_cnt/total_cnt)
