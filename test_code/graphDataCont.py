#!/usr/bin/env python3

#read data imports
import smbus
import time

# graph data imports
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Global declarations
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xs = []
ys = []


#this function is called periodically from FuncAnimation
def animate(i, xs, ys):
	# Read RH from SHT30
	rhData = round(readData(), 2)

	# Add a and y to lists
	xs.append(dt.datetime.now().strftime('%S'))
	ys.append(rhData)

	#limit a and y to 20 items
	xs = xs[-20:]
	ys = ys[-20:]

	#draw x and y lists
	ax.clear()
	ax.plot(xs, ys)

	#format plot
	plt.xticks(ha='right')
	plt.subplots_adjust(bottom=0.30)
	plt.title('SHT30 Relative Humidity over Time')
	plt.ylabel('Relative Humidity (%)')
	plt.xlabel('Seconds from Code Begin (s)')

def readData():
	# Get I2C bus
	bus = smbus.SMBus(1)

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
	return 100 * (data[3] * 256 + data[4]) / 65535.0

def main():
	ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
	plt.show()

if __name__=="__main__":
	try:
		main ()
	except KeyboardInterrupt:
		print ("\b\bUser called KeyboardInterrupt\nExiting...")
		exit (0)
	else:
		print ("Unexpected Error")
		exit (0)

