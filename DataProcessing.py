import json
import math
import re

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper
    
courses = "course.json"
minors = "minors.json"

course = open(courses)
course = json.load(course)
minors = open(minors)
minors = json.load(minors)

def removeDuplicateAndAddProgrammeForCore(data):
    moduleDict = {}
    for module in data:
        if module["module_code"] not in moduleDict:
            moduleDict[module["module_code"]] = module
            moduleDict[module["module_code"]]["programme"] = [module["course_name"].replace("Year", "1").split("1")[2].strip()]
            moduleDict[module["module_code"]]["category"] = ["Core"]
        else:
            moduleDict[module["module_code"]]["programme"].append(module["course_name"].replace("Year", "1").split("1")[2].strip())
            moduleDict[module["module_code"]]["programme"] = list(set(moduleDict[module["module_code"]]["programme"]))
    return moduleDict

def convertAUToNum(moduleDict):
    for key, value in moduleDict.items():
        value["module_units"] = int(float(value["module_units"].split(" ")[0]))
    return moduleDict

minimalProcessedCourse = convertAUToNum(removeDuplicateAndAddProgrammeForCore(course))

def convertToDictionary(data):
    moduleDict = {}
    for module in data:
        moduleDict[module["module_code"]] = module
    return moduleDict

def addProgrammeAndCategoryForMinors(moduleDict):
    for key, value in moduleDict.items():
        if "General Education in " in value["course_name"]:
            value["category"] = ["Broadening & Deepening/GER-PE (STS)"]
            value["programme"] = [value["course_name"].replace("General Education in ", "").split("2021")[0].strip()]
        elif "C N Yang Scholars Programme" in value["course_name"]:
            value["programme"] = [value["course_name"].split("2021")[0].strip()]
            value["category"] = []
        elif "University Scholars Programme (Core)" in value["course_name"]:
            value["programme"] = [value["course_name"].split("(Core)")[0].strip()]
            value["category"] = ["Core"]
        elif "University Scholars Programme" in value["course_name"]:
            value["programme"] = [value["course_name"].split("2021")[0].strip()]
        elif "Broadening and Deepening Electives/Unrestricted Electives in " in value["course_name"]:
            value["programme"] = [value["course_name"].replace("Broadening and Deepening Electives/Unrestricted Electives in ", "").split("2021")[0].strip()]
            value["category"] = ["Broadening & Deepening/UE"]
        elif "Minor in " in value["course_name"]:
            value["category"] = []
            value["programme"] = [value["course_name"].replace("Minor in ", "").split("2021")[0].strip()]
    return moduleDict

minimalProcessedMinors = addProgrammeAndCategoryForMinors(convertAUToNum(convertToDictionary(minors)))

def combineMinorsAndModule(minorDict, courseDict):
    for key, value in minorDict.items():
        if key in course:
            courseDict[key]["isMinor"] = True
            courseDict[key]["deptMaintain"] = value["dept_maintain"]
            courseDict[key]["category"] = courseDict[key]["category"] + value["category"]
        else:
            courseDict[key] = value
    return courseDict

def addInPostrequisites(moduleDict):
    for key, value in moduleDict.items():
        if "Prerequisite:" in value:
            modulePrereq = value["Prerequisite:"].replace("OR", "&").replace(" &", " ")
            for module in modulePrereq.split(" "):
                module = module.strip()
                if "(Corequisite)" in module:
                    continue
                if module in moduleDict:
                    if moduleDict[module].get('prerequisiteFor') is not None:
                        if key not in moduleDict[module]["prerequisiteFor"]:
                            moduleDict[module]["prerequisiteFor"] += ", " + key
                    else:
                        moduleDict[module]["prerequisiteFor"] = key
    return moduleDict

combinedModulesDict = addInPostrequisites(combineMinorsAndModule(minimalProcessedCourse, minimalProcessedMinors))

