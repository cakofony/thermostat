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

    temp = -30
    target_heat = False
    target_cool = False

    def __init__(self):
        #thermostat setup
        self.thermometer = ThermometerSingleton(1)
        self.thermometer.register_observer(thermweb)
        self.thermometer.running = True
        self.thermometer.start()


        #set up climate control
        self.climate_control = ClimateControlSingleton()

        self.climate_control.register_observer(thermweb)
        self.climate_control.notify_observers()
        #^ otherwise web doesn't know status until a change is made

        self.config = Settings()
        self.config.register_observer(thermweb)
        thermweb.conf = self.config
        self.config.register_observer(self)
        self.thermometer.register_observer(self)
        
        self.lcd = LCDPlate()
        self.climate_control.register_observer(self.lcd)
        self.thermometer.register_observer(self.lcd)

        self.http_server = WSGIServer(('0.0.0.0', 5000), therm_app, handler_class=WebSocketHandler)

        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            self.close_nicely()
        except:
            self.close_nicely()

    def close_nicely(self):
        print '\nClosing\n'
        self.config.save()
        self.thermometer.running = False
        self.thermometer.remove_observer(thermweb)
        self.lcd.off()

    def evaluate_control(self):
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
            self.climate_control.set_off()
        
        if self.config.fan:
            self.climate_control.fan_on()
        elif not (self.climate_control.ac or self.climate_control.heat):
            self.climate_control.fan_off()

    def settings_changed(self, config):
        self.evaluate_control()

    def update_temperature(self, temp):
        self.temp = temp
        self.evaluate_control()
        

control = ThermostatController()
