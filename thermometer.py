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

import threading
import random
import sys
import os
import glob
import time
from observable import Observable

class ThermometerSingleton(Observable):

    _instance = None
    running = False;

    #singleton magic
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThermometerSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, update_interval = 1):
        super(ThermometerSingleton,self).__init__()
        self.update_interval = update_interval

        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            print 'Error reading temp'
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f

    def get_temp(self):
        #return random.randint(50,100)
        return self.read_temp()

    def notify_observers(self):
        temp = self.get_temp()
        for o in self.observers:
            o.update_temperature(temp)

    def start(self):
        self.notify_observers()
        if self.running:
            threading.Timer(self.update_interval, self.start).start()


