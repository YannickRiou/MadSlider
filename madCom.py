#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import bluetooth
import subprocess

from threading import Thread

class ComThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.server_sock.bind(("",bluetooth.PORT_ANY))
        self.server_sock.listen(bluetooth.PORT_ANY)
        self.data =""
        self.client_sock,self.address = self.server_sock.accept()
        print "Accepted connection from ",self.address

        
   

    def run(self): 
        while "quit" not in self.data:       
            self.data = self.client_sock.recv(1024)
            self.client_sock.send(self.data)
            print "received [%s]" % self.data
        self.client_sock.close()
        self.server_sock.close()
            
            
