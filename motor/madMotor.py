###
# madMotor.py
# Send command to control the motor
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import RPi.GPIO as GPIO

# Python utility
from Queue import Queue
from time import sleep
from threading import Thread, Event


# Parsing utilities
import re

#MAXIMUM STEPS LENGTH : 275000 -> Middle at 137500
MAXPOSITION = 137500

#Define GPIO pinout 
#Enable the driver when this pin is LOW
EN =  11 #GPIO 23 #BCM 11
#Direction of rotation 
DIR = 26 #GPIO 37 #BCM 26
#A 1 and 0 on this pin make the motor go forward 1 step
STEP = 19 #GPIO 35 #BCM 19

# Pin connected to start switch to initialize the position
START = 12 # GPIO 32 # BCM 12

#Position hints 
AWAYFROMSTART = 1
CLOSETOSTART = 0

class motorThread(Thread):

    def makeAStep(self, interval, dir):
        global position
        GPIO.output(STEP, GPIO.LOW)
        sleep(0.01)
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

    def smoothMove (self, msgQueue, start, end):
        global position
        global startEndstop
        step = 0

        #Main routine
        GPIO.output(EN, GPIO.LOW)

        if position > start :
            while position != start :
                GPIO.output(DIR, GPIO.LOW)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.0001)
                GPIO.output(STEP,GPIO.HIGH)
                sleep(0.0001)
                # update position variable
                position = position - 1
        elif position < start:
            while position != start :
                GPIO.output(DIR, GPIO.HIGH)
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.0001)
                GPIO.output(STEP,GPIO.HIGH)
                sleep(0.0001)
                # update position variable
                position = position + 1

        if end > start :
            dir = AWAYFROMSTART
            GPIO.output(DIR, GPIO.HIGH)
            # carriage is going away from the start, increase position
        else:
            dir = CLOSETOSTART
            GPIO.output(DIR, GPIO.HIGH)
            # carriage is going to the start, decrease position

        nbSteps = abs(start - end)
           
        while (step < nbSteps) and msgQueue.empty() and position < MAXPOSITION and position != end and not startEndstop :
            self.makeAStep(0.01,dir)
            step = step + 1

        if startEndstop:
            startEndstop = False
            

    def initMadSliderPos(self):
        global position
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
        startEndstop = True

    def __init__(self, taskQ):
        Thread.__init__(self)
        self.taskQueue = taskQ
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

        GPIO.add_event_detect(START, GPIO.RISING, callback=self.interrupt_handler, bouncetime=200)

        # Variable to tell when the motor is moving
        self.motorActive = True  

        self.startEndstop = False
        self.task ="" 
        self.parsedMsg ="" 
        self.cmd =""
        self.numberOfStep = 0
        self.dir = 0
        self.interval = 0 
        self.runMotorLoop = True
        self.position = 0

        self.initMadSliderPos()
   
    def run(self): 
        while self.runMotorLoop : 
            try:       
                print"waity for Q"
                self.task = self.taskQueue.get()
                print "get : ", self.task
                if 'quit' in self.task :
                    print "KOUKOU"
                    self.runMotorLoop = False
                else:
                    self.parsedMsg =  re.findall('\[([a-z]*)\],',self.task)
                    self.cmd = self.parsedMsg[0]
                    print "Command : ", self.task
                    
                    if self.cmd == "mv" or self.cmd == "tl":
                        print "Command is MV or TL"
                        self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9]*),([0-1]*),([0-9]*\.[0-9]*)',self.task)
                        self.numberOfStep = int(self.parsedMsg[0][1])
                        self.dir = int(self.parsedMsg[0][2])
                        self.interval = float(self.parsedMsg[0][3])
                        self.programMove(self.taskQueue,self.numberOfStep,self.dir,self.interval)
                    if self.cmd == "tr" :
                        print "CMD IS TR"
                        self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9]*),([0-9]*)',self.task)
                        self.smoothMove(self.taskQueue,int(self.parsedMsg[0][1]),int(self.parsedMsg[0][2]))

                   
            except Exception as e:
                print("Oops error occured  : ", e)

        print "quitting"
        GPIO.cleanup() 
        return 0  

   
