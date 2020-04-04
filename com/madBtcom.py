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
from queue import *

# Bluetooth library
import bluetooth

runSndThread = True

class btComRcvThread(Thread):
    def __init__(self,msgQ,comSendQ):
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
        print ("Accepted connection from ",self.address)

        self.sendQ = comSendQ

        # Create thread to handle send of telemetry to phone (position, status,etc.)
        self.btComSndThread = btComSndThread(self.sendQ,self.client_sock)
        self.btComSndThread.setName('Bluetooth Communication Send Thread')
        self.btComSndThread.start()


    # Run loop as long as the phone didn't send "quit" command
    def run(self):
        global runSndThread
        while 'quit' not in self.data:
            self.data = self.client_sock.recv(2048).decode()
            #self.client_sock.send(self.data)
            print ("rcv : ", self.data)
            # Add the received command to the main Queue to be handled
            # by madSlider main routine
            self.msgQueue.put(self.data)
            print ("Queue size :", self.msgQueue.qsize())

        print ('==[Quitting Rcv Thread]==')
        runSndThread = False
        self.sendQ.put("[quit]")
        self.btComSndThread.join()
        self.client_sock.close()
        self.server_sock.close()

class btComSndThread(Thread):
    def __init__(self,comSendQ,btSock):
        Thread.__init__(self)
        self.sendQueue = comSendQ
        self.btSendSocket = btSock
        self.msg =""
        self.parsedMsg =""
        self.cmd = ""
        self.pos = 0


    # Run loop as long as the phone didn't send "quit" command
    def run(self):
        global runSndThread
        while runSndThread:
            try:
                self.msg = self.sendQueue.get()
                self.btSendSocket.send(self.msg)
            except Exception as e:
                print("Oops error occured from sendThread  : ", e)

        print ('==[Quitting Send Thread]==')
        return 0
