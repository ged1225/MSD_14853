#!/usr/bin/env python3
import tkinter as tk
import time
import smbus
from spidev import SpiDev
import subprocess
import csv
import threading
import re
import os
import datetime as dt

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
BASE_ADDR = '/media/ossila-chamber/'
CSV_ROWS = [] # will be populated with lists of 3 (timestamp, rh, temp)
CSV_ROWS_LOCK = threading.Lock()
RECORDING_DATA = False

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
def export_button(tvar: tk.StringVar, button: tk.Button, frame: tk.Frame):
    global CSV_ROWS
    global CSV_ROWS_LOCK
    
    if tvar.get() == EXPORT_IDLE:
        # set the button label to active
        tvar.set(EXPORT_ACTIVE)
        
        # deactivate button
        button.configure(state=tk.DISABLED)

        with CSV_ROWS_LOCK:
            if not CSV_ROWS:
                frame.update_messages("No data to export!")
                return 0
        if RECORDING_DATA:
            frame.update_messages("Cannot export while recording!")
            return 0

        # wait for 1 second -- todo add functionnality here
        if usb_availiable():
            write_csv(frame=frame)
        else:
            frame.update_messages(message="Cannot Export: Couldn't find a USB drive")

        # reset the button label
        tvar.set(EXPORT_IDLE)

        # reactivate the button
        button.configure(state=tk.NORMAL)

    else:
        # print message -- todo make LOG
        frame.update_messages("Button error - pressed while active status")


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def dehumidifcation_button(tvar: tk.StringVar, frame: tk.Frame):
    if tvar.get() == DHUMID_ACTIVE:
        tvar.set(DHUMID_IDLE)
        set_relay(RELAY_OFF)
        frame.update_messages("Dehumidification complete (relay 0 deactivated)")
    elif tvar.get() == DHUMID_IDLE:
        tvar.set(DHUMID_ACTIVE)
        set_relay(RELAY_ON)
        frame.update_messages("Beginning dehumidification (relay 0 deactivated)")

'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def set_relay(mode: int):
    bus = smbus.SMBus(RELAY_BUS)
    if mode == RELAY_OFF:
        #off
        bus.write_byte_data(RELAY_ADDR, 1, RELAY_OFF)
    elif mode == RELAY_ON:
        #on
        bus.write_byte_data(RELAY_ADDR, 1, RELAY_ON)
    else:
        #error
        pass


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def record_button(tvar: tk.StringVar, frame: tk.Frame):
    global RECORDING_DATA
    global CSV_ROWS
    global CSV_ROWS_LOCK

    # recording is in progress
    if tvar.get() == RECORD_ACTIVE:
        #stop recording
        tvar.set(RECORD_IDLE)
        with CSV_ROWS_LOCK:
            frame.update_messages("Recording stopped, data recorded: " + str(CSV_ROWS))
        RECORDING_DATA = False
    # recording is not in progress
    elif tvar.get() == RECORD_IDLE:
        tvar.set(RECORD_ACTIVE)
        # check for usb port
        frame.update_messages("Recording active.")
        RECORDING_DATA = True
    #error case
    else:
        #start recording
        frame.update_messages("Error in [back_end.py-record_button]: unrecognized button text.")


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
def write_csv(frame: tk.Frame):
    global BASE_ADDR
    global CSV_FIELDS
    global CSV_ROWS

    try:
        usb_path = str(os.listdir(BASE_ADDR)[0]) + '/'
    except IndexError:
        frame.update_messages("USB connection unstable! No touchy!")
        return 0

    #print('usd drive list ' + str(usb_drive_name))

    csv_name = dt.datetime.now().strftime('%m-%d-%Y_%H-%M-%S') + ".csv"

    frame.update_messages("Attempting to export to " + csv_name + " in mount " + usb_path)

    with open(("/media/ossila-chamber/"+ usb_path + csv_name), 'w', newline='') as file:
        writer = csv.writer(file, dialect="excel")
        writer.writerow(CSV_FIELDS)
        for row in CSV_ROWS:
            writer.writerow(row)

    frame.update_messages("Export successful!")

'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def usb_availiable():
    if os.path.exists('/dev/sda') and os.path.ismount('/mnt') == False:
        return True
    else:
        return False