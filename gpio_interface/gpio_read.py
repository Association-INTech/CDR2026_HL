import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class GPIORead:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)
        
    def getPinOutput(self, pin):
        return GPIO.input(pin)