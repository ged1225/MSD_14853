#import time as t
import smbus
#import sys
import RPi.GPIO as GPIO

# relay i2c globals
DEVICE_BUS = 1
RELAY_ADDR = 0x10
RELAY_ON = 0xFF
RELAY_OFF = 0x00
bus = smbus.SMBus(DEVICE_BUS)
WRITABLE_RELAYS = [1,2,3,4]

# button gpio global
BUTTON_GPIO_PIN = 11


def toggle_relay(relay_n, mode):
    # gate for incorrect mode arguments
    if mode != RELAY_ON and mode != RELAY_OFF:
        raise TypeError("Incorrect relay mode argument in toggle_relay() call")
        exit(0)

    # gate for incorrect relay number
    if relay_n not in WRITABLE_RELAYS:
        raise TypeError("Incorrect relay number argument in toggle_relay() call")
        exit(0)
    
    bus.write_byte_data(RELAY_ADDR, relay_n, mode)

 
def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(BUTTON_GPIO_PIN, GPIO.RISING, callback=lambda *a: toggle_relay(relay_n=1, mode=RELAY_ON))
    print("Press the button to trigger a relay interupt\n\n")
    usr_inp = input("Press enter to exit")
    bus.write_byte_data(RELAY_ADDR, 1, RELAY_OFF)


if __name__ == "__main__":
    main()