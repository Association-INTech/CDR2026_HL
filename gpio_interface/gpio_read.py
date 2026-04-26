import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class GPIORead:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def getPinInput(self):
        return GPIO.input(self.pin)

if __name__ == "__main__":
    TIRETTEPIN = 20
    SIDE_SWITCH_PIN = 14
    tirette = GPIORead(TIRETTEPIN)
    side_switch = GPIORead(SIDE_SWITCH_PIN)
    while True:
        print(f"Tirette: {tirette.getPinInput()}, Side Switch: {side_switch.getPinInput()}")