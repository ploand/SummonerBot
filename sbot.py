#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
from PIL import Image
from PIL import ImageFile
from pytesser import *
import cv2.cv2 as cv2
from adbInterface import adbInterface as adb

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
adbpath = '..\\platform-tools\\.\\adb'
serial = ""
ImageFile.LOAD_TRUNCATED_IMAGES = True
soldRunes = 0
keptRunes = 0
totalRefills = 0
adb = adb()

def adbshell(command):
    return adb.adbshell(command)

def adbpull(command):
    return adb.adbpull(command)

def adbdevices():
    return adb.adbdevices()

def touchscreen_devices():
        return adb.touchscreen_devices()

def tap(x, y):
    command = "input tap " + str(x) + " " + str(y)
    command = str.encode(command)
    adbshell(command.decode('utf-8'))

def screenCapture():
    # perform a search in the sdcard of the device for the SummonerBot
    # folder. if we found it, we delete the file inside and capture a 
    # new file.
    child = adbshell('ls sdcard')
    bFiles = child.stdout.read().split(b'\n')
    bFiles = list(filter(lambda x: x.find(b'SummonerBot\r') > -1, bFiles))
    if  len(bFiles) == 0:
        print("-----------------creating new folder-----------------")
        adbshell('mkdir -m 777 /sdcard/SummonerBot')
    # else:
        # print("-----------------removing screen capture-----------------")
        # adbshell('rm /sdcard/SummonerBot/capcha.png')
    adbshell('screencap -p /sdcard/SummonerBot/capcha.jpg')
    return ""

def clearConsole():
    os.system('cls') 

def runImageCheck(imageType):
    args = ["python.exe","classify_image.py","--image_file",".\dataset\\" + imageType + ".jpeg"]
    # print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

def sleepPrinter(timeEpoch):
    # print("sleeping for: " + str(timeEpoch) + " seconds")
    sleepCountdown(timeEpoch)

def sleepCountdown(timeEpoch):
    last_sec = 0
    for i in range(0,int(timeEpoch)):
        sys.stdout.write('\r' + str(int(timeEpoch)-i)+' ')
        sys.stdout.flush()
        time.sleep(1)
        last_sec = i
    if timeEpoch-float(last_sec+1) > 0:
        time.sleep(timeEpoch-float(last_sec+1))
    # print("")
    sys.stdout.write('\r')
    sys.stdout.flush()
        # print("")
        # print("waiting reminder: " + str(timeEpoch-float(last_sec+1)))

def tif2text(fileName):
    image_file = fileName
    text = ""
    try: 
        im = Image.open(image_file + '.tif')
        text = image_to_string(im)
        text = image_file_to_string(image_file + '.tif')
        text = image_file_to_string(image_file + '.tif', graceful_errors=True)
    except IOError:
        print("Error converting tif to text")
    except errors.Tesser_General_Exception:
        print("Error converting tif to text in Tesseract")

    return text

def convTIF2PNG(fileName):
    image_file = Image.open(fileName + '.tif').convert('L')
    image_file.save(fileName + '.jpg')

def convPNG2TIF(fileName):
    # print(fileName)
    try: 
        image_file = Image.open(fileName + '.jpg').convert('L')
        image_file.save(fileName + '.tif')
    except IOError:
        print("Error saving from jpg to tif")

def checkSixStar(fileName):
    res = False
    im_gray = cv2.imread(fileName+".jpg", cv2.IMREAD_GRAYSCALE)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    try:
        if im_bw is not None:
            res = im_bw[363][718] == im_bw[363][732]
            print("Found it to be a 6*? " + str(res))
    except IOError:
        print("No picture found")
    return res

def getScreenCapture():
    screenCapture()
    # Pull image from the phone
    adbpull("/sdcard/SummonerBot/capcha.jpg")
    # adbpull("/sdcard/SummonerBot/capcha.png")
    # # convert to a working jpg file
    time.sleep(1)
    # try:
    #     im = Image.open("capcha.png")
    #     rgb_im = im.convert('RGB')
    #     rgb_im.save('capcha.jpg')
    # except IOError:        
    #     print("Could not open file capcha.png")
    # return file name
    return "capcha"

def crop(x,y,h,w,fileName):
    try:
        img = cv2.imread(fileName + '.jpg')
        if img is not None:
            crop_img = img[y:y+h, x:x+w]
            cv2.imwrite(fileName + "_c.jpg", crop_img)
    except IOError:
        print("Could not open file " + fileName)
    return fileName + "_c"

def crop2Default():
    try:
        img = cv2.imread('capcha_c.tif')
        if img is not None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.tif", crop_img)    
    except IOError:
        print("Could not open file capcha_c.tif")

    try:
        img = cv2.imread('capcha_c.jpg')
        if img.all() != None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.jpg", crop_img)    
    except IOError:
        print("Could not open file capcha_c.jpg")

def performOCR():
    global totalRefills
    fileN = getScreenCapture()
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("Not enough Energy") != -1:
            totalRefills += 1
            return "refill"
        if text.find("Revive") != -1:
            return "revive"
        if text.find("correct") != -1:
            return "correct"
    fileN = crop(800,350,300,450,fileN)
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    print(fullText)
    for text in fullText:
        if text.find("Reward") != -1:
            return "reward"
        if text.find("Rewand") != -1:
            return "reward"
        if text.find("Rewamdi") != -1:
            return "reward"
        if text.find("Rewamd") != -1:
            return "reward"

    return "performed OCR reading "
    
