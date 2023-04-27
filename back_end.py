#!/usr/bin/env python3
import tkinter as tk
import time
import smbus
from spidev import SpiDev
import subprocess
import csv
import threading

# display strings
RECORD_IDLE = "Record"
RECORD_ACTIVE = "Recording..."
DHUMID_IDLE = "Start"
DHUMID_ACTIVE = "Stop"
EXPORT_IDLE = "Export"
EXPORT_ACTIVE = "Exporting..."
RH_SUFFIX = "%"
TEMP_SUFFIX = "°C"

#export data stuff
CSV_FIELDS = ['Time', 'RH', 'Temp. (C)']
CSV_ROWS = [] # will be populated with lists of 3 (timestamp, rh, temp)
CSV_ROWS_LOCK = threading.Lock()
RECORDING_DATA = False
RECORDING_THREAD = None

#rh probe stuff
SHT30_PROBE_0 = 1
SHT30_PROBE_1 = 0
SHT30_RH = 0
SHT30_TF = 1
SHT30_TC = 2

# relay stuff
PUMP_ON = True
PUMP_OFF = False
RELAY_ON = 0xFF
RELAY_OFF = 0x00
RELAY_ADDR = 0x10
RELAY_BUS = 1


class MCP3008:
	def __init__(self, bus = 0, device = 0):
		self.bus, self.device = bus, device
		self.spi = SpiDev()
		self.open()
		self.spi.max_speed_hz = 1000000 #1MHz

	def open(self):
		self.spi.open(self.bus, self.device)
		self.spi.max_speed_hz = 1000000 #1MHz

	def read(self, channel = 0):
		adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
		data = ((adc[1] & 3) << 8) + adc[2]
		return data

	def close(self):
		self.spi.close()


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def export_button(tvar: tk.StringVar, button: tk.Button, frame):
    if tvar.get() == EXPORT_IDLE:
        # set the button label to active
        tvar.set(EXPORT_ACTIVE)
        # deactivate button
        button.configure(state=tk.DISABLED)

        # print message --todo make LOG
        print("Exporting...")

        # wait for 1 second -- todo add functionnality here
        time.sleep(5)
        if usb_availiable():
            export_thread = threading.Thread(target=record_thread)
            export_thread.join()
        else:
            frame.update_messages(message="Can't Export: Couldn't find a USB drive")

        # reset the button label
        tvar.set(EXPORT_IDLE)

        # reactivate the button
        button.configure(state=tk.NORMAL)

        # print message --todo make LOG
        print("Export complete")
    else:
        # print message -- todo make LOG
        print("Button error - pressed while active status")


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def dehumidifcation_button(tvar: tk.StringVar, button: tk.Button):
    if tvar.get() == DHUMID_ACTIVE:
        tvar.set(DHUMID_IDLE)
        print("Dehumidification complete...")
    else:
        tvar.set(DHUMID_ACTIVE)
        print("Dehumidifying...")


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def record_button(tvar: tk.StringVar, button: tk.Button):
    global RECORDING_THREAD
    # recording is in progress
    if tvar.get() == RECORD_ACTIVE:
        # tell the thread to break its loop
        RECORDING_THREAD.do_run = False
        # wait for the thread to exit
        RECORDING_THREAD.join()
        # set the global pointer to None
        RECORDING_THREAD = None
         # update the text on the record button to the idle message
        tvar.set(RECORD_IDLE) # "Begin Recording"
        # update the log
        print("Record complete")
    # recording is not in progress
    else:
        # ensure the global pointer isn't refrencing an active thread
        if RECORDING_THREAD is not None:
            #send error message to log
            print("Recording is already in progress")
            return -1
        # set the global variable to a new recording thread instance
        RECORDING_THREAD = threading.Thread(target=record_thread)
        # start the new thread
        RECORDING_THREAD.start()
        # set the button text to the active message
        tvar.set(RECORD_ACTIVE) # "Stop Recording"
        # send message to the log
        print("Recording...")


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def get_sht30(probe, data_type):
    if probe == SHT30_PROBE_0:
        bus = smbus.SMBus(SHT30_PROBE_0)
    elif probe == SHT30_PROBE_1:
        bus = smbus.SMBus(SHT30_PROBE_1)
    else:
        #todo raise error
        return -1
    
    # write instruction to record data
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])

    # wait for data to be recorded
    time.sleep(1)

    # read data that was recorded
    data = bus.read_i2c_block_data(0x44, 0x00, 6)
    
    #calculate data required
    if data_type is SHT30_RH:
        data =  100 * (data[3] * 256 + data[4]) / 65535.0
    elif data_type == SHT30_TC:
        data = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    elif data_type == SHT30_TF:
        data = (((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45) * 1.8 +32
    else:
        #todo -> error
        return -1
    return data


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def toggle_pump(mode):
    bus = smbus.SMBus(RELAY_BUS)
    if mode is PUMP_ON:
        print("turning relay #1 on")
        bus.write_byte_data(RELAY_ADDR, 1, RELAY_ON)
        #time.sleep(1)
    elif mode is PUMP_OFF:
        print("turning relay #1 off")
        bus.write_byte_data(RELAY_ADDR, 1, RELAY_OFF)
        #time.sleep(1)
    else:
        #todo raise error
        return -1


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def read_MCP3008(chnl):
    adc = MCP3008()

    value = adc.read( channel = chnl)#0 for solvent %, 2 for temperature

    voltage =  (value/ 1023.0 * 3.3)

    #todo find equation for solvent % and temp from data sheet
    if chnl == 0:
        data = voltage
    elif chnl == 2:
        data = voltage
    else:
        #todo error
        return -1

    return data


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def record_thread():
    start_time = time.time()
    global CSV_ROWS
    global CSV_ROWS_LOCK
    t = threading.currentThread()

    with CSV_ROWS_LOCK:
        while getattr(t, "do_run", True):
            # populate a new data point for the CSV file
            CSV_ROWS.append([
                        (time.time()-start_time), 
                        get_sht30(SHT30_PROBE_1, SHT30_RH),
                        get_sht30(SHT30_PROBE_1, SHT30_TC)])
            # wait one second
            time.sleep(1)


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def export_thread():
    pass

'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def usb_availiable():
    return False