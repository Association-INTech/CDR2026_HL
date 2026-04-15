import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class GPIORead:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def getPinInput(self):
        return GPIO.input(self.pin)