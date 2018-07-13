
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

ImageFile.LOAD_TRUNCATED_IMAGES = True
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
adbpath = '..\\platform-tools\\.\\adb'
serial = ""

def adbshell(command):
    args = [adbpath]
    if serial is not None:
        args.append('-s')
        args.append(serial)
    args.append('shell')
    args.append(command)
    print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

def adbpull(command):
    args = [adbpath]
    # if serial is not None:
        # args.append('-s')
        # args.append(serial)
    args.append('pull')
    args.append(command)
    print(args)
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
    else:
        print("-----------------removing screen capture-----------------")
        adbshell('rm /sdcard/SummonerBot/capcha.png')
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

    sys.stdout.write('\r')
    sys.stdout.flush()

def getScreenCapture():
    screenCapture()
    # Pull image from the phone
    adbpull("/sdcard/SummonerBot/capcha.png")
    # convert to a working jpg file
    im = Image.open("capcha.png")
    rgb_im = im.convert('RGB')
    rgb_im.save('capcha.jpg')
    # return file name
    return "capcha"

def performCommand():
    
    fileN = getScreenCapture()# '.\dataset\gb10_start_run'
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    print(fullText)
    returnVal = findCommand(fullText,fileN)
    if returnVal == "ERROR":
        return False
    else:
        return True

def tif2text(fileName):
    image_file = fileName
    im = Image.open(image_file + '.tif')
    text = image_to_string(im)
    text = image_file_to_string(image_file + '.tif')
    text = image_file_to_string(image_file + '.tif', graceful_errors=True)

    return text

def convTIF2PNG(fileName):
    image_file = Image.open(fileName + '.tif').convert('L')
    image_file.save(fileName + '.jpg')

def convPNG2TIF(fileName):
    # print(fileName)
    image_file = Image.open(fileName + '.jpg').convert('L')
    image_file.save(fileName + '.tif')

def crop(x,y,h,w,fileName):
    img = cv2.imread(fileName + '.jpg')
    if img.all != None:
        crop_img = img[y:y+h, x:x+w]
        cv2.imwrite(fileName + "_c.jpg", crop_img)
        return fileName + "_c"

def refillEnergy():

    status = "gb10_not_enough_energy"
    i = 0
    while status.find("gb10_purchase_succesful") != -1:
        fileN = getScreenCapture()# '.\dataset\gb10_start_run'
        convPNG2TIF(fileN)
        fullText = tif2text(fileN).split('\n')
        # print(fullText)
        for textInput in fullText:
            if textInput.find("Not enough Energy") != -1:
                if i == 0:
                    status = "gb10_not_enough_energy"
                    i += 1

            if textInput.find("sundle Man") != -1:
                if i == 1:
                    status = "gb10_purchase_energy"
                    i += 1
                
            if textInput.find("Purchase with 30 CrystaI(s)?") != -1:
                if i == 2:
                    status = "gb10_purchase_confirm_spend_crystals"
                    i += 1
            
            if textInput.find("Purchase successful") != -1:
                if i == 3:
                    status = "gb10_purchase_succesful"
                    i += 1
    exitRefill()

def exitRefill():
    print("Clicked Close Purchase")
    tap(random.randint(1760,1850),random.randint(75,140))

oper = 0

def findCommand(fullText,fileName):
    for textInput in fullText:
        # print(textInput)
        if textInput.find("Would you like to sell") != -1:
            # TODO if it's a blue rune, sell! implement color pick here
            return "gb10_confirm_rune_sell"
        
        if ( textInput.find("Giant") != -1 ):
            # if
            if oper == 1: 
                # We win
                print("Clicked Randomly")
                tap(random.randint(1300,1900),random.randint(100,1000))
                sleepPrinter(3)
                # Chest click
                print("Clicked Chest")
                tap(random.randint(1300,1900),random.randint(100,1000))
                return "gb10_loading_victory"

        if textInput.find("Not enough Energy") != -1:
            return "gb10_not_enough_energy"

        if textInput.find("Network connection delayed") != -1: 
            if oper == 0:
                while textInput.find("Network connection delayed") != -1:
                    fileN = getScreenCapture()
                    convPNG2TIF(fileN)
                    fullText = tif2text(fileN).split('\n')
                return "gb10_network_connection_delay"
            
        if textInput.find("a magic symbol") != -1:
            # Click get symbol
            print("Clicked Get Symbol\\angelmon\\scrolls")
            tap(random.randint(950,1050),random.randint(850,950))
            return "gb10_magic_symbol_red"
            

        if textInput.find("Rune ") != -1:
            # For now, keep the rune
            # Click keep rune
            print("Clicked keep rune")
            tap(random.randint(1030,1230),random.randint(820,920))
            return "gb10_sell_rune"

        if textInput.find("Giant") != -1:
            print("Clicked Replay")
            tap(random.randint(350,850),random.randint(520,650))
            return "gb10_victory_post_sell"

        if textInput.find("Revive now") != -1:
            if oper == 1:
                print("Clicked Dead")
                tap(random.randint(1050,1420),random.randint(650,750))
                sleepPrinter(random.uniform(1,3))
                print("Clicked Randomly")
                tap(random.randint(1300,1900),random.randint(100,1000))
                return "gb10_death"
                

        # if textInput.find("Battle") != -1:
        #     return "gb10_start_run" 

        # fileN = crop(1400,650,1800,850,fileName)
        # if fileN != None:
        #     convPNG2TIF(fileN)
        #     fullText = tif2text(fileN).split('\n')
        #     print(fullText)
        #     return findCommand(fullText,fileN)

    return "ERROR"


def startBot():
    while True:
        
        print("-----------------------------------------------------------------------------------------")
        
        print("Clicked Start")
        tap(random.randint(1460,1780),random.randint(780,840)) # Click on start
        # sleepPrinter(50)
        oper = 0
        while True:
            returnVal = performCommand()
            oper += 1
            if returnVal == "gb10_not_enough_energy":
                refillEnergy()
            sleepPrinter(random.uniform(3,5))
        # sleepPrinter(random.uniform(110,115))
        
        # # Click get symbol
        # print("Clicked Get Symbol\\angelmon\\scrolls")
        # tap(random.randint(950,1050),random.randint(850,950)) 
        # sleepPrinter(random.uniform(1,3))
        # # Click keep rune
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
        

clearConsole()
print("---Finding devices serial---")
serial = adbdevices()
print("---Serial found: " + serial + "---")
startBot()

# fileN = getScreenCapture()# '.\dataset\gb10_start_run'
# convPNG2TIF(fileN)
# fullText = tif2text(fileN).split('\n')
# print(fullText)
# print(findCommand(fullText,fileN))

# print("Finished")
