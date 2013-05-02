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

import pickle
from observable import Observable
import thread

class Settings(Observable):
    source = None
    def __init__(self):
        super(Settings, self).__init__()
        try:
            self.read()
            self.source=None
        except:
            self.mint = 70
            self.maxt=74
            self.fan=False
            self.system=True
            self.source=None

    def notify_observers(self):
        for o in self.observers:
            o.settings_changed(self)

    def set_all(self, mint, maxt, fan, system, source=None):
        self.mint = mint
        self.maxt = maxt
        self.fan = fan
        self.system = system
        self.source = source
        self.notify_observers()

    def set_fan(self, fan, source=None):
        self.fan = fan
        self.source = source
        self.notify_observers()
    
    def set_system(self, system, source=None):
        self.system = system
        self.source = source
        self.notify_observers()

    def set_min(self, mint, source=None):
        self.mint = mint
        self.source = source
        self.notify_observers()

    def set_max(self, maxt, source=None):
        self.maxt = maxt
        self.source = source
        self.notify_observers()

    def get_fan(self):
        if self.fan:
            return 'on'
        return 'off'

    def get_sys(self):
        if self.system:
            return 'on'
        return 'off'

    def to_dict(self):
        result = {'mintemp':self.mint, 'maxtemp':self.maxt, 'fan':self.get_fan(), 'system':self.get_sys()}
        if self.source:
            result["source"] = self.source
        return result

    def save(self):
        output = open('settings.pkl', 'w')
        for o in self.observers:
            self.remove_observer(o)
        del self.source
        del self.observers
        pickle.dump(self.__dict__, output)
        output.close()

    def read(self):
        inp = open('settings.pkl', 'r')
        self.__dict__ = pickle.load(inp)
        inp.close()
        self.source = None
        self.observers = []
