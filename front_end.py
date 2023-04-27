#!/usr/bin/env python3

import enum
import getopt
import logging
import sys
import tkinter as tk
import back_end
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib import pyplot as plt, animation
import numpy as np
import time
import threading

# Program name global strings
PROGRAM_NAME = 'Ossila Enviornmental Control'
PROGRAM_FILE_NAME = PROGRAM_NAME + '.py'
LOG_NAME = PROGRAM_NAME + '_log'


# exit codes enumerator
class ExitCode(enum.Enum):
    SUCCESS = 0,
    UNEXPECTED_ERROR = -1,
    KEYBOARD_INTERRUPT = -5,

PADX = 10
PADY = 10

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
BUTTON_HEIGHT = 2
MESSAGE_BOX_HEIGHT=10
MESSAGE_BOX_WIDTH=70

BUTTON_FONT_SIZE = 24
TITLE_FONT_SIZE = 32
DATA_FONT_SIZE = 18

RH_0 = 0.0
RH_1 = 0.0
RH_LOCK = threading.Lock()
TEMP = 0
TEMP_LOCK = threading.Lock()


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry(str(SCREEN_WIDTH)+"x"+str(SCREEN_HEIGHT))
        self.title(PROGRAM_NAME)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        frame = MainFrame(container, self)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.tkraise()

        #frame.update_data_read()


