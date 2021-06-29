import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

spreadsheet_name = "Pokemon IF Sprite Completion (discord bot)"
worksheet_name = "TestSheet"
row_fusion_init = 6
col_fusion_init = 3

no_fusion = ""
valid_fusion = "x"
approved_fusion = "✓"

scope = None
creds = None
client = None
sheet = None
wks = None

def init():
    successful_init = True
    try:
        global scope, creds, client, sheet, wks
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('token.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(spreadsheet_name)
        wks = sheet.worksheet(worksheet_name)
    except Exception as e:
        print("Exception :", e, "\n")
        successful_init = False
    return successful_init

def get_fusion_data(head_id, body_id):
    row, col = row_fusion_init + body_id, col_fusion_init + head_id
    return gspread.models.Worksheet.cell(wks, row, col)

def set_fusion_data(head_id, body_id, new_value):
    row = row_fusion_init + int(body_id)
    col = col_fusion_init + int(head_id)
    cell = gspread.utils.rowcol_to_a1(row, col)
    wks.update_acell(cell, new_value)

def validate_fusion(fusion_id):
    split_fusion_id = fusion_id.split(".")
    if len(split_fusion_id) == 2:
        head_id, body_id= int(split_fusion_id[0]), int(split_fusion_id[1])
        set_fusion_data(head_id, body_id, valid_fusion)
    else:
        print("validate_fusion", fusion_id)