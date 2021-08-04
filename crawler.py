import re, csv
from time import sleep, time
from bs4 import BeautifulSoup as soup
import pandas as pd
import json
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pytesseract
import easyocr
import re
from pprint import pprint
# config absolute

path = '/Users/paking-guest/Desktop/pythonTool/crawler/crawler_script.txt'

# config
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def doAction(item):
    # ID = "id"
    # XPATH = "xpath"
    # LINK_TEXT = "link text"
    # PARTIAL_LINK_TEXT = "partial link text"
    # NAME = "name"
    # TAG_NAME = "tag name"
    # CLASS_NAME = "class name"
    # CSS_SELECTOR = "css selector"
    global detectString
    global outputString
    source = item.split(",")
    act = source[0]
    tag = By.ID
    if source[1] == "ID":
       tag = By.ID 
    if source[1] == "NAME":
       tag = By.NAME 
    if source[1] == "CSS_SELECTOR":
       tag = By.CSS_SELECTOR 
    if source[1] == "CLASS_NAME":
       tag = By.CLASS_NAME 
    if source[1] == "TAG_NAME":
       tag = By.TAG_NAME 
    tagVal = source[2]
    setVal = source[3] if len(source) > 3 else ""
    if ( act == 'input' ):
        driver.find_element(tag, tagVal).send_keys(setVal)
    if ( act == 'click' ):
        driver.find_element(tag, tagVal).click()
    if ( act == 'text' ):
        outputString += "<get>" + driver.find_element(tag, tagVal).text + "<get>\n"
    if ( act == 'recognize' ):
        get_captcha(driver,driver.find_element(tag, tagVal),img_path)
    if ( act == 'input_recognize'):
        if len(detectString) > 0 :
            driver.find_element(tag, tagVal).send_keys(detectString[0])
            detectString.pop(0)
        
def doSrcipt(driver,action):
    for item in action:
        doAction(item)


def get_captcha(driver, element, path):
    global reader
    global detectString
    global outputString
    driver.save_screenshot(path)          # 先將目前的 screen 存起來
    location = element.location           # 取得圖片 element 的位置
    size = element.size                   # 取得圖片 element 的大小
    left = int(location['x']) + offsetX                 # 決定上下左右邊界
    top = int(location['y']) + offsetY
    right = left + int(size['width']) + marginRight
    bottom = top + int(size['height']) + marginBottom
    image = Image.open(path)        # 將 screen load 至 memory
    image = image.crop((left, top, right, bottom)) # 根據位置剪裁圖片
    image.save(path, 'png')
    detectString = reader.readtext(path, detail = 0)
    for item in detectString:
        outputString += 'Detect Text:' + item + "\n"
            
    
# main 
f = open(path, 'r')
scriptStr = f.read()
f.close()
setting = find_between(scriptStr,"//Setting","//Setting").split("\n")[1:-1]
settingDict = {}
for item in setting:
    key = item.split(',')[0]
    val = item.split(',')[1]
    settingDict[key] = val


url = settingDict['url']#"https://officemail.cloudmax.com.tw"
img_path = settingDict['img_path']#"/Users/paking-guest/Desktop/ipynb/screen.png"
driverPath = settingDict['driverPath']#"/Users/paking-guest/Desktop/ipynb/chromedriver"
offsetX = int(settingDict['offsetX'])
offsetY = int(settingDict['offsetY'])
marginRight = int(settingDict['marginRight'])
marginBottom = int(settingDict['marginBottom'])
outputString = ""
pprint(settingDict)
driver = webdriver.Chrome(executable_path = driverPath)
driver.set_window_size(int(settingDict['browserW']), int(settingDict['browserH']))
detectString = ""
reader = easyocr.Reader(['ch_sim','en'])
action = find_between(scriptStr,"//Script","//Script").split("\n")[1:-1]
driver.get(url)
doSrcipt(driver,action)

path = settingDict['outputText']
f = open(path, 'w')
f.write(outputString)
f.close()

import keyboard
while True:
    if keyboard.read_key() == "esc":
        driver.close()
        break

    
