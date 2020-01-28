#Tiny Tower Bot: https://github.com/CeHaga/Tiny-Tower-Bot
#Made by Carlos Bravo
#Feel free to copy or modify as you wish

import os
import cv2 as cv
import numpy as np 
from time import sleep 

def androidTap(x,y):
    os.system("adb shell input tap " + str(x) + " " + str(y))

def androidType(text):
    text = text.replace(" ","\ ")
    os.system('adb shell input text "' + text + '"')

def screenshot(name):
    os.system("adb shell screencap -p /sdcard/TesteAndroid/screencap.png")
    os.system("adb pull /sdcard/TesteAndroid/screencap.png")
    os.system("mv screencap.png Screenshots/" + name + ".png")
    os.system("adb shell rm /sdcard/TesteAndroid/screencap.png")

def androidPress(x,y,tempo):
    os.system("adb shell input swipe " + str(x) + " " + str(y) + " " + str(x) + " " + str(y) + " " + str(tempo))

def androidSwipe(x1,y1,x2,y2,tempo):
    os.system("adb shell input swipe " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2) + " " + str(tempo))

def identifyFloor(imgGray,elevator=True):
    folder = ''
    if(elevator): folder = "Elevator"
    else: folder = "Request"
    floors = []
    floor = 0
    for i in range(10):
        temp = cv.imread("Screenshots/"+folder+"/"+str(i)+".png",0)
        w,h = temp.shape[::-1]
        res = cv.matchTemplate(imgGray,temp,cv.TM_CCOEFF_NORMED)
        threshold = 0.92
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            floors.append((pt[0],i))

    floors = sorted(floors,reverse=True)
    exp = 0
    for t in floors:
        floor += t[1] * 10**exp
        exp += 1
    return floor

def elevatorState(req = False, top = True):
    screenshot("elevator")
    img = cv.imread("Screenshots/elevator.png")
    imgGray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    floorReq = imgGray[1202:1253,97:200]
    nextFloor = imgGray[910:971,102:190]
    # cv.imshow("Request",floorReq)
    # cv.waitKey(0)
    if(not isActive(img)): return False,None,0,0
    if(reachedTop(imgGray)): return True,True,0,0 
    requestReturn = 0
    if(req): requestReturn = identifyFloor(floorReq,False)
    return True, False, identifyFloor(nextFloor), requestReturn

def isActive(img):
    imgGray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    temp = cv.imread("Screenshots/button.png",0)
    w,h = temp.shape[::-1]
    res = cv.matchTemplate(imgGray,temp,cv.TM_CCOEFF_NORMED)
    threshold = 0.75
    loc = np.where(res >= threshold)
    return len(loc[0]) != 0

def reachedTop(img):
    temp = cv.imread("Screenshots/top.png",0)
    w,h = temp.shape[::-1]
    res = cv.matchTemplate(img,temp,cv.TM_CCOEFF_NORMED)
    threshold = 0.75
    loc = np.where(res >= threshold)
    return len(loc[0]) != 0

def elevator():
    #androidTap(130,1730) #Click the person
    print("Starting elevator")
    active, _, nextFloor, request= elevatorState(req = True, top = False)

    if(not active): return

    androidPress(404.5,1985,1000) #Press up for 1 second
    sleep(0.8)
    print("Calculating velocity")

    active, _, nextFloor,_ = elevatorState(top = False)
    vel = nextFloor - 2 #Calculate FPS
    while(active):
        sleep(0.5)
        active, top, nextFloor,_ = elevatorState()
        if(not active or nextFloor == request+1): break
        if(top):
            print("Last floor")
            time = int((1/vel)*975)
            androidPress(676,1985,time)
            continue
        if(not active or nextFloor == request+1): break
        dif = request - nextFloor + 1 #Difference of floors
        print("next = {}\nreq = {}\nvel = {}\ndif = {}".format(nextFloor,request,vel,dif))
        time = int((dif/vel)*975) #Time left pressing (975 because acceleration for the first few floors, the later ones will be adjusted)
        if(time > 0): androidPress(404.5,1985,time)
        else: androidPress(676,1985,-time)
    print("Done")

