import json
import sheet
import time

delay = 4

start = 400
end = 500
count = start

"""
29 : 1.201 : None
48 : 1.31 : x
75 : 1.84 : ✓R
88 : 10.143 :  
171 : 100.269 :   
{{215 : 100}}
260 : 101.364 : None
341 : 103.157 :   
387 : 104.140 : R
479 : 105.219 : None
490 : 105.287 : None
517 : 105.92 : 
602 : 107.91 :   
607 : 108.113 : x
636 : 108.29 : x
642 : 108.387 : None
656 : 108.92 : None
684 : 109.402 : None
806 : 111.29 : x
844 : 112.68 : ✓R
1035 : 118.121 :  s
1170 : 12.339 : ✓R
1196 : 12.76 : ✓R
1214 : 120.199 : ✓R
1227 : 120.337 : None
1230 : 120.397 : None
1231 : 120.398 : None
1291 : 121.337 :   
1295 : 121.397 :   
1296 : 121.398 :   
1387 : 122.357 :   
1391 : 122.387 : 
1421 : 123.102 : x
1423 : 123.108 : x
"""

print("BEFORE")
with open("sprites.json") as json_file:
    print("DURING")
    fusions = json.load(json_file)
    sheet.init()
    print("AFTER")

    print(" ")
    print(len(fusions))
    print(" ")

    for fusion_id in fusions[start:]:
        data = sheet.get_fusion_data_by_fusion_id(fusion_id)
        try:
            if (data.value != sheet.approved_fusion):
                print(count, ":", fusion_id, ":", data.value)
        except Exception as e:
            print("Exception (", count, "/", fusion_id, ") : ", e)
        count += 1
        time.sleep(delay)

    print(" ")
    print("DONE")