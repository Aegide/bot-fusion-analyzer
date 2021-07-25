import json
import sheet
import time

valid_value = "✓"
no_value = ""
worksheet_name = "Aegide Dex"
cell_list = []

print("BEFORE JSON FILE")
with open("sprites.json") as json_file:
    print("AFTER JSON FILE")
    print(" ")
    print("BEFORE JSON LOAD")
    fusions = json.load(json_file)
    print("AFTER JSON LOAD")
    print(" ")
    if sheet.init(worksheet_name):
        print("BEFORE FUSION CELLS")
        for fusion_id in fusions:
            cell = sheet.get_valid_cell_by_fusion_id(fusion_id)
            print(fusion_id, cell)
            cell_list.append(cell)
        print("AFTER FUSION CELLS")
        print(" ")
        sheet.set_fusion_data_from_list(cell_list)    
        print("DONE")
    else:
        print("ERROR")


"""
delay = 4
start = 400
end = 500
count = start
with open("sprites.json") as json_file:
    print("DURING")
    fusions = json.load(json_file)
    sheet.init(worksheet_name)
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
"""