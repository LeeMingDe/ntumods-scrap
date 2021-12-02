import json

fileToOpen = "moduleCodeList.json"
modulesList = open(fileToOpen)
modulesList = json.load(modulesList)

print(len(modulesList))