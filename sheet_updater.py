import json
import sheet
import time

valid_value = "✓"
no_value = ""
cell_list = []


def load_sprites_json_then_update_sheet():
    worksheet_name = "Aegide Dex"
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


def load_data_from_sheet():
    worksheet_name = "Aegide Dex"
    if sheet.init(worksheet_name):
        print("INIT")
        all_data = sheet.get_all_fusion_data()
        print("DONE")
        for idx1, val1 in enumerate(all_data):
            index_1 = idx1+1
            if index_1 == 15:
                for idx2, cell_value in enumerate(val1):
                    index_2 = idx2+1
                    head_id = index_2
                    body_id = index_1
                    print(head_id, body_id, ":", cell_value)
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