def isPersonWaiting(img):
    x,y = 0,0
    temp = cv.imread("Screenshots/elevatorButton.png",0)
    w,h = temp.shape[::-1]
    res = cv.matchTemplate(img,temp,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        x = pt[0]+w/2
        y = pt[1]+h/2
    return len(loc[0]) != 0, x, y

def checkStock(img):
    imgGray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    imgCut = imgGray[1850:1940, 135:510]
    temp = cv.imread("Screenshots/stock.png",0)
    res = cv.matchTemplate(imgCut,temp,cv.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if(len(loc) != 0):
        print(img[1927,358])
        if(np.all(img[1927,358] == [204,131,0])):
            androidTap(309.7,1910.1)
            sleep(0.5)
            androidTap(750.2,1392.4)
            sleep(0.7)
            if(checkComplete(img)): androidTap(545.5,1406.4)

def checkComplete(img):
    imgGray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    temp = cv.imread("Screenshots/continue.png",0)
    w,h = temp.shape[::-1]
    res = cv.matchTemplate(imgGray,temp,cv.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)
    return len(loc[0]) != 0

def autoPlay():
    sleep(2)
    screenshot("lobby")
    lobby = cv.imread("Screenshots/lobby.png")
    wait, x, y = isPersonWaiting(cv.cvtColor(lobby,cv.COLOR_BGR2GRAY))
    if(wait):
        androidTap(x,y)
        sleep(2)
        elevator()
        androidTap(68.9,2213)
    checkStock(lobby)

def visit():
    print("Starting visit")
    firstY = [1934,1715,1544,1339,1139,942,760,560] 
    screenshot("friends")
    img = cv.imread("Screenshots/friends.png")
    if(np.all(img[1970,530] == [0,0,0])): print("Few friends") #TODO
    else:
        print("Going down")
        while(np.all(img[2080,530] != [24,15,3]) and np.all(img[2080,530])):
            androidSwipe(400,2050,400,10,1000)
            screenshot("friends")
            img = cv.imread("Screenshots/friends.png")
            print(img[2080,530])
        print("Bottom")
        for y in firstY:
            print(y)
            androidTap(414.5,y)
            print("Clicking friend")
            sleep(0.1)
            screenshot("friends")
            img = cv.imread("Screenshots/friends.png")
            while(not checkComplete(img) and not isActive(img)):
                print("Looking complete or elevator")
                sleep(0.5)
                screenshot("friends")
                img = cv.imread("Screenshots/friends.png")
            if(checkComplete(img)): androidTap(545.5,1406.4)
            if(isActive(img)):
                elevator()
                while(not checkComplete(img)): 
                    screenshot("friends")
                    img = cv.imread("Screenshots/friends.png")
                androidTap(545.5,1406.4)
            print("Complete! Closing friend")
            sleep(0.1)
            androidTap(978,2180)
            sleep(0.1)
        while(True):
            print("Going to next upward")
            androidSwipe(414.5,1885,414.5,2059,1000)
            screenshot("friends")
            img = cv.imread("Screenshots/friends.png")
            if(np.all(img[277,13] == [0,224,0])):
                print("Found top")
                androidTap(414.5,700)
                screenshot("friends")
                img = cv.imread("Screenshots/friends.png")
                while(not checkComplete(img) or not isActive(img)):
                    sleep(0.5)
                    screenshot("friends")
                    img = cv.imread("Screenshots/friends.png")
                if(checkComplete(img)): androidTap(545.5,1406.4)
                if(isActive(img)):
                    elevator()
                    while(not checkComplete(img)): 
                        screenshot("friends")
                        img = cv.imread("Screenshots/friends.png")
                    androidTap(545.5,1406.4)
                sleep(0.1)
                androidTap(978,2180)
                sleep(0.1)
                androidTap(414.5,516.5)
                screenshot("friends")
                img = cv.imread("Screenshots/friends.png")
                while(not checkComplete(img) or not isActive(img)):
                    sleep(0.5)
                    screenshot("friends")
                    img = cv.imread("Screenshots/friends.png")
                if(checkComplete(img)): androidTap(545.5,1406.4)
                if(isActive(img)):
                    elevator()
                    while(not checkComplete(img)): 
                        screenshot("friends")
                        img = cv.imread("Screenshots/friends.png")
                    androidTap(545.5,1406.4)
                sleep(0.1)
                androidTap(978,2180)
                sleep(0.1)
                androidTap(978,2180) #Close friends list
                sleep(0.1)
                androidTap(978,2180) #Close menu
                return
            androidTap(414.5,516.5)
            screenshot("friends")
            img = cv.imread("Screenshots/friends.png")
            while(not checkComplete(img) and not isActive(img)):
                sleep(0.5)
                screenshot("friends")
                img = cv.imread("Screenshots/friends.png")
            if(checkComplete(img)): androidTap(545.5,1406.4)
            if(isActive(img)):
                elevator()
                while(not checkComplete(img)): 
                    screenshot("friends")
                    img = cv.imread("Screenshots/friends.png")
                androidTap(545.5,1406.4)
            sleep(0.1)
            androidTap(978,2180)
            sleep(0.1)
