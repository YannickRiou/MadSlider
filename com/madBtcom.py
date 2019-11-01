###
# madBtcom.py
# Communication thread to speak with smartphone and get/send command.
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Raspberry pi based
import RPi.GPIO as GPIO

# Python utilities
from time import sleep
from threading import Thread
from Queue import Queue

# Bluetooth library
import bluetooth

class btComThread(Thread):
    def __init__(self,msgQ):
        Thread.__init__(self)
        self.server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.server_sock.bind(("",bluetooth.PORT_ANY))
        self.server_sock.listen(bluetooth.PORT_ANY)
        self.data =""
        self.msgQueue = msgQ

        # List of data that can be received
        # Can be simple travel for video, steps for timelapse with a given interval in secs
        self.cmd=0      

        #Wait for connection from smartphone
        self.client_sock,self.address = self.server_sock.accept()
        print "Accepted connection from ",self.address  

    # Run loop as long as the phone didn't send "quit" command
    def run(self): 
        while 'quit' not in self.data:       
            self.data = self.client_sock.recv(2048)
            #self.client_sock.send(self.data)
            print "rcv : ", self.data
            # Add the received command to the main Queue to be handled 
            # by madSlider main routine 
            self.msgQueue.put(self.data)
            print "Queue size :", self.msgQueue.qsize()
            	
        print 'Quitting'
        self.client_sock.close()
        self.server_sock.close()   
            
