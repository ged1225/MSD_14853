import RPi.GPIO as GPIO

button_gpio_pin = 11

def button_callback(channel):
    print("button was pressed")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(button_gpio_pin, GPIO.RISING, callback=button_callback)

message = input("press enter to quit\n\n")

GPIO.cleanup()
