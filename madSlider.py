###
# madSlider.py
# Main file launching and managing all thread.
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
from time import sleep

import subprocess
import Queue

from threading import Thread

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib
from luma.oled.device import sh1106

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from ui.madUi import UIThread
from motor.madMotor import MotorThread
from com.madCom import ComThread

#motorMovesQueue = Queue.Queue(maxsize = 10)

#uiThread = UIThread(motorMovesQueue)
#motorThread = MotorThread(motorMovesQueue)
comThread = ComThread()

#uiThread.setName('User Interface Thread')
#motorThread.setName('Motor Movement Thread')

comThread.start()
#uiThread.start()
#motorThread.start()

#motorThread.join()
#uiThread.join()
