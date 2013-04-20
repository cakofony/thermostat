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

    def get_temp(self):
        return random.randint(50,100)

    def notify_observers(self):
        temp = self.get_temp()
        for o in self.observers:
            o.update_temperature(temp)

    def start(self):
        self.notify_observers()
        if self.running:
            threading.Timer(self.update_interval, self.start).start()


