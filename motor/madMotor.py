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
from threading import Thread

#Define GPIO pinout 
#Enable the driver when this pin is LOW
EN =  11 #GPIO 23 #BCM 11
#Direction of rotation 
DIR = 26 #GPIO 37 #BCM 26
#A 1 and 0 on this pin make the motor go forward 1 step
STEP = 19 #GPIO 35 #BCM 19

# Pin connected to start switch to initialize the position
START = ??

class MotorThread(Thread):
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

    def programMove(self,numberOfStep,dir, interval):
        
        if dir:
            GPIO.output(DIR, GPIO.LOW)
        else:
            GPIO.output(DIR, GPIO.HIGH)

        for i in range(1,numberOfStep) :
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.0001)
            GPIO.output(STEP,GPIO.HIGH)
            sleep(interval)

    def run(self): 
        while self.taskQueue.empty() == False:       
            print(self.taskQueue.get(block,1))
            

   
