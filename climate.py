"""
Copyright (C) 2013 Carter Kozak c4kofony@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from observable import Observable
import RPi.GPIO as GPIO

class ClimateControlSingleton(Observable):
    _instance = None

    fan = False
    ac = False
    heat = False

    #singleton magic
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ClimateControlSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super(ClimateControlSingleton,self).__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)

    def notify_observers(self):
        if self.ac:
            result = 'cool'
        elif self.heat:
            result = 'heat'
        else:
            result = 'off'
        for o in self.observers:
            o.update_active(result, self.heat, self.cool, self.fan)

    def fan_on(self):
        GPIO.output(17, GPIO.HIGH)
        self.fan = True

    def fan_off(self):
        GPIO.output(17, GPIO.LOW)
        self.fan = False

    def heat_on(self):
        GPIO.output(22, GPIO.LOW)
        self.ac = False
        GPIO.output(27, GPIO.HIGH)
        self.heat = True
    
    def heat_off(self):
        GPIO.output(27, GPIO.LOW)
        self.heat = False
        self.notify_observers()

    def ac_on(self):
        GPIO.output(27, GPIO.LOW)
        self.heat = False
        GPIO.output(22, GPIO.HIGH)
        self.ac = True

    def ac_off(self):
        GPIO.output(22, GPIO.LOW)
        self.ac = False

    #if heat or ac are on, we ALWAYS want to start the fan
    def set_ac_on(self):
        self.heat_off()
        self.ac_on()
        self.fan_on()
        self.notify_observers()

    #if heat or ac are on, we ALWAYS want to start the fan
    def set_heat_on(self):
        self.ac_off()
        self.heat_on()
        self.fan_on()
        self.notify_observers()

    def set_off(self):
        self.ac_off()
        self.heat_off()
        self.notify_observers()