def refillEnergy():
    print("Clicked Refill")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked recharge energy")
    tap(random.randint(690,700),random.randint(300,700))
    sleepPrinter(2)

    print("Clicked confirm buy")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked purchase successful")
    tap(random.randint(840,1090),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked close shop")
    tap(random.randint(850,1050),random.randint(880,980))
    sleepPrinter(2)

    # exitRefill()

def exitRefill():
    print("Clicked Close Purchase")
    tap(random.randint(1760,1850),random.randint(75,140))


def keepOrSellRune():
    i = 2
    keep = True
    hasSpeedSub = False
    foundRare = False
    global soldRunes
    global keptRunes
    
    while i > 0:
        i-=1
        performOCR()        
        fileN = crop(1200,350,50,100,"capcha") # Rarity
        convPNG2TIF(fileN)
        
        try:
            img = cv2.imread('capcha_c.tif')
            if img.all() != None:
                cv2.imwrite("rarity.tif", img) 
        except IOError:
            print("couldn't save with other name")
        fullText = tif2text("rarity").split('\n')

        print("Rarity:" + str(fullText))
        rarity = ""
        for text in fullText:
            if text.find("Rare") != -1:
                # Sell rune if it's 5* and Rare.
                foundRare = True
                rarity = "Rare"
            if text.find("Hero") != -1:
                rarity = "Hero"
            if text.find("Legend") != -1:
                rarity = "Legend"

        if rarity == "" and i == 0:
            clickOther()
            return

        
        fileN = crop(600,350,300,600,"capcha") # Sub stats
        convPNG2TIF(fileN)
        
        try:
            img = cv2.imread('capcha_c.tif')
            if img.all() != None:
                cv2.imwrite("substats.tif", img) 
        except IOError:
            print("couldn't save with other name")
        fullText = tif2text("substats").split('\n')

        print("Subststs:" + str(fullText))
        for text in fullText:
            if text.find("SPD") != -1:
                # Keep rune if it has speed sub.
                hasSpeedSub = True

    sixStar = checkSixStar("capcha")

    print("found speed? " + str(hasSpeedSub))
    print("found rare? " + str(foundRare))
    print("found rarity? " + rarity)
    # print("Is 5* and has speed? " + str(sixStar))

    if sixStar:
        if rarity == "Rare" and not hasSpeedSub:
            keep = False
        else:
            keep = True
    else:
        if rarity == "Legend":
            keep = True
        else:
            # keep = False
            if  rarity == "Hero" and hasSpeedSub:
                keep = True
            else:
                keep = False
        
    print("keep? " + str(keep))
    if keep == False:
        print("Clicked sell rune")
        tap(random.randint(700,900),random.randint(820,920)) 
        sleepPrinter(random.uniform(1,3))
        print("Clicked confirmed rune sell")
        tap(random.randint(850,880),random.randint(600,700))
        soldRunes += 1
    else:
        print("Clicked keep rune")
        tap(random.randint(1030,1230),random.randint(820,920))
        keptRunes += 1

def sayNo2Revives():
    print("Clicked no on revive")
    tap(random.randint(1050,1420),random.randint(650,750))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1340,1350),random.randint(440,450))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1300,1350),random.randint(440,450))
    sleepPrinter(3)

def clickOther():
    
    # fileN = crop(580,250,100,600,"capcha") # Rarity
    # convPNG2TIF(fileN)
    # fullText = tif2text(fileN).split('\n')
    # print(fullText)
    # clickOthers = False
    # for text in fullText:
    #     if ( text.find("Rare") == -1 ):
    #         clickOthers = True
    #     if ( text.find("Legend") == -1 ): 
    #         clickOthers = True
    #     if ( text.find("Hero") == -1 ):
    #         # if it doesn't have rarity, it's not a rune.
    #         clickOthers = True
    # if clickOthers:    
    print("it's not a rune!")
    print("Clicked Get Symbol\\angelmon\\scrolls")
    tap(random.randint(950,960),random.randint(850,870)) 
    sleepPrinter(random.uniform(1,3))
    # return clickOthers

def startBot(_SellRunes = False):
    SellRunes = _SellRunes
    i = 0
    while True:
        i += 1
        # print()
        print("-----------------------------------------------------------------------------------------")
        
        print("Stats:")
        print("Selling runes? " + str(SellRunes))
        print("Number of runes sold: " + str(soldRunes) + " Number of runes kept: " + str(keptRunes))
        print("Total refills: " + str(totalRefills))
        print("Total runs: " + str(i))
        print("-----------------------------------------------------------------------------------------")
        
        crop2Default() # Reset capcha_c.tif file to avoid reading the same file next iteration
        
        getScreenCapture()
        print("Clicked Start")
        tap(random.randint(1460,1780),random.randint(780,840)) # Click on start
        
        refilled = False
        loopCond = True
        mod = 0
        while loopCond:
            ret = performOCR()
            if ret.find("refill") != -1:
                refillEnergy()
                loopCond = False
                refilled = True

            if ret.find("revive") != -1:
                sayNo2Revives()
                refilled = True
                loopCond = False
            
            if ret.find("reward") != -1:
                loopCond = False

            if ret.find("correct") != -1:
                return True

            mod += 1        
            mod = mod %1024
            sys.stdout.write(ret + str(mod) + "\n")
            sys.stdout.flush()        
        
        if refilled == False:
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(1)
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(3)
            # Click get other stuff if needed
            # clickOther()
            # Click keep rune
            if SellRunes:
                keepOrSellRune()
            else:
                print("Clicked keep rune")
                tap(random.randint(1030,1230),random.randint(820,920)) 
            sleepPrinter(random.uniform(2,3))
            
        print("Clicked Continue")
        tap(random.randint(800,850),random.randint(600,650))
        sleepPrinter(random.uniform(1.5,2.5))
        

clearConsole()

startBot(True)
# keepOrSellRune()

print("Finished")