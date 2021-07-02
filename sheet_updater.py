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