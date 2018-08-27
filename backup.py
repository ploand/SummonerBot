
#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
import numpy as np
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
    # convPNG2TIF(fileName)
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

oper = 0

def findCommand(fullText,fileName):
    for textInput in fullText:
        print(textInput)
        if textInput.find("Rare") != -1:
            # TODO if it's a blue rune, sell! implement color pick here
            return "gb10_sell_rune"

    return "ERROR"

def checkFiveStar(fileName):
    im_gray = cv2.imread(fileName+".jpg", cv2.IMREAD_GRAYSCALE)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    return im_bw[363][718] == im_bw[363][732]

def capchaCheck():
    fileN = ".\\dataset\\capcha_run"# '.\dataset\gb10_start_run'
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("correct"):
            return True

clearConsole()
print(capchaCheck())
# fileN = ".\dataset\capcha_run"# '.\dataset\gb10_start_run'
# convPNG2TIF(fileN)
# fullText = tif2text(fileN).split('\n')
# for text in fullText:
#     if text.find("correct"):
#         return True
# fileN = crop(735,365,30,150,fileN) # Rarity

# (730,360) (x,y) of 6th star
# (720,360) (x,y) of 5th star
# img = cv2.imread(fileN + '.jpg')
# print(img[700,360])
# print(img[720,360])
# if img[720,360].all(img[730,360]):
    # print("Not a 6* rune")
# convPNG2TIF(fileN)
# fullText = tif2text(fileN).split('\n')

# print(fullText)
# print(findCommand(fullText,fileN))
# im_gray = cv2.imread(fileN + '.jpg', cv2.IMREAD_GRAYSCALE)
# # (thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
# thresh = 150
# im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
# cv2.imwrite(fileN + '.jpg', im_bw)

# print("Finished")
