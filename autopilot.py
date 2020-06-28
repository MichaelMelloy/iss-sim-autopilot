from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

#for some fucking reason space'x display is wrong and is actually 2.6x faster. -> 0.1°/s is actually 0.26°/s
#direction controlls increase by 0.03m/s per hit so 5 hits are equal to 0.15m/s
#Start Browser and connect to SpaceX-Sim
driver = webdriver.Firefox()
driver.get("https://iss-sim.spacex.com/")

fast = 70
slow = 20
dock = 2

rotSpeed3 = 0.71
rotSpeed0 = 0.11

lastRollCalc = 0
lastPitchCalc = 0
lastYawCalc = 0
lastXCalc = 0
lastYCalc = 0
lastZCalc = 0



#Define Rotational values
roll, rollRate, pitch, pitchRate, yaw, yawRate = 0, 0, 0, 0, 0, 0
#Define Distane values
xDist, xRate, yDist, yRate, zDist, zRate = 0, 0, 0, 0, 0, 0


#Start Simulator
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "begin-button"))).click() #Click on the Begin button

print("Starting Autopilot")

time.sleep(12) #let simulator actually start

# //*[@id='direction']/div[1] <- what the xml path should look like

body = driver.find_element_by_xpath("/html/body") #Gets Body to send keys for operation (faster than clicking buttons)
def rollLeft():
    body.send_keys(Keys.NUMPAD7)
def rollRight():
    body.send_keys(Keys.NUMPAD9)
def pitchUp():
    body.send_keys(Keys.NUMPAD8)
def pitchDown():
    body.send_keys(Keys.NUMPAD5)
def yawLeft():
    body.send_keys(Keys.NUMPAD4)
def yawRight():
    body.send_keys(Keys.NUMPAD6)

def Forward():
    body.send_keys('E')
def Backward():
    body.send_keys('Q')
def Up():
    body.send_keys('w')
def Down():
    body.send_keys('S')
def Left():
    body.send_keys('A')
def Right():
    body.send_keys('D')

#Get Rotational values
def updateValues():
    #get global variables

    global roll, rollRate, pitch, pitchRate, yaw, yawRate, xDist, xRate, yDist, yRate, zDist, zRate, lastRollCalc, lastPitchCalc, lastYawCalc, lastXCalc, lastYCalc, lastZCalc
    roll = driver.find_element_by_xpath("//*[@id='roll']/div[1]").text[:-1]
    roll = float(roll)
    rollRate = driver.find_element_by_xpath("//*[@id='roll']/div[2]").text[:-3]
    rollRate = float(rollRate) 
    pitch = driver.find_element_by_xpath("//*[@id='pitch']/div[1]").text[:-1]
    pitch = float(pitch)
    pitchRate = driver.find_element_by_xpath("//*[@id='pitch']/div[2]").text[:-3]
    pitchRate = float(pitchRate)
    yaw = driver.find_element_by_xpath("//*[@id='yaw']/div[1]").text[:-1]
    yaw = float(yaw)
    yawRate = driver.find_element_by_xpath("//*[@id='yaw']/div[2]").text[:-3]
    yawRate = float(yawRate)
    #Get Offset values
    xDist = driver.find_element_by_xpath("//*[@id='x-range']/div[1]").text[:-1]
    xDist = float(xDist)
    yDist = driver.find_element_by_xpath("//*[@id='y-range']/div[1]").text[:-1]
    yDist = float(yDist)
    zDist = driver.find_element_by_xpath("//*[@id='z-range']/div[1]").text[:-1]
    zDist = float(zDist)

    lastRollCalc = time.time()
    lastPitchCalc = time.time()
    lastYawCalc = time.time()

def updateDistances():
    global xDist, yDist, zDist
    xDist = driver.find_element_by_xpath("//*[@id='x-range']/div[1]").text[:-1]
    xDist = float(xDist)
    yDist = driver.find_element_by_xpath("//*[@id='y-range']/div[1]").text[:-1]
    yDist = float(yDist)
    zDist = driver.find_element_by_xpath("//*[@id='z-range']/div[1]").text[:-1]
    zDist = float(zDist)

