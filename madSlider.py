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
from Queue import Queue
from threading import Thread

# Utility to launch shell commands
import subprocess

# Parsing utilities
import re

# Project packages to handle motors, screen and communication
#from ui.madUi import UIThread
#from motor.madMotor import MotorThread
from com.madBtcom import btComThread
#from com.madWificom import wifiComThread

if __name__ == '__main__':

    # Message queue to handle communication request
    msgQueue = Queue(maxsize = 10)

    # Task queue to handle command to motor and UI
    motorTaskQueue = Queue(maxsize = 10)
    uiTaskQueue = Queue(maxsize = 10)

    #Create Threads to handle UI, motor control and communication
    # (BT for smartphone and wifi for camera)
    #uiThread = UIThread(uiTaskQueue)
    #motorThread = MotorThread(motorTaskQueue)
    btComThread = btComThread(msgQueue)
    #wifiComThread = wifiComThread(msgQueue)

    # Give threads more meaningful names
    #uiThread.setName('User Interface Thread')
    #motorThread.setName('Motor Movement Thread')
    btComThread.setName('Bluetooth Communication Thread')
    #wifiComThread.setName('Wifi Communication Thread')

    # Start all threads beginning with the Bluetooth communication thread
    btComThread.start()
    #uiThread.start()
    #motorThread.start()
    #wifiComThread.start()

    # Boolean to keep track of the running state of the main loop
    runMainLoop = True

    # Main running loop that wait for messages from btComThread and give task to 
    # uiThread, motorThread and send message to wifiComThread
    while btComThread.is_alive() :
	try:
        	# Verify the command sent by the smartphone
        	msg = msgQueue.get()

        	# Msg is like this: [cmd],parameter1, parameter2, parameterx
        	#cmd can be mv (move), tl (timelapse), tr (travel)
        	cmd =  re.findall('\[([a-z]*)\]',msg)[0]
        	print(cmd)
	except :
		print("Oops error occured.")

    # If the system is shutting down, wait for all the threads to quit and stop
    #motorThread.join()
    #uiThread.join()
    btComThread.join()
    #wifiComThread.join()
   
    # Everything went well, now shutdown the pi 
    # so we can disconnect the battery
    #subprocess.call(["shutdown", "-h", "now"])
