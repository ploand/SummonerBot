
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

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
adbpath = '.\\platform-tools\\.\\adb'
serial = ""
ImageFile.LOAD_TRUNCATED_IMAGES = True

def adbshell(command):
    args = [adbpath]
    if serial is not None:
        args.append('-s')
        args.append(serial)
    args.append('shell')
    args.append(command)
    # print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

def adbpull(command):
    args = [adbpath]
    args.append('pull')
    args.append(command)
    # print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

def adbdevices():
    # create a tuple with the arguments for the command
    args = [adbpath]
    args.append('devices')
    # run command to shell (This is not hazardos while shell=True because
    # the args input is not dependant in user input)
    child = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    # split the bytes string where I can get the serial of the device
    bSerial = child.stdout.read().split(b'\n')[1].split(b'\t')[0]
    # decode the bytes into string
    return bSerial.decode()

def touchscreen_devices():
        child = adbshell('getevent -il')
        bTouchdev = child.stdout.read().split(b'add device ')
        bTouchdev = list(filter(lambda x: x.find(b'ABS_MT_POSITION_X') > -1, bTouchdev))[0]
        return bTouchdev.decode()

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
    adbshell('screencap /sdcard/SummonerBot/capcha.png')
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
    try: 
        im = Image.open(image_file + '.tif')
        text = image_to_string(im)
        text = image_file_to_string(image_file + '.tif')
        text = image_file_to_string(image_file + '.tif', graceful_errors=True)
    except IOError:
        print("Error converting tif to text")

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

def getScreenCapture():
    screenCapture()
    # Pull image from the phone
    adbpull("/sdcard/SummonerBot/capcha.png")
    # convert to a working jpg file
    time.sleep(1)
    try:
        im = Image.open("capcha.png")
        rgb_im = im.convert('RGB')
        rgb_im.save('capcha.jpg')
    except IOError:        
        print("Could not open file capcha.png")
    # return file name
    return "capcha"

def crop(x,y,h,w,fileName):
    try:
        img = cv2.imread(fileName + '.jpg')
        if img.all != None:
            crop_img = img[y:y+h, x:x+w]
            cv2.imwrite(fileName + "_c.jpg", crop_img)
    except IOError:
        print("Could not open file " + fileName)
    return fileName + "_c"

def crop2Default():
    try:
        img = cv2.imread('capcha_c.tif')
        if img.all != None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.tif", crop_img)    
    except IOError:
        print("Could not open file capcha_c.tif")

    try:
        img = cv2.imread('capcha_c.jpg')
        if img.all != None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.jpg", crop_img)    
    except IOError:
        print("Could not open file capcha_c.jpg")
    print("Reset defaults")

def performOCR():
    fileN = getScreenCapture()
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("Not enough Energy") != -1:
            return "refill"
        if text.find("Revive") != -1:
            return "revive"
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
    tap(random.randint(670,920),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked recharge energy")
    tap(random.randint(600,970),random.randint(300,700))
    sleepPrinter(2)

    print("Clicked confirm buy")
    tap(random.randint(670,920),random.randint(600,700))
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
    keep = False
    hasSpeedSub = False
    fileN = crop(1200,350,50,100,"capcha") # Rarity
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("Rare"):
            # Sell rune if it's 5* and Rare.
            keep = False
        # if text.find("Rare"):
        #     # Sell rune if it's 5* and Rare.
        #     Keep = False
    
    fileN = crop(600,450,300,500,"capcha") # Sub stats
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("SPD"):
            # Keep rune if it has speed sub.
            hasSpeedSub = True

    # print(fullText)
    # print(findCommand(fullText,fileN))
    if keep == False:
        print("Clicked sell rune")
        tap(random.randint(700,900),random.randint(820,920)) 
        sleepPrinter(random.uniform(1,3))
        print("Clicked confirmed rune sell")
        tap(random.randint(680,880),random.randint(600,700))
    else:
        print("Clicked keep rune")
        tap(random.randint(1030,1230),random.randint(820,920))

def startBot():
    i = 0
    while True:
        # imageType = screenCapture()
        print("-----------------------------------------------------------------------------------------")
        # sleepPrinter(random.uniform(0,1))
        # imageType = "golden_retriver"
        # print(runImageCheck(imageType).stdout.read().split(b'(score ')[0].decode())
        crop2Default() # Reset capcha_c.tif file to avoid reading the same file next iteration
        # convPNG2TIF("capcha")
        getScreenCapture()
        print("Clicked Start")
        tap(random.randint(1460,1780),random.randint(780,840)) # Click on start
        # sleepPrinter(random.uniform(110,115))
        refilled = False
        loopCond = True
        mod = 0
        while loopCond:
            # sleepPrinter(3)
            ret = performOCR()
            if ret.find("refill") != -1:
                refillEnergy()
                loopCond = False
                refilled = True

            if ret.find("revive") != -1:
                
                print("Clicked no on revive")
                tap(random.randint(1050,1420),random.randint(650,750))
                sleepPrinter(1)
                print("Clicked Randomly")
                tap(random.randint(1300,1350),random.randint(450,700))
                refilled = True
                loopCond = False
            
            if ret.find("reward") != -1:
                loopCond = False
                # performOCR()
            
            # print("\r" + ret)
            mod += 1        
            mod = mod %1024
            sys.stdout.write('\r' + ret + str(mod))
            sys.stdout.flush()
        
        
        if refilled == False:
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(450,700))
            sleepPrinter(1)
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(650,700))
            sleepPrinter(3)
            # Click get symbol
            print("Clicked Get Symbol\\angelmon\\scrolls")
            tap(random.randint(950,1050),random.randint(850,950)) 
            sleepPrinter(random.uniform(1,3))
            # print("Clicked again for safety")
            # tap(random.randint(850,1050),random.randint(850,950)) 
            # sleepPrinter(random.uniform(1,3))
            # Click keep rune
            keepOrSellRune()
            # print("Clicked keep rune")
            # tap(random.randint(1030,1230),random.randint(820,920)) 
            sleepPrinter(random.uniform(1,3))
            # print("Clicked keep rune")
            # tap(random.randint(1030,1230),random.randint(820,920)) 
            # sleepPrinter(random.uniform(1,3))
        # open or close chat randomly
        # openCloseChat = random.randint(1,100)
        # if openCloseChat < 10:
        #     tap(random.randint(20,100),random.randint(20,100))
        #     sleepPrinter(random.uniform(1.5,2.5))
        #     tap(random.randint(1820,1860),random.randint(50,100))
        #     sleepPrinter(random.uniform(1.5,2.5))
        # Replay
        print("Clicked Continue")
        tap(random.randint(350,850),random.randint(520,650))
        # Check if we need to refill
        ret = performOCR()
        if ret.find("refill") != -1:
            refillEnergy()

clearConsole()
print("---Finding devices serial---")
serial = adbdevices()
print("---Serial found---")
startBot()

print("Finished")