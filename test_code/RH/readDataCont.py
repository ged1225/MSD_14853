# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# SHT30
# This code is designed to work with the SHT30_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Humidity?sku=SHT30_I2CS#tabs-0-product_tabset-2

import smbus
import time

def main():
	while(True):
		# Get I2C bus
		# bus 1 for relays and first RH probe
		# bus 0 for second rh probe
		bus = smbus.SMBus(0)

		# SHT30 address, 0x44(68)
		# Send measurement command, 0x2C(44)
		#0x06(06) - High repeatability measurement
		bus.write_i2c_block_data(0x44, 0x2C, [0x06])

		time.sleep(0.5)

		# SHT30 address, 0x44(68)
		# Read data back from 0x00(00), 6 bytes
		# cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
		data = bus.read_i2c_block_data(0x44, 0x00, 6)

		# Convert the data
		humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

		# Output data to screen
		print ("Relative Humidity : %.2f %%RH" %humidity)	
		time.sleep(1)

if __name__=="__main__":
	try:
		main ()
	except KeyboardInterrupt:
		print ("\b\bUser called KeyboardInterrupt\nExiting...")
		exit (0)
	else:
		print ("Unexpected Error")
		exit (0)