def adjustRoll():
    global roll, rollRate, rotSpeed0, rotSpeed3, lastRollCalc
    maxRollSpeed = 0
    #Calculate Rolled distance since last call without website update
    timeSinceLastRoll = time.time() - lastRollCalc
    roll += rollRate * timeSinceLastRoll *-2.6

    #Determine max Rotation speed
    if roll > 5: maxRollSpeed = rotSpeed3
    if roll < 5 and roll > 0: maxRollSpeed = rotSpeed0
    if roll < -5: maxRollSpeed = rotSpeed3 *-1
    if roll > -5 and roll < 0: maxRollSpeed = rotSpeed0 *-1
    #Roll Right if still below max Speed and misaligned
    if rollRate < maxRollSpeed - 0.01 and roll > 0.1:
        rollRight()
        rollRate += 0.1
    #Roll Left if still below max (negative) Speed and misaligned
    if rollRate > maxRollSpeed + 0.01 and roll < -0.1:
        rollLeft()
        rollRate -= 0.1

    #Reduce speed if above max Speed
    if rollRate > maxRollSpeed and roll > 0.1:
        rollLeft()
        rollRate -= 0.1

    if rollRate < maxRollSpeed and roll < -0.1:
        rollRight()
        rollRate += 0.1

    #Stop when within margin
    if rollRate > 0 and (roll == 0 or roll == 0.1): 
        rollLeft() 
        rollRate -= 0.1
    if rollRate < 0 and (roll == 0 or roll == -0.1): 
        rollRight()
        rollRate += 0.1
    #Start timer to calculate flown distance since last calculation
    lastRollCalc = time.time()

def adjustPitch():
    global pitch, pitchRate, rotSpeed0, rotSpeed3, lastPitchCalc
    maxPitchSpeed = 0
    #Calculate Pitched distance since last call without website update
    timeSinceLastPitch = time.time() - lastPitchCalc
    pitch += pitchRate * timeSinceLastPitch *-2.6

    #Determine max Rotation speed
    if pitch > 5: maxPitchSpeed = rotSpeed3
    if pitch < 5 and pitch > 0: maxPitchSpeed = rotSpeed0
    if pitch < -5: maxPitchSpeed = rotSpeed3 *-1
    if pitch > -5 and pitch < 0: maxPitchSpeed = rotSpeed0 *-1
    #pitch Right if still below max Speed and misaligned
    if pitchRate < maxPitchSpeed - 0.01 and pitch > 0.1:
        pitchDown()
        pitchRate += 0.1
    #pitch Left if still below max (negative) Speed and misaligned
    if pitchRate > maxPitchSpeed + 0.01 and pitch < -0.1:
        pitchUp()
        pitchRate -= 0.1

    #Reduce speed if above max Speed
    if pitchRate > maxPitchSpeed and pitch > 0.1:
        pitchUp()
        pitchRate -= 0.1

    if pitchRate < maxPitchSpeed and pitch < -0.1:
        pitchDown()
        pitchRate += 0.1

    #Stop when within margin
    if pitchRate > 0 and (pitch == 0 or pitch == 0.1): 
        pitchUp() 
        pitchRate -= 0.1
    if pitchRate < 0 and (pitch == 0 or pitch == -0.1): 
        pitchDown()
        pitchRate += 0.1
    #Start timer to calculate flown distance since last calculation
    lastpitchCalc = time.time()

def adjustYaw():
    global yaw, yawRate, rotSpeed0, rotSpeed3, lastYawCalc
    maxYawSpeed = 0
    #Calculate yawed distance since last call without website update
    timeSinceLastYaw = time.time() - lastYawCalc
    yaw += yawRate * timeSinceLastYaw *-2.6

    #Determine max Rotation speed
    if yaw > 5: maxYawSpeed = rotSpeed3
    if yaw < 5 and yaw > 0: maxYawSpeed = rotSpeed0
    if yaw < -5: maxYawSpeed = rotSpeed3 *-1
    if yaw > -5 and yaw < 0: maxYawSpeed = rotSpeed0 *-1
    #yaw Right if still below max Speed and misaligned
    if yawRate < maxYawSpeed - 0.01 and yaw > 0.1:
        yawRight()
        yawRate += 0.1
    #yaw Left if still below max (negative) Speed and misaligned
    if yawRate > maxYawSpeed + 0.01 and yaw < -0.1:
        yawLeft()
        yawRate -= 0.1

    #Reduce speed if above max Speed
    if yawRate > maxYawSpeed and yaw > 0.1:
        yawLeft()
        yawRate -= 0.1

    if yawRate < maxYawSpeed and yaw < -0.1:
        yawRight()
        yawRate += 0.1

    #Stop when within margin
    if yawRate > 0 and (yaw == 0 or yaw == 0.1): 
        yawLeft() 
        yawRate -= 0.1
    if yawRate < 0 and (yaw == 0 or yaw == -0.1): 
        yawRight()
        yawRate += 0.1
    #Start timer to calculate flown distance since last calculation
    lastYawCalc = time.time()


