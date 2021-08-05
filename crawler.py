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
folderPath = '/Users/paking-guest/Desktop/pythonTool'
path = folderPath + '/Crawler_Script/crawler_script.txt'

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
    global driver
    global detectString
    global outputString
    outputString += item + "\n"
    source = item.split("|")
    act = source[0]
    if act == 'export':
        f = open(folderPath + '/Crawler_Script/' + source[1], "a")
        f.write(driver.page_source)
        f.close()
    tag = By.ID
    if source[1] == "ID":
       tag = By.ID 
    if source[1] == "LINK_TEXT":
       tag = By.LINK_TEXT 
    if source[1] == "PARTIAL_LINK_TEXT":
       tag = By.PARTIAL_LINK_TEXT
    if source[1] == "XPATH":
       tag = By.XPATH
    if source[1] == "NAME":
       tag = By.NAME 
    if source[1] == "CSS_SELECTOR":
       tag = By.CSS_SELECTOR 
    if source[1] == "CLASS_NAME":
       tag = By.CLASS_NAME
    if source[1] == "TAG_NAME":
       tag = By.TAG_NAME 
    tagVal = source[2] if len(source) > 2 else ""
    setVal = source[3] if len(source) > 3 else ""
    tmp = driver.find_elements(tag, tagVal)
    for item in tmp:
        if ( act == 'input' ):
            item.send_keys(setVal)
        if ( act == 'click' ):
            item.click()
        if ( act == 'text' ):
            outputString += "<get>" + item.text + "<get>\n"
        if ( act == 'recognize' ):
            get_captcha(driver,item,img_path+"recognize.png")
            if ( act == 'input_recognize'):
                if len(detectString) > 0 :
                    item.send_keys(detectString[0])
                    detectString.pop(0)
        if (act == 'get_image'):
            getImage(item,img_path+source[2]+'.png')
        if (act == 'get_attr_val'):
            search = source[3:]
            for el in search:
                outputString += "<{}>".format(el) + item.get_attribute(el) + "<{}>\n".format(el)
        if (act == 'set_attr_val'):
            search = source[3:]
            driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2])", item, search[0],search[1] )
    if ( act == 'js'):
        driver.execute_script(source[1])
        
def doSrcipt(driver,action):
    for item in action:
        doAction(item)
    print( "Script Done!" )

def getImage(element,path):
    global driver
    driver.save_screenshot(path)          # 先將目前的 screen 存起來
    location = element.location           # 取得圖片 element 的位置
    size = element.size                   # 取得圖片 element 的大小
    print(size)
    left = int(location['x']) + offsetX                 # 決定上下左右邊界
    top = int(location['y']) + offsetY
    right = left + int(size['width']) * scale_x
    bottom = top + int(size['height']) * scale_y
    image = Image.open(path)        # 將 screen load 至 memory
    image = image.crop((left, top, right, bottom)) # 根據位置剪裁圖片
    image.save(path, 'png')
    return image

def get_captcha(driver, element, path):
    global reader
    global detectString
    global outputString
    global ocrMode
    image = getImage(element,path)
    if ocrMode == 0:
        print('pytesseract')
        detectString = pytesseract.image_to_string(image)
    else:
        print('easy ocr')
        detectString = reader.readtext(path, detail = 0)
    for item in detectString:
        outputString += 'Detect Text:' + item + "\n"
            
    
# main 
f = open(path, 'r',encoding="utf-8")
scriptStr = f.read()
f.close()
setting = find_between(scriptStr,"//Setting","//Setting").split("\n")[1:-1]
settingDict = {}
for item in setting:
    key = item.split(',')[0]
    val = item.split(',')[1]
    settingDict[key] = val

ocrMode = settingDict['ocrMode'] # 0->pytesseract 1->easyocr
url = settingDict['url']
img_path = settingDict['img_path']
driverPath = settingDict['driverPath']
offsetX = int(settingDict['offsetX'])
offsetY = int(settingDict['offsetY'])
scale_x = float(settingDict['scale_x'])
scale_y = float(settingDict['scale_y'])
outputString = ""
print('===Setting===')
pprint(settingDict)
print('===Setting===\n\n')
driver = webdriver.Chrome(executable_path = driverPath)
driver.set_window_size(int(settingDict['browserW']), int(settingDict['browserH']))
detectString = ""
reader = easyocr.Reader(['ch_sim','en'])
action = find_between(scriptStr,"//Script","//Script").split("\n")[1:-1]
print('===Script===')
pprint(action)
print('===Script===\n\n')
driver.get(url)
sleep(10)
doSrcipt(driver,action)
path = settingDict['outputText']
f = open(path, 'w',encoding="utf-8")
f.write(outputString)
f.close()

import keyboard
while True:
    if keyboard.read_key() == "esc":
        driver.close()
        break
