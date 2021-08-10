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

def save_data_from_sheet_to_file():
    worksheet_name = "Full dex"
    if sheet.init(worksheet_name):
        # print("INIT")
        all_data = sheet.get_all_fusion_data()
        # print("CONTINUE")
        with open("full_dex.txt", "w", encoding="utf-8") as f:
            for line_data in all_data:
                f.write("%s\n" % line_data)
        # print("DONE")

        
    else:
        print("ERROR")



dex_dict = {}

def add_element(key, value):
    if key in dex_dict:
        values = dex_dict[key]
        values.append(value)
        dex_dict[key]=values
    else:
        dex_dict[key]=[value]



def load_data_from_file():
    filename = "full_dex.txt"
    with open(filename, "r", encoding="utf-8") as f:
        idx1 = 0
        for line in f:
            val1 = line.split(",")
            # clean : val1
            index_1 = idx1 + 1
            for idx2, cell_value in enumerate(val1):
                cell_value = cell_value.replace("["," ").replace("]","")
                index_2 = idx2 + 1
                head_id = index_2
                body_id = index_1
                fusion_id = str(head_id) + "." + str(body_id)

                cell_value = cell_value.strip()
                
                # print(fusion_id, ":", cell_value)
                add_element(cell_value, fusion_id)



def clean_dex_dict():

    del dex_dict["''"]
    del dex_dict["'\\u2003'"]
    del dex_dict["'\\u2003\\u2003'"]

    confirmed = dex_dict.pop("'✓'")
    done = dex_dict.pop("'x'")
    redo = dex_dict.pop("'✓R'") + dex_dict.pop("'...R'") + dex_dict.pop("'R'")

    keys = list(dex_dict.keys())
    print(" ")
    print(keys)
    dex_dict["Claimed"] = []
    for key in keys:
        claimed = dex_dict[key]
        dex_dict["Claimed"] = dex_dict["Claimed"] + claimed
        del dex_dict[key]
    
    dex_dict["Confirmed"] = confirmed
    dex_dict["Done"] = done
    dex_dict["Redo"] = redo


def display_dex_dict():
    print(" ")
    for key in dex_dict:
        print(key, len(dex_dict[key]), "\n")
    print("TOTAL", len(dex_dict["Confirmed"]) + len(dex_dict["Done"]), "\n")



def save_total_from_list_to_json():
    total = dex_dict["Confirmed"] + dex_dict["Done"]
    total_json = json.dumps(total, separators=(',\n', ': '))
    sheet_sprites = open("sheet_sprites.json", "w")
    sheet_sprites.write(total_json)
    sheet_sprites.close()




save_data_from_sheet_to_file()
load_data_from_file()
clean_dex_dict()
display_dex_dict()
save_total_from_list_to_json()


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