def outputToJson(moduleDict, nameOfOutputFile):
    jsonString = json.dumps(moduleDict)
    jsonFile = open(nameOfOutputFile, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

timetable = "modulesTimetable.json"
timetable = open(timetable)
timetable = json.load(timetable)

def combineTimetable(combinedModules):
    for key, value in timetable.items():
        if key in combinedModules:
            combinedModules[key]["exam"] = value["exam"]
            moduleSchedule = []
            isLabBased = False
            isOnline = False
            isWorkloadObtained = False

            workload = {
                "lecture": 0,
                "tutorial": 0,
                "lab": 0
            }

            for index, timeslots in value["timetable"].items():
                for timeslot in timeslots:
                    if timeslot["day"] not in moduleSchedule:
                        moduleSchedule.append(timeslot["day"])
                    if "LAB" in timeslot["details"]:
                        isLabBased = True
                    if "ONLINE" in timeslot["details"]:
                        isOnline = True
                    if not isWorkloadObtained:
                        timings = list(set(re.sub("[;-]", "", timeslot["details"]).split())) #eg, 1230to1420
                        for timing in timings:
                            if "to" in timing:
                                timing = timing.split("to")
                                numHours = truncate((float(timing[1]) - float(timing[0]) + 10)/100, 1)
                                if "LEC" in timeslot["details"]:
                                    workload["lecture"] += numHours
                                elif " SEM " in timeslot["details"]:
                                    workload["lecture"] += numHours
                                elif "TUT" in timeslot["details"]:
                                    workload["tutorial"] += numHours
                                elif "LAB" in timeslot["details"]:
                                    workload["lab"] += numHours
                isWorkloadObtained = True
            combinedModules[key]["schedule"] = moduleSchedule
            combinedModules[key]["timetable"] = value["timetable"]
            combinedModules[key]["isLabBased"] = isLabBased
            combinedModules[key]["isOnline"] = isOnline
            combinedModules[key]["workload"] = workload
    return combinedModules

combinedModulesWithTimetable = combineTimetable(combinedModulesDict)

def extractProgrammeName(moduleDict):
    modulesProgramme = []
    for key, value in moduleDict.items():
        if "programme" in value:
            programme = value["programme"]
            modulesProgramme = modulesProgramme + programme
    return list(set(modulesProgramme))

outputToJson(extractProgrammeName(combinedModulesWithTimetable), "moduleProgramme.json")

def renameKeyInModuleDict(moduleDict):
    for key, value in moduleDict.items():
        value["courseName"] = value["course_name"]
        del value['course_name']

        value["moduleCode"] = value["module_code"]
        del value['module_code']

        value["moduleName"] = value["module_name"]
        del value['module_name']

        value["au"] = value["module_units"]
        del value['module_units']

        value["description"] = value["module_description"]
        del value['module_description']

        if "Prerequisite:" in value:
            value["prerequisite"] = value["Prerequisite:"]
            del value['Prerequisite:']

        if "Mutually exclusive with: " in value:
            value["preclusion"] = value["Mutually exclusive with: "]
            del value['Mutually exclusive with: ']

        if "Not available to Programme: " in value:
            value["NotAvailableToProgramme"] = value["Not available to Programme: "]
            del value['Not available to Programme: ']
        
        if "Not available to all Programme with: " in value:
            value["NotAvailableToAllProgrammeWith"] = value["Not available to all Programme with: "]
            del value['Not available to all Programme with: ']
        
        if "Not available as BDE/UE to Programme: " in value:
            value["NotAvailableAsBDE/UETo"] = value["Not available as BDE/UE to Programme: "]
            del value['Not available as BDE/UE to Programme: ']
        
        if "Not available as Core to Programme: " in value:
            value["NotAvailableAsCoreTo"] = value["Not available as Core to Programme: "]
            del value['Not available as Core to Programme: ']

        if "Not available as PE to Programme: " in value:
            value["NotAvailableAsPETo"] = value["Not available as PE to Programme: "]
            del value['Not available as PE to Programme: ']
    return moduleDict

def convertGradeTypeToBoolean(moduleDict):
    for key, value in moduleDict.items():
        if "Grade Type" in value:
            value["isPassFail"] = True
            del value["Grade Type"]
    return moduleDict

# renamedModuleDict = convertGradeTypeToBoolean(renameKeyInModuleDict(combinedModulesWithTimetable))
# print(len(renamedModuleDict))
# outputToJson(renamedModuleDict, "test.json")

def insertFaculty(moduleList):
    for key, value in moduleList.items():
        courseName = [x.lower() for x in value["programme"]]
        if "faculty" not in value:
            value["faculty"] = []

        if any("accountancy" in x for x in courseName) or any("business" in x for x in courseName) or any("nanyang technopreneurship centre" in x for x in courseName):
            value["faculty"].append("Nanyang Business School (NBS)")

        if any("electrical" in x for x in courseName):
            value["faculty"].append("School Electrical and Electronic Engineering (EEE)")    
        if (any("civil engineering" in x for x in courseName) or any("environmental engineering" in x for x in courseName) or any("information engineering" in x for x in courseName) or
            any("maritime studies"in  x for x in courseName)):
            value["faculty"].append("School of Civil and Environmental Engineering (CEE)")    
        if any("aerospace engineering" in x for x in courseName) or "engineering" in courseName or any("mechanical engineering" in x for x in courseName):
            value["faculty"].append("School of Mechanical and Aerospace Engineering (MAE)")
        if any("bioengineering" in x for x in courseName) or any("chemical" in x for x in courseName):
            value["faculty"].append("School of Chemical and Biomedical Engineering (SCBE)")
        if any("computer" in x for x in courseName) or any("data science" in x for x in courseName):
            value["faculty"].append("School of Computer Science and Engineering (SCSE)")
        if any("materials engineering" in x for x in courseName):
            value["faculty"].append("School of Materials Science and Engineering (MSE)")
        
        if (any("chinese" in x for x in courseName) or any("english" in x for x in courseName) or any("history" in x for x in courseName)
            or any("linguistics" in x for x in courseName) or any("philosophy" in x for x in courseName) or any("english literature" in x for x in courseName)
            or any("humanities" in x for x in courseName)):
            value["faculty"].append("School of Humanities (SOH)")
        if (any("economics" in x for x in courseName) or any("psychology" in x for x in courseName) or any("sociology" in x for x in courseName) or any("public policy" in x for x in courseName)
            or any("media analytics" in x for x in courseName) or any("drama" in x for x in courseName) or any("social sciences" in x for x in courseName)):
            value["faculty"].append("School of Social Sciences (SSS)")
        if any("communication studies" in x for x in courseName):
            value["faculty"].append("Wee Kim Wee School of Communication and Information (WKWSCI)")
        if any("art, design & media" in x for x in courseName):
            value["faculty"].append("School of Art, Design and Media (ADM)")
 
        if any("biomedical" in x for x in courseName) or any("biological" in x for x in courseName):
            value["faculty"].append("School of Biological Sciences (SBS)")
        if (any("data science" in x for x in courseName) or any("mathematical" in x for x in courseName) or any("physics" in x for x in courseName)
            or any("chemistry" in x for x in courseName) or any("mathematics" in x for x in courseName)):
            value["faculty"].append("School of Physical and Mathematical Sciences (SPMS)")    
        if any("environmental earth systems science" in x for x in courseName):
            value["faculty"].append("The Asian School of the Environment (ASE)")

        if any("renaissance engineering" in x for x in courseName):
            value["faculty"].append("Renaissance Engineering Programme (REP)")

        if any("science, technology & society" in x for x in courseName):
            value["faculty"].append("Institute of Science and Technology for Humanity (NISTH)")

        if (any("sport science and management" in x for x in courseName) or any("early childhood education" in x for x in courseName) 
        or any("education studies" in x for x in courseName) or any("early childhood education" in x for x in courseName) 
        or any("music" in x for x in courseName) or any('special needs education' in x for x in courseName)
        or any('science of learning' in x for x in courseName)): 
            value["faculty"].append("National Institute of Education (NIE)")

        if any("medicine" in x for x in courseName):
            value["faculty"].append("Lee Kong Chian School of Medicine (LKCM)")

        if any("university scholars programme" in x for x in courseName) or any("liberal arts" in x for x in courseName):
            value["faculty"].append("University Scholars Programme (USP)")

        if any("c n yang scholars programme" in x for x in courseName):
            value["faculty"].append("C N Yang Scholars Programme")

        if any('design and systems thinking' in x for x in courseName):
            value["faculty"].append("Centre for Teaching, Learning & Pedagogy (CTLP)")

        if any('youth work and guidance' in x for x in courseName):
            value["faculty"].append("SkillsFuture Work-Study Degree Programmes (WSDPs)")

        if len(value["faculty"]) == 0:
            print(courseName)

            break
    return moduleList

def addHasSaturdayAndExtendedTiming(moduleDict):
    for key, value in moduleDict.items():
        if "timetable" in value:
            for idx, timeslot in value["timetable"].items():
                for x in timeslot:
                    if "SAT" in x["day"]:
                        value["hasSaturday"] = True
                    detailsArr = x["details"].split(" ")
                    for y in detailsArr:
                        if "to" in y:
                            startTiming = y.split("to")[0]
                    if startTiming in ["1830", "1930", "2030", "2130", "2230", "2330"]:
                        value["isExtendedTiming"] = True
                    if "hasSaturday" in value and "isExtendedTiming" in value and value["hasSaturday"] and value["isExtendedTiming"]:
                        break
    return moduleDict

nameOfOutputFile = "final.json"
renamedModuleDict = convertGradeTypeToBoolean(renameKeyInModuleDict(combinedModulesWithTimetable))
renamedModuleDict = addHasSaturdayAndExtendedTiming(renamedModuleDict)

def outputToJsonMongoDbFormat(dictionary):
    for key, value in dictionary.items():
        jsonString = json.dumps(value)
        jsonFile = open(nameOfOutputFile, "a")
        jsonFile.write(jsonString)
        jsonFile.close()
outputToJsonMongoDbFormat(insertFaculty(renamedModuleDict))

