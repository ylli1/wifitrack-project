import json
import numpy as np
from sklearn.neighbors.kde import KernelDensity
import os
import multiprocessing

staff = ['BN381 333 Exhibition St','218','219','498','136','134','139','696','161','344','540','404','403','221','400','281','220','348','713','262','260','266','269','416','417','411','290','199','198','195','191','252','390','242','278','250','414','99 Shiel St North Melbourne','527','254','368','916','911','912','308','245','244','246','384','385','387','388','248','101','902','901','907','434','413','337','242','102','257','731','249','187','506','507','505','903','168','166','167','222','163','189','863','865','867','866','726','722','723','721','152','156','326','744','201','203','143','207','898','899','754','732','357','356','353','359','358','687']
student = ['133','130','160','719','716','715','714','263','261','128','528','379','418','419','200','194','144','193','192','115','110','113','112','204','140','206','421','914','423','363','243','103','101','106','105','148B','148A','906','905','908','519','510','177','176','175','174','173','171','170','182','181','184','169','165','162','861','860','862','864','151','150','153','154','158','541','879','876','875','872','155','147','142','141','149','437','122','123','Outdoor']




def select(file,staff,student):
    l = []
    record = {}
    a1 = []
    x = []
    listori = []
    y = []
    rankedlist = []
    with open("classify/"+file)as f:
        # with open("data" + "/" + file)as f:
        a = f.readlines()
        record["hmacaddress"] = json.loads(a[0])["hmacaddress"]

        for line in a:
            data = json.loads(line)
            if data["building"] in a1:
                indx = a1.index(data["building"])
                # print(indx)
                l.append(indx)


            else:
                a1.append(data["building"])
                indx = a1.index(data["building"])
                l.append(indx)

        print(l)
        print(a1)
        if len(a1) < 5:
            pass
        else:

            loc = np.array([d for d in l]).reshape(len(l), 1)

            s = np.array([d for d in range(0, len(a1))]).reshape(len(a1), 1)
            # print(loc)
            print(s)
            kde = KernelDensity(kernel='gaussian', bandwidth=0.01).fit(loc)

            for i in range(0, len(a1)):
                rankedlist.append(kde.score_samples(s)[i])
            # rankedlist=kde.score_samples(s).sort()

            listori = rankedlist.copy()
            rankedlist.sort(reverse=True)

            sat = 0
            stu = 0
            for i in range(0, 5):
                if a1[listori.index(rankedlist[i])] in staff:
                    sat += 1
                    y.append(rankedlist[i])
                    x.append(a1[listori.index(rankedlist[i])])

                elif a1[listori.index(rankedlist[i])] in student:
                    stu += 1
                    y.append(rankedlist[i])
                    x.append(a1[listori.index(rankedlist[i])])

            if stu > sat:
                record["career"] = "student"
            else:
                record["career"] = "staff"

            with open(("results/Career.json"), 'a') as file:
                record_str = json.dumps(record)
                file.writelines(record_str + '\n')


pool = multiprocessing.Pool(8)
dic = (os.listdir("data"))
for file in dic:
    pool.apply_async(select, args=(file,staff,student))

pool.close()
pool.join()
