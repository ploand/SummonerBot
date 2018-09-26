#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
from PIL import Image
from PIL import ImageFile
from pytesser import *
import cv2
from adbInterface import adbInterface as adb

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
adbpath = '..\\platform-tools\\.\\adb'
serial = ""
ImageFile.LOAD_TRUNCATED_IMAGES = True
soldRunes = 0
keptRunes = 0
totalRefills = 0
adb = adb()

### Sobre o funcionamento do bot ###
    # As vezes o bot nao limpa a variavel ref o que faz com que o texto antigo fique sendo exibido apos a tela de execucao do bot exemplo "Reward"
    # isso faz com que o bot execute a rotina de cliques 

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
        print("-- creating new folder --")
        adbshell('mkdir -m 777 /sdcard/SummonerBot')
    else:
        #print("-- comando do adb para remover capturas de tela --")
        adbshell('rm /sdcard/SummonerBot/capcha.jpg')
        #adbshell('rm /sdcard/SummonerBot/capcha_c.jpg')
        #adbshell('rm /sdcard/SummonerBot/capcha.png')
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
    # print("-- Nome da imagem salva como TIF --") #Exibindo o nome do arquivo salvo no formato TIF que sera usado como base para leita da tela pelo bot
    # print(fileName)
    # geralmente o nome das imagens salvas sao "capcha" e "capcha_c" respectivamente
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

### textos exibidos no final da dungeon de gigante ###
    # "eed more room in you" - exibido quando o inventario de runas esta cheio
    # "symbol that contains" - quando a recompensa eh simbolo do caos
    # "pieces of stones"     - quando a recompensa eh pecas de runa
    # "Unknown Scroll"       - quando a recompensa eh unknown scroll

def performOCR(): # Metodo que fica sendo executado e faz a leitura da tela para o bot processar as informacoes
    time.sleep(2) # Adicionado um tempo de espera para o bot nao ler a tela muitas vezes seguidas
    global totalRefills
    fileN = getScreenCapture()
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("Not enough Energy") != -1:
            totalRefills += 1
            return "need refill"
        if text.find("Revive") != -1:
            return "revive screen"
        if text.find("pieces of stones") != -1:
            return "pieces of stones screen"
        if text.find("symbol that contains") != -1:
            return "symbol that contains screen"
        if text.find("DEF") != -1 or text.find("ATK") != -1 or text.find("HP") != -1 or text.find("SPD") != -1 or text.find("CRI") != -1 or text.find("Resistance") != -1 or text.find("Accuracy") != -1:
            return "rune screen"
        if text.find("correct") != -1:
            return "correct"
    fileN = crop(800,350,300,450,fileN)
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    print("-- exibindo conteudo da variavel (fullText) utilizada no metodo performOCR --")
    print(fullText) # exibe a array com varios textos de leitura da tela
    for text in fullText: # caso o bot retorne reward ele executa o procedimento para verificar runa e continua e retorna a execucao para este metodo
        if text.find("Reward") != -1:
            return "reward"
        if text.find("Rewand") != -1:
            return "reward"
        if text.find("Rewamdi") != -1:
            return "reward"
        if text.find("Rewamd") != -1:
            return "reward"

    return "performed OCR reading"

# (bug) Quando o bot entra neste metodo ele nao sai mais    
def refillEnergy():
    print("\nClicked Refill\n")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("\nClicked recharge energy\n")
    tap(random.randint(690,700),random.randint(300,700))
    sleepPrinter(2)

    print("\nClicked confirm buy\n")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("\nClicked purchase successful\n")
    tap(random.randint(840,1090),random.randint(600,700))
    sleepPrinter(2)

    print("\nClicked close shop\n")
    tap(random.randint(850,1050),random.randint(880,980))
    sleepPrinter(2)

    exitRefill()

def exitRefill():
    print("\nClicked Close Purchase\n")
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
        print("\nClicked sell rune\n")
        tap(random.randint(700,900),random.randint(820,920)) 
        sleepPrinter(random.uniform(1,3))
        print("\nClicked confirmed rune sell\n")
        tap(random.randint(850,880),random.randint(600,700))
        soldRunes += 1
    else:
        print("\nClicked keep rune\n")
        tap(random.randint(1030,1230),random.randint(820,920))
        keptRunes += 1

def sayNo2Revives():
    print("\nClicked no on revive\n")
    tap(random.randint(1050,1420),random.randint(650,750))
    sleepPrinter(1)
    print("\nClicked Randomly\n")
    tap(random.randint(1340,1350),random.randint(440,450))
    sleepPrinter(1)
    print("\nClicked Randomly\n")
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
    print("\nClicked Get Symbol\\angelmon\\scrolls\n")
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
        print("-- Stats --")
        print("Selling runes: " + str(SellRunes))
        print("Number of runes sold: " + str(soldRunes))
        print("Number of runes kept: " + str(keptRunes))
        print("Total refills: " + str(totalRefills))
        print("Total runs: " + str(i))
        print("-----------------------------------------------------------------------------------------")
        
        crop2Default() # Reset capcha_c.tif file to avoid reading the same file next iteration
        
        getScreenCapture()
        print("\nClicked Start\n")
        tap(random.randint(1460,1780),random.randint(780,840)) # Click on start
        
        refilled = False
        loopCond = True
        mod = 0
        while loopCond:
            ret = performOCR()
            if ret.find("need refill") != -1: #(bug) quando o bot entra na condicao de refil nao esta saindo mais
                refillEnergy()
                loopCond = False
                refilled = True

            if ret.find("revive screen") != -1:
                sayNo2Revives()
                refilled = True
                loopCond = False
            
            if ret.find("reward") != -1 or ret.find("rune screen") != -1:
                loopCond = False

            if ret.find("correct") != -1:
                return True

            if  ret.find("pieces of stones screen") != -1 or ret.find("symbol that contains screen") != -1:
                clickOther()
                loopCond = False

            mod += 1        
            mod = mod %1024
            print("-- exibindo o texto de leitura de tela --")
            sys.stdout.write(ret + " (execution number:" + str(mod) + ")\n") # exibe o texto "performed OCR reading" ou o texto que retornardo do metodo performOCR()
            sys.stdout.flush()
            print("\n")
        
        if refilled == False:
            print("\nClicked Randomly\n")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(1)
            print("\nClicked Randomly\n")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(3)
            # Click get other stuff if needed
            # clickOther()
            # Click keep rune
            if SellRunes:
                keepOrSellRune()
            else:
                print("\nClicked keep rune\n")
                tap(random.randint(1030,1230),random.randint(820,920)) 
            sleepPrinter(random.uniform(2,3))
            
        print("\nClicked Continue\n")
        tap(random.randint(800,850),random.randint(600,650))
        sleepPrinter(random.uniform(1.5,2.5))
        

clearConsole()

startBot(False)
# keepOrSellRune()

print("Finished")