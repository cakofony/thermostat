from climate import ClimateControlSingleton
from thermometer import ThermometerSingleton
from settings import Settings
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import thermweb
from thermweb import therm_app
from lcd_display import LCDPlate
from controller import ThermostatController

#thermostat setup
thermometer = ThermometerSingleton(1)
thermometer.register_observer(thermweb)
thermometer.running = True
thermometer.start()

#set up climate control
climate_control = ClimateControlSingleton()
climate_control.register_observer(thermweb)

config = Settings()
config.register_observer(thermweb)
thermweb.conf = config

lcd = LCDPlate()
climate_control.register_observer(lcd)
thermometer.register_observer(lcd)
climate_control.notify_observers()

control = ThermostatController()
control.climate_control = climate_control
thermometer.register_observer(control)
config.register_observer(control)
config.notify_observers()

http_server = WSGIServer(('0.0.0.0', 80), therm_app, handler_class=WebSocketHandler)

def close_nicely():
    print '\nClosing\n'
    config.save()
    thermometer.running = False
    thermometer.remove_observer(thermweb)
    lcd.off()

try:
    http_server.serve_forever()
except KeyboardInterrupt:
    close_nicely()
except:
    close_nicely()
