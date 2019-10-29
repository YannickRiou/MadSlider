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


#Define GPIO pinout 
#Enable the driver when this pin is LOW
EN =  11 #GPIO 23 #BCM 11
#Direction of rotation 
DIR = 26 #GPIO 37 #BCM 26
#A 1 and 0 on this pin make the motor go forward 1 step
STEP = 19 #GPIO 35 #BCM 19

# Pin connected to start switch to initialize the position
START = 12 # GPIO 32 # BCM 12

class motorThread(Thread):

    def programMove(self, quitEvt,numberOfStep,dir, interval):
        GPIO.output(EN, GPIO.LOW)
        if dir:
            GPIO.output(DIR, GPIO.LOW)
        else:
            GPIO.output(DIR, GPIO.HIGH)

        for i in range(1,numberOfStep) :
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.0001)
            GPIO.output(STEP,GPIO.HIGH)
            sleep(interval)
            if quitEvt.wait(0) :
                print "QUIT EVENT"
                return 0
        #Take a picture -> send message to wifiComThread

    def __init__(self, taskQ):
        Thread.__init__(self)
        self.taskQueue = taskQ
        #Stepper motor TMC2208 Pin definition
        GPIO.setmode(GPIO.BCM)
    
        #Stepper motor TMC2208 Pin configuration
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(EN, GPIO.OUT)

        #Disable the stepper driver
        GPIO.output(EN, GPIO.HIGH)

        # Variable to tell when the motor is moving
        self.motorActive = True  

        self.task ="" 
        self.parsedMsg ="" 
        self.cmd =""
        self.numberOfStep = 0
        self.dir = 0
        self.interval = 0 
        self.killPill = Event()

        
   
    def run(self): 
        while True : 
            try:       
                print"waity for Q"
                self.task = self.taskQueue.get()
                if "quit" in self.task :
                    self.killPill.set()
                    GPIO.cleanup()   
                    print "Quitting motor Thread"
                    return 0
               
                self.parsedMsg =  re.findall('\[([a-z]*)\],([0-9999]*),([0-9999]*),([0-999].[0-9999]*)',self.task)
                self.cmd = self.parsedMsg[0][0]
                self.numberOfStep = int(self.parsedMsg[0][1])
                self.dir = int(self.parsedMsg[0][2])
                self.interval = float(self.parsedMsg[0][3])
                
                self.runningTask = Thread(target=self.programMove, args=(self.killPill, self.numberOfStep,self.dir, self.interval,))
                self.runningTask.start()
                #self.programMove(self.killPill,self.numberOfStep,self.dir,self.interval)

            except Exception as e:
                print("Oops error occured. : ", e)

        

   
