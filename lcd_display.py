from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

class LCDPlate():

    def __init__(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.begin(16, 2)
        self.lcd.clear()
        self.lcd.backlight(self.lcd.OFF)

    def update_active(self, result):
        if result == 'cool':
            self.lcd.backlight(self.lcd.BLUE)
        elif result == 'heat':
            self.lcd.backlight(self.lcd.RED)
        elif result == 'off':
            self.lcd.backlight(self.lcd.PURPLE)

    def update_temperature(self, temp):
        self.lcd.clear()
        self.lcd.message("Temp: %.1fF" % temp)

    def off(self):
        self.lcd.backlight(self.lcd.OFF)
        self.lcd.clear()
