import time as t
import smbus
import sys

DEVICE_BUS = 1
DEVICE_ADDR = 0x10
RELAY_ON = 0xFF
RELAY_OFF = 0x00
bus = smbus.SMBus(DEVICE_BUS)

print("turning relay #1 on")
bus.write_byte_data(DEVICE_ADDR, 1, RELAY_ON)
t.sleep(1)

print("turning relay #1 off")
bus.write_byte_data(DEVICE_ADDR, 1, RELAY_OFF)
t.sleep(1)

print("exiting")