def adjustX():
    global xDist, xRate, fast, slow, dock, lastXCalc
    maxXSpeed = 0
    #Calculate flown distance since last call without website update
    if xDist > 50: maxXSpeed = fast
    if xDist < 50 and xDist > 0: maxXSpeed = slow
    if xDist < 7 and xDist > 0: maxXSpeed = dock
    if xDist < -50: maxXSpeed = fast *-1
    if xDist < -7 and xDist > -50: maxXSpeed = slow *-1
    if xDist > -7 and xDist < 0: maxXSpeed = dock *-1

    #Accellerate
    if xRate < maxXSpeed and xDist > 0.1:
        Forward()
        xRate += 1

    if xRate > maxXSpeed and xDist < -0.1:
        Backward()
        xRate -= 1

    #Reduce speed if above max Speed
    if xRate > maxXSpeed and xDist > 0.1:
        Backward()
        xRate -= 1

    if xRate < maxXSpeed and xDist < -0.1:
        Forward()
        xRate += 1

    #Stop when within margin
    if xRate > 0 and (xDist == 0 or xDist == 0.1): 
        Backward() 
        xRate -= 1
    if xRate < 0 and (xDist == 0 or xDist == -0.1): 
        Forward()
        xRate += 1

def adjustY():
    global yDist, yRate, fast, slow, dock, lastYCalc
    maxYSpeed = 0
    #Calculate flown distance since last call without website update
    if yDist > 70: maxYSpeed = fast
    if yDist < 70 and yDist > 5: maxYSpeed = slow
    if yDist < 5 and yDist > 0: maxYSpeed = dock
    if yDist < -70: maxYSpeed = fast *-1
    if yDist < -5 and yDist > -70: maxYSpeed = slow *-1
    if yDist > -5 and yDist < 0: maxYSpeed = dock *-1

    #Accellerate
    if yRate < maxYSpeed and yDist > 0.0:
        Left()
        yRate += 1

    if yRate > maxYSpeed and yDist < -0.0:
        Right()
        yRate -= 1

    #Reduce speed if above max Speed
    if yRate > maxYSpeed and yDist > 0.0:
        Right()
        yRate -= 1

    if yRate < maxYSpeed and yDist < -0.0:
        Left()
        yRate += 1

    #Stop when within margin
    if yRate > 0 and (yDist == 0 or yDist == 0.0): 
        Right() 
        yRate -= 1
    if yRate < 0 and (yDist == 0 or yDist == -0.0): 
        Left()
        yRate += 1

def adjustZ():
    global zDist, zRate, fast, slow, dock, lastZCalc
    maxZSpeed = 0
    #Calculate flown distance since last call without website update
    if zDist > 70: maxZSpeed = fast
    if zDist < 70 and zDist > 5: maxZSpeed = slow
    if zDist < 5 and zDist > 0: maxZSpeed = dock
    if zDist < -70: maxZSpeed = fast *-1
    if zDist < -5 and zDist > -70: maxZSpeed = slow *-1
    if zDist > -5 and zDist < 0: maxZSpeed = dock *-1

    #Accellerate
    if zRate < maxZSpeed and zDist > 0.1:
        Down()
        zRate += 1

    if zRate > maxZSpeed and zDist < -0.1:
        Up()
        zRate -= 1

    #Reduce speed if above max Speed
    if zRate > maxZSpeed and zDist > 0.1:
        Up()
        zRate -= 1

    if zRate < maxZSpeed and zDist < -0.1:
        Down()
        zRate += 1

    #Stop when within margin
    if zRate > 0 and (zDist == 0 or zDist == 0.1): 
        Up() 
        zRate -= 1
    if zRate < 0 and (zDist == 0 or zDist == -0.1): 
        Down()
        zRate += 1

###Programm Start###
updateValues()
programLoop = True
updateTimer = time.time()

print("Startup complete - Engaging Autopilot")
while programLoop:
    #Checks if program run conditions are true
    programLoop = roll <= 0.1 or roll >= -0.1 or pitch <= 0.1 or pitch >= -0.1 or yaw <= 0.1 or yaw >= -0.1 or xDist > 0.1 or yDist > 0.1 or zDist > 0.1 or pitchRate > 0 or pitchRate > 0 or yawRate > 0 

    if(time.time() - updateTimer >= 2):
        updateValues()
        updateTimer = time.time()

    if roll < 3 and roll > -3:
         updateValues()
    adjustRoll()
    adjustPitch()
    adjustYaw()


    rollCheck = roll <= 0.1 and roll >= -0.1
    pitchCheck = pitch <= 0.1 and pitch >= -0.1
    yawCheck = yaw <= 0.1 and yaw >= -0.1
    allCheck = rollCheck and pitchCheck and yawCheck

    if allCheck:
        time.sleep(0.05)
        adjustX()
        adjustY()
        adjustZ()
        updateDistances()

    time.sleep(0.15)