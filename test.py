import os
from os import listdir
from os.path import isfile, join

token = os.environ['GSHEET_KEY']
print(token)

text_file = open("token.json", "wt")
text_file.write(token)
text_file.close()

mypath = "."
# onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print("-")
for element in listdir(mypath):
    print(element)
print("-")