'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
class MainFrame(tk.Frame):
    '''
    @Description:
    @Params:
    @Author: Gabriel Dombrowski (ged1225@g.rit.edu)
    '''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # >>>>>>>>>>>>> Declarations <<<<<<<<<<<<<<
        # title
        self.title_label = tk.Label(self, text='Ossilla Enviornnmental Control System', font=('Times', TITLE_FONT_SIZE))
        
        # labelframe
        self.label_frame = tk.LabelFrame(self, text="Readings", font=('Times', DATA_FONT_SIZE))

        # declare graph stuff
        # used for animation
        graph_frame = tk.LabelFrame(self, text="Relative Humidity", font=('Times', DATA_FONT_SIZE))

        self.xs = [] # time axis
        self.rh_out = [] # data plot #1
        self.rh_in = [] # data plot #2
        self.fig = plt.Figure(figsize=(6, 2)) # declare figure
        # self.x = 20*np.arange(0, 2*np.pi, 0.01)        # x-array
        self.ax = self.fig.add_subplot(111)   # declare a subplot
        # self.line, = self.ax.plot(self.x, np.sin(self.x))        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.start_time = time.time()
        self.ax.set_ylabel('Relative Humidity (%)')
        self.ax.set_xlabel('Seconds from Code Begin (s)')
        self.ax.plot(self.xs, self.rh_in, 'r-', label='Pre-Cyld.')
        self.ax.plot(self.xs, self.rh_out, 'b-', label='Post-Clyd.')
        self.ax.legend()

        # rh in Lableframe
        self.rh_data_var = tk.StringVar(value="--%")
        self.rh_label = tk.Label(self.label_frame, text="Relative Humidity", font=('Times', DATA_FONT_SIZE))
        self.rh_data = tk.Label(self.label_frame, textvariable=self.rh_data_var, font=('Times', BUTTON_FONT_SIZE))

        # temp in Labelframe
        self.temp_label = tk.Label(self.label_frame, text="Temperature", font=('Times', DATA_FONT_SIZE))
        self.temp_data_var = tk.StringVar(value="--°C")
        self.temp_data = tk.Label(self.label_frame, textvariable=self.temp_data_var, font=('Times', BUTTON_FONT_SIZE))
        
        self.button_frame = tk.LabelFrame(self, text='Controls', font=('Times', DATA_FONT_SIZE))

        # start button in button frame
        self.dehumidify_button_tvar = tk.StringVar(value=back_end.DHUMID_IDLE)
        self.dehumidify_button = tk.Button(self.button_frame, height=BUTTON_HEIGHT, font=('Times', BUTTON_FONT_SIZE),
                                    textvariable=self.dehumidify_button_tvar,  
                                    command= lambda: back_end.dehumidifcation_button(tvar=self.dehumidify_button_tvar, 
                                                                    button=self.dehumidify_button))

        # record button in button frame
        self.record_button_tvar = tk.StringVar(value=back_end.RECORD_IDLE)
        self.record_button = tk.Button(self.button_frame, height=BUTTON_HEIGHT, font=('Times', BUTTON_FONT_SIZE),
                                textvariable=self.record_button_tvar,  
                                command= lambda: back_end.record_button(tvar=self.record_button_tvar, 
                                                                    button=self.record_button))

        # Export button in button frame
        self.export_button_tvar = tk.StringVar(value=back_end.EXPORT_IDLE)
        self.export_button = tk.Button(self.button_frame, height=BUTTON_HEIGHT, font=('Times', BUTTON_FONT_SIZE),
                                textvariable=self.export_button_tvar, 
                                command= lambda: back_end.export_button(tvar=self.export_button_tvar, 
                                                                    button=self.export_button, 
                                                                    frame=self))
        
        # message label frame
        self.message_frame = tk.LabelFrame(graph_frame, text="Messages from the system", font=('Times', DATA_FONT_SIZE))

        # Message box
        self.message_counter = 0
        self.message_box = tk.Text(self.message_frame, height=MESSAGE_BOX_HEIGHT, width=MESSAGE_BOX_WIDTH)
        # use -> message_box.insert(tk.End, <string>)

        # >>>>>>>>>>>>> Pack <<<<<<<<<<<<<<
        '''
        ._______________________________________________________.
        |   .____________________.      |       _____________   |
        |   |                    |      |  ____/                |
        |   |     Data Display   |      | /     <RH Graph>      |
        |   |____________________|      |/                      |
        |                               |_____________________  |
        |     >>  Start Button <<                               |
        |                               .____________________.  |
        |     >> Record Button <<       |   Message Box      |  |
        |                               |                    |  |
        |     >> Export Button <<       |____________________|  |
        |_______________________________________________________|
        '''
        #pack labelframe
        self.rh_label.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="ew")
        self.rh_data.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="ew")
        self.temp_label.grid(row=1, column=1, padx=PADX, pady=PADY, sticky="ew")
        self.temp_data.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="ew")

        # pack button frame
        self.dehumidify_button.pack(side='top', expand=True, fill='x', padx=PADX)
        self.record_button.pack(side='top', expand=True, fill='x', padx=PADX)
        self.export_button.pack(side='top', expand=True, fill='x', padx=PADX)

        # pack message frame
        self.message_box.grid(row=0, column=0, padx=PADX, pady=PADY, sticky='nsew')

        # pack window
        self.title_label.grid(row=0, column=0, padx=PADX, pady=PADY, columnspan=5)
        self.label_frame.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="ew", rowspan=2)
        self.button_frame.grid(row=3, column=0, padx=PADX, pady=PADY, sticky='nesw')
       
        # pack graph
        graph_frame.grid(column=1, row=1, padx=PADX, pady=PADY, sticky='nesw', rowspan=3)
        self.canvas.get_tk_widget().pack(padx=PADX, pady=PADY)
        self.message_frame.pack(padx=PADX, pady=PADY)

        # set graph to animate
        self.ani = animation.FuncAnimation(self.fig, self.animate, np.arange(1, 200), interval=25, blit=False)

        #threading
        self.update_thread = threading.Thread(target=self.update_data_read)
        self.update_thread.start()

    '''
    @Description:
    @Params:
    @Author: Gabriel Dombrowski (ged1225@g.rit.edu)
    '''
    def update_messages(self, message):
        self.message_box.insert('1.0', ("(" + str(self.message_counter) +"): "+ message + "\n"))
        self.message_counter += 1
    
    '''
    @Description:
    @Params:
    @Author: Gabriel Dombrowski (ged1225@g.rit.edu)
    '''
    def update_data_read(self):
        global RH_0
        global RH_1
        global TEMP

        with RH_LOCK:
            RH_0 = round(back_end.get_sht30(back_end.SHT30_PROBE_0, back_end.SHT30_RH), 3)
            RH_1 = round(back_end.get_sht30(back_end.SHT30_PROBE_1, back_end.SHT30_RH), 3)
            self.rh_data_var.set(str(RH_0) + back_end.RH_SUFFIX)
        
        with TEMP_LOCK:
            TEMP = round(back_end.get_sht30(back_end.SHT30_PROBE_0, back_end.SHT30_TC), 3)
            self.temp_data_var.set(str(TEMP) + back_end.TEMP_SUFFIX)

        time.sleep(1)
    
    '''
    @Description:
    @Params:
    @Author: Gabriel Dombrowski (ged1225@g.rit.edu)
    '''
    def animate(self,i):
        global RH_0
        global RH_1

        # read data from RH out and round to 2 digits
        with RH_LOCK:
            self.rh_out.append(RH_0)
            self.rh_in.append(RH_1)
        
       
        # read data from RH in and round to 2 digits        
        self.rh_out = self.rh_out[-20:]
        self.rh_in = self.rh_in[-20:]
       
        # add time and Rh data to the plot
        self.xs.append(time.time()-self.start_time)
        self.xs = self.xs[-20:]
        
        #clear the old data
        self.ax.clear()

        #plot the new data
        self.ax.plot(self.xs, self.rh_in, 'r-', label='Pre-Cyld.')
        self.ax.plot(self.xs, self.rh_out, 'b-', label='Post-Clyd.')
        self.ax.legend()
        self.ax.set_ylabel('Relative Humidity (%)')
        self.ax.set_xlabel('Seconds from Code Begin (s)')
        self.fig.subplots_adjust(bottom=0.30)

'''
@Description:
@Params:
@Author: Gabriel Dombrowski (ged1225@g.rit.edu)
'''
def main(inputs_dict, main_log):
    main_log.info('entering main function')
    main_log.debug('inputs dictionary ->', inputs_dict)
    app = Application()
    app.mainloop()


# program runnable startup code
if __name__ == '__main__':
    log = logging.getLogger(LOG_NAME)

    inputs = {}
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, 'dv', ['debug', 'verbose'])
    for opt, arg in opts:
        inputs[opt] = arg

    print('inputs: ', inputs)

    if '-d' in inputs.keys() or '--debug' in inputs.keys():
        logging.basicConfig(level=logging.DEBUG)
        log.debug('%s started in debug mode' % PROGRAM_NAME)

    elif '-v' in inputs.keys() or '--verbose' in inputs.keys():
        logging.basicConfig(level=logging.INFO)
        log.info('%s started in verbose mode' % PROGRAM_NAME)

    else:
        logging.basicConfig(level=logging.WARNING)

    main(inputs, log)