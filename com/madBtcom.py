###
# madBtcom.py
# Communication thread to speak with smartphone and get/send command.
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Raspberry pi based
import RPi.GPIO as GPIO

# Python utility 
from time import sleep
from threading import Thread

# Bluetooth library
import bluetooth

class btComThread(Thread):
    def __init__(self,taskQ):
        Thread.__init__(self)
        self.server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.server_sock.bind(("",bluetooth.PORT_ANY))
        self.server_sock.listen(bluetooth.PORT_ANY)
        self.data =""
        self.taskQueue = taskQ

        # List of data that can be received
        # Can be simple travel for video, steps for timelapse with a given interval in secs
        self.cmd=""
        # number of steps to move
        self.nbSteps=""
        #Delay between steps
        self.interval=""
        
        #Wait for connection from smartphone
        self.client_sock,self.address = self.server_sock.accept()
        print "Accepted connection from ",self.address  

    # Run loop as long as the phone didn't send "quit" command
    def run(self): 
        while "quit" not in self.data:       
            self.data = self.client_sock.recv(1024)
            self.client_sock.send(self.data)
            print "received [%s]" % self.data
        self.client_sock.close()
        self.server_sock.close()
            
            
