#!/usr/bin/env python3

import threading, time, random, serial


SERIAL_PORT = "/dev/ttyUSB0"

class SerialHandler(threading.Thread):

    def __init__(self):
        super().__init__()
        self.newInput = False
        self.buttonEvent = tuple()
        self.connected = False
        try: 
            self.__serial = serial.Serial(SERIAL_PORT, 9600, timeout=0.5)
            print("Connected to buttonpanel")
            self.connected = True
        except:
            print("Could not connect to buttonpanel at " + SERIAL_PORT + ". Maybe change port in serial_handler.py?")

    def run(self):
        while self.connected:
            line = self.__serial.readline().decode("utf-8")
            
            if(line != '') and ('start' not in line):
                self.newInput = True
                self.buttonEvent = (line[0],line[1])

            time.sleep(.01)

    def getButtonEvent(self):
        return self.buttonEvent

    def receivedNewInput(self):
        return self.newInput

    def resetInputFlag(self):
        self.newInput = False
