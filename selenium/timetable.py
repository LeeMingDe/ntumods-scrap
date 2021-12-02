from os import _exit
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from shutil import which
import json

accountId = ""
accountPassword = ""

fileToOpen = "moduleCodeList.json"
fileToOutput = "modulesTimetableExtra.json"
modulesList = open(fileToOpen)
modulesList = json.load(modulesList)

def outputToJson(moduleList):
    jsonString = json.dumps(moduleList)
    jsonFile = open(fileToOutput, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

chrome_path = which("chromedriver")

driver = webdriver.Chrome(executable_path=chrome_path)
driver.get("https://wish.wis.ntu.edu.sg/pls/webexe/ldap_login.login?w_url=https://wish.wis.ntu.edu.sg/pls/webexe/aus_stars_planner.main")

username_input = driver.find_element_by_id("UID")
username_input.send_keys(accountId)

ok_btn = driver.find_element_by_xpath("//form/table/tbody/tr/td/table/tbody/tr[4]/td[2]/input[1]")
ok_btn.click()

username_input = driver.find_element_by_id("PW")
username_input.send_keys(accountPassword)

ok_btn = driver.find_element_by_xpath("//form/center[1]/table/tbody/tr/td/table/tbody/tr[5]/td[2]/input[1]")
ok_btn.click()

planner = driver.find_element_by_xpath("//table/tbody/tr/td[1]/table/tbody/tr[15]/td/input")
planner.click()

moduleTimetable = {}

try:
    for count, module in enumerate(modulesList[328:]):
        # add_course = driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]/table/tbody/tr[1]/td[1]/a/span")
        # add_course.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//table/tbody/tr[1]/td[2]/table/tbody/tr[1]/td[1]/a/span'))).click()

        print(str(count) + ": " + module)

        # Key in module code to search
        alert = driver.switch_to.alert
        alert.send_keys(module)
        alert.accept()

        dropdown = Select(driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/select"))
        moduleTimetable[module] = {}

        # exam = driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[3]/font").text
        try:
            exam = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[3]/font'))).text
            moduleTimetable[module]["exam"] = exam
        except:
            moduleTimetable[module]["exam"] = "Not Applicable"

        moduleTimetable[module]["timetable"] = {}

        # Skip if dropdown only got 1 option
        if len(dropdown.options) <= 1:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[1]/a[1]/span"))).click()
            alert = driver.switch_to.alert
            alert.accept()
            continue

        # Iterate through the dropdown options
        for optionNum in range(1, len(dropdown.options)):
            dropdown = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/select"))))
            # dropdown = Select(driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/select"))

            timetableIndex = dropdown.options[optionNum].get_attribute("value")
            dropdown.select_by_index(optionNum)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/select")))

            # Skip if there is duplicate index
            if timetableIndex in moduleTimetable[module]["timetable"]:
                continue

            moduleTimetable[module]["timetable"][timetableIndex] = []

            # Loop through the rows and column of the table
            rowCounter = 2
            while True:
                columnCounter = 2

                # Terminate loop and move on to next option in the dropdown if number of rows is exceeded
                if  not driver.find_elements_by_xpath(f"//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[{columnCounter}]"):
                    break

                # lastColumn = driver.find_element_by_xpath(f"(//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[last()])")
                lastColumn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f"(//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[last()])")))

                while True:
                    timings = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f"//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[{columnCounter}]/font"))).text
                    # timings = driver.find_element_by_xpath(f"//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[{columnCounter}]/font").text

                    if ' '.join(timings.split()):
                        timeslots = {
                            "day": WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f"//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[{columnCounter}]/font"))).text,
                            # "day": driver.find_element_by_xpath(f"//table/tbody/tr[1]/td[1]/table/tbody/tr[1]/td[{columnCounter}]/font").text,
                            "details": timings.replace("\n", " ")
                        }
                        timetableArray = moduleTimetable[module]["timetable"][timetableIndex]
                        timetableArray.append(timeslots)
                        moduleTimetable[module]["timetable"][timetableIndex] = timetableArray
                    if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f"//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[{columnCounter}]"))) == lastColumn:
                        rowCounter += 1
                        break
                    # if driver.find_element_by_xpath(f"//table/tbody/tr[1]/td[1]/table/tbody/tr[{rowCounter}]/td[{columnCounter}]") == lastColumn:
                    #     rowCounter += 1
                    #     break
                    columnCounter += 1

        # Confirm and remove the course
        # remove_course = driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[1]/a[1]/span")
        # remove_course.click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[1]/a[1]/span"))).click()
        alert = driver.switch_to.alert
        alert.accept()
finally:
    outputToJson(moduleTimetable)
