#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep

import subprocess
import Queue

from threading import Thread

EN =  11 #GPIO 23 #BCM 11
DIR = 26 #GPIO 37 #BCM 26
STEP = 19 #GPIO 35 #BCM 19


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

        #Stepper motor TMC2208 Pin configuration
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(EN, GPIO.OUT)

        #Disable the stepper driver
        GPIO.output(EN, GPIO.LOW)

        self.motorActive = True   

    def programMove(self,numberOfStep,dir):
        
        if dir:
            GPIO.output(DIR, GPIO.LOW)
        else:
            GPIO.output(DIR, GPIO.HIGH)

        for i in range(1,numberOfStep) :
            GPIO.output(STEP, GPIO.LOW)
            sleep(0.0001)
            GPIO.output(STEP,GPIO.HIGH)
            sleep(0.0001)

    def run(self): 
        while self.taskQueue.empty() == False:       
            print(self.taskQueue.get(block,1))
            

   
