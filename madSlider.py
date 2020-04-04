###
# madSlider.py
# Main file that control and launch thread
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# raspberry pi based
import RPi.GPIO as GPIO

# Python utility
from time import sleep
from queue import *
from threading import Thread

# Utility to launch shell commands
from subprocess import call

# Parsing utilities
import re

# Project packages to handle motors, screen and communication
#from ui.madUi import UIThread
from motor.madMotor import motorThread
from com.madBtcom import btComRcvThread
from battery.madBattery import batteryThread

#from com.madWificom import wifiComThread

if __name__ == '__main__':

    # Message queue to handle communication request
    msgQueue = Queue()

    # Task queue to handle command to motor and UI
    motorTaskQueue = Queue()
    comSendQueue = Queue()
    #uiTaskQueue = Queue()

    #Create Threads to handle UI, motor control and communication
    # (BT for smartphone and wifi for camera)
    #uiThread = UIThread(uiTaskQueue)
    motorThread = motorThread(motorTaskQueue,comSendQueue)
    btComRcvThread = btComRcvThread(msgQueue,comSendQueue)
    batteryThread = batteryThread(comSendQueue)
    #wifiComThread = wifiComThread(msgQueue)

    # Give threads more meaningful names
    #uiThread.setName('User Interface Thread')
    motorThread.setName('Motor Movement Thread')
    btComRcvThread.setName('Bluetooth Communication Receive Thread')
    batteryThread.setName('Battery level checker thread')
    #wifiComThread.setName('Wifi Communication Thread')

    # Start all threads beginning with the Bluetooth communication thread
    btComRcvThread.start()
    #uiThread.start()

    motorThread.start()
    #wifiComThread.start()

    batteryThread.start()

    # Boolean to keep track of the running state of the main loop
    runMainLoop = True

    # Main running loop that wait for messages from btComThread and give task to
    # uiThread, motorThread and send message to wifiComThread
    while runMainLoop :
        try:
          # Verify the command sent by the smartphone
          msg = msgQueue.get()

          # Msg is like this: [cmd],parameter1, parameter2, parameterx
          #cmd can be mv (move), tl (timelapse), tr (travel)
          cmd =  re.findall('\[([a-zA-Z]*)\]',msg)[0]

          if "quit" in msg :
            print ("received quit, sending quit to thread")
            runMainLoop = False
            motorTaskQueue.put(msg)

          #TODO: Cleanup...
          elif  "mv" in cmd or "tl" in cmd or "tr" in cmd or "getpos" in cmd or "mvTo":
            print ("Command received for Motor ! ")
            motorTaskQueue.put(msg)

        except Exception as e:
          print("Oops error occured from madSlider.py  : ", e)

    # If the system is shutting down, wait for all the threads to quit and stop
    #uiThread.join()
    #wifiComThread.join()
    motorThread.join()
    btComRcvThread.join()

    # Everything went well, now shutdown the pi
    # so we can disconnect the battery
    #call("sudo shutdown -h now", shell=True)
