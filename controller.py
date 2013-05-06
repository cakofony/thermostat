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

from climate import ClimateControlSingleton
from thermometer import ThermometerSingleton
from settings import Settings
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import thermweb
from thermweb import therm_app
from lcd_display import LCDPlate

MAX_THRESHOLD = 2

class ThermostatController:

    temp = None
    target_heat = False
    target_cool = False
    config = None

    def evaluate_control(self):
        if temp is None: #before we read the thermometer, we don't want to cycle AC
            return

        temp = self.temp
        mi = self.config.mint
        ma = self.config.maxt

        if self.config.system:
            if temp < mi:
                self.target_heat = True
                self.climate_control.set_heat_on()
            elif self.target_heat:
                if temp >= min((mi*2+ma)/3, mi+MAX_THRESHOLD):
                    self.target_heat = False
                    self.climate_control.set_off()
                    if not self.config.fan:
                        self.climate_control.fan_off()
            if temp > ma:
                self.target_cool = True
                self.climate_control.set_ac_on()
            elif self.target_cool:
                if temp <= max((ma*2+mi)/3, ma-MAX_THRESHOLD):
                    self.target_cool = False
                    self.climate_control.set_off()
                    if not self.config.fan:
                        self.climate_control.fan_off()
        else:
            target_heat = False
            target_cool = False
            self.climate_control.set_off()
        
        if self.config.fan:
            self.climate_control.fan_on()
        elif not (self.climate_control.ac or self.climate_control.heat):
            self.climate_control.fan_off()

    def settings_changed(self, config):
        self.config = config
        self.evaluate_control()

    def update_temperature(self, temp):
        self.temp = temp
        self.evaluate_control()
