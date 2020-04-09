###
# madMotor.py
# Send command to control the motor
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import RPi.GPIO as GPIO

# Python utility
from queue import *
from time import sleep
from threading import Thread, Event


# Parsing utilities
import re


MAXPOSITION = 27319

#Define GPIO pinout
#Enable the driver when this pin is LOW
EN =  15 #GPIO 10 #BCM 15
#Direction of rotation
DIR = 23 #GPIO 16 #BCM 23
#A 1 and 0 on this pin make the motor go forward 1 step
STEP = 18 #GPIO 12 #BCM 18

# Pin connected to start switch to initialize the position
START = 12 # GPIO 32 # BCM 12

#Position hints
AWAYFROMSTART = 1
CLOSETOSTART = 0

class motorThread(Thread):

    def makeAStep(self, interval, dir):
        global position
        GPIO.output(STEP, GPIO.LOW)
        sleep(0.001)
        GPIO.output(STEP,GPIO.HIGH)
        sleep(interval)
        # update position variable
        if dir :
            position = position + 1
        else :
            position = position - 1

    def programMove (self, msgQueue, nbSteps, dir, interval):
        global position
        global startEndstop
        step = 0

        #Main routine
        GPIO.output(EN, GPIO.LOW)

        if dir:
            GPIO.output(DIR, GPIO.HIGH)
            # carriage is going away from the start, increase position
        else:
            GPIO.output(DIR, GPIO.LOW)
            # carriage is going to the start, decrease position


        while (step < nbSteps) and msgQueue.empty() and position < MAXPOSITION and not startEndstop :
            self.makeAStep(interval,dir)
            step = step + 1

        if startEndstop:
            startEndstop = False

    def moveTo (self, msgQueue, sendQueue, pos):
        global position
        global startEndstop
        step = 0

        #Main routine
        GPIO.output(EN, GPIO.LOW)

        if pos > position:
            GPIO.output(DIR, GPIO.HIGH)
            dir = 1
            # goal position is away
        else:
            GPIO.output(DIR, GPIO.LOW)
            dir = 0
            # goal position is toward start

        while (position != pos) and msgQueue.empty() and position < MAXPOSITION and not startEndstop :
            self.makeAStep(0.001,dir)
            if position % 1000 == 0 :
                sendQueue.put("[pos]," + str(position))

        sendQueue.put("[pos]," + str(position))
        if startEndstop:
            startEndstop = False

    def smoothMove (self, msgQueue, start, end, interval):
        global position
        global startEndstop
        step = 0

        #Main routine
        GPIO.output(EN, GPIO.LOW)

        if startEndstop:
            startEndstop = False

        if position > start :
            while position != start :
                GPIO.output(DIR, GPIO.LOW)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.00001)
                GPIO.output(STEP,GPIO.HIGH)
                sleep(0.00001)
                # update position variable
                position = position - 1

        elif position < start:
            while position != start :
                GPIO.output(DIR, GPIO.HIGH)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.00001)
                GPIO.output(STEP,GPIO.HIGH)
                sleep(0.00001)
                # update position variable
                position = position + 1

        if end > start :
            dir = AWAYFROMSTART
            GPIO.output(DIR, GPIO.HIGH)
            # carriage is going away from the start, increase position
        else:
            dir = CLOSETOSTART
            GPIO.output(DIR, GPIO.LOW)
            # carriage is going to the start, decrease position

        nbSteps = abs(start - end)

        while (step < nbSteps) and msgQueue.empty() and position < MAXPOSITION and position != end and not startEndstop :
            self.makeAStep(interval,dir)
            step = step + 1

    def initMadSliderPos(self):
        global position
        global startEndstop
        # Initialize the camera at position 0
        GPIO.output(EN, GPIO.LOW)
        GPIO.output(DIR, GPIO.LOW)
        while (not GPIO.input(START)):
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.0001)
            GPIO.output(STEP,GPIO.HIGH)
            sleep(0.0001)
        position = 0
        startEndstop = False
        GPIO.output(EN, GPIO.HIGH)

    def interrupt_handler (self,channel):
        global startEndstop
        global position
        startEndstop = True
        position = 0

    def __init__(self, taskQ,comQ):
        Thread.__init__(self)
        self.taskQueue = taskQ
        self.comSendQueue = comQ
        #Stepper motor TMC2208 Pin definition
        GPIO.setmode(GPIO.BCM)

        #Stepper motor TMC2208 Pin configuration
        # DIR = 0 go to the start (where the motor is)
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(EN, GPIO.OUT)
        GPIO.setup(START, GPIO.IN)

        #Disable the stepper driver
        GPIO.output(EN, GPIO.HIGH)

        # Variable to tell when the motor is moving
        self.motorActive = True

        self.startEndstop = False
        self.task =""
        self.parsedMsg =""
        self.cmd =""
        self.numberOfStep = 0
        self.goToPos = 0
        self.dir = 0
        self.interval = 0
        self.runMotorLoop = True
        self.position = 0

        GPIO.add_event_detect(START, GPIO.RISING, callback=self.interrupt_handler, bouncetime=200)

    def run(self):
        self.initMadSliderPos()
        while self.runMotorLoop :
            try:
                self.task = self.taskQueue.get()
                #print ("get : ", self.task)
                if 'quit' in self.task :
                    self.runMotorLoop = False
                else:
                    self.parsedMsg =  re.findall('\[([a-zA-Z]*)\],',self.task)
                    self.cmd = self.parsedMsg[0]

                    if self.cmd == "mv":
                        self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9]*),([0-1]*),([0-9]*\.[0-9]*)',self.task)
                        self.numberOfStep = int(self.parsedMsg[0][1])
                        self.dir = int(self.parsedMsg[0][2])
                        self.interval = float(self.parsedMsg[0][3])
                        self.programMove(self.taskQueue,self.numberOfStep,self.dir,self.interval)
                    if self.cmd == "tl":
                        self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9]*),([0-9]*),([0-9]*\.[0-9]*)',self.task)
                        self.smoothMove(self.taskQueue,int(self.parsedMsg[0][1]),int(self.parsedMsg[0][2]),float(self.parsedMsg[0][3]))
                    if self.cmd == "tr" :
                        self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9]*),([0-9]*)',self.task)
                        self.smoothMove(self.taskQueue,int(self.parsedMsg[0][1]),int(self.parsedMsg[0][2]),0.001)
                    if self.cmd == "getpos":
                        print ("Position : ", position)
                    if self.cmd == "mvTo":
                        self.parsedMsg =  re.findall('\[([a-zA-Z]*)\],([0-9]*)',self.task)
                        self.goToPos = int(self.parsedMsg[0][1])
                        self.moveTo(self.taskQueue,self.comSendQueue,self.goToPos)


            except Exception as e:
                print("**Oops error occured from madMotor.py  : ", e)

        print ("==[Quitting motor thread]==")
        GPIO.cleanup()
        return 0
