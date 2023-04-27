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

# Program name global strings
PROGRAM_NAME = 'EnviornmentalControl'
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
MESSAGE_BOX_WIDTH=85

BUTTON_FONT_SIZE = 24
TITLE_FONT_SIZE = 36
DATA_FONT_SIZE = 18


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

        # >>>>>>>>>>>>> Declarations <<<<<<<<<<<<<<
        # title
        self.title_label = tk.Label(self, text='Ossilla Enviornnmental Control System', font=('Times', TITLE_FONT_SIZE))
        
        # labelframe
        self.label_frame = tk.LabelFrame(self, text="Readings", font=('Times', DATA_FONT_SIZE))

        # declare graph stuff
        # used for animation
        self.v = 1.0
        self.A = 1.0
        self.xs = []
        self.rh_out = []
        self.rh_in = []
        graph_frame = tk.LabelFrame(self, text="Relative Humidity", font=('Times', DATA_FONT_SIZE))
        self.fig = plt.Figure(figsize=(6, 2))
        self.x = 20*np.arange(0, 2*np.pi, 0.01)        # x-array
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(self.x, np.sin(self.x))        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)

        # rh in Lableframe
        self.rh_data_var = tk.StringVar(value="--%")
        self.rh_label = tk.Label(self.label_frame, text="Relative Humidity", font=('Times', DATA_FONT_SIZE))
        self.rh_data = tk.Label(self.label_frame, textvariable=self.rh_data_var, font=('Times', BUTTON_FONT_SIZE))

        # temp in Labelframe
        self.temp_label = tk.Label(self.label_frame, text="Temperature", font=('Times', DATA_FONT_SIZE))
        self.temp_data_var = tk.StringVar(value="--°C")
        self.temp_data = tk.Label(self.label_frame, textvariable=self.temp_data_var, font=('Times', BUTTON_FONT_SIZE))
            
        # start button in button frame
        self.dehumidify_button_tvar = tk.StringVar(value="START/STOP")
        self.dehumidify_button = tk.Button(self.button_frame, height=BUTTON_HEIGHT, font=('Times', BUTTON_FONT_SIZE),
                                    textvariable=self.dehumidify_button_tvar,  
                                    command= lambda: back_end.dehumidifcation_button(tvar=self.dehumidify_button_tvar, 
                                                                    button=self.dehumidify_button))

        # record button in button frame
        self.record_button_tvar = tk.StringVar(value="RECORD")
        self.record_button = tk.Button(self.button_frame, height=BUTTON_HEIGHT, font=('Times', BUTTON_FONT_SIZE),
                                textvariable=self.record_button_tvar,  
                                command= lambda: back_end.record_button(tvar=self.record_button_tvar, 
                                                                    button=self.record_button))

        # Export button in button frame
        self.export_button_tvar = tk.StringVar(value="EXPORT")
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
        ''' dehumidify_button.grid(row=0, column=0, padx=PADX, pady=PADY, sticky='nsew')
        record_button.grid(row=1, column=0, padx=PADX, pady=PADY, sticky='nsew')
        export_button.grid(row=2, column=0, padx=PADX, pady=PADY, sticky='nsew')'''

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
        pass
    
    '''
    @Description:
    @Params:
    @Author: Gabriel Dombrowski (ged1225@g.rit.edu)
    '''
    def animate(self,i):
        # read data from RH out and round to 2 digits
        rhData = round(back_end.get_sht30(back_end.SHT30_PROBE_0, back_end.SHT30_RH), 2)
        self.rh_out.append(rhData)
        self.rh_out = self.rh_out[-20:]
       
        # read data from RH in and round to 2 digits
        rhData = round(back_end.get_sht30(back_end.SHT30_PROBE_1, back_end.SHT30_RH), 2)
        self.rh_in.append(rhData)
        self.rh_in = self.rh_in[-20:]
       
        # add time and Rh data to the plot
        self.xs.append(dt.datetime.now().strftine('%S'))
        self.xs = self.xs[-20:]
        
        self.ax.clear()
        self.ax.plot(self.ys, self.rh_in, 'r-', label='in')
        self.ax.plot(self.ys, self.rh_out, 'b-', label='out')

        self.plt.xticks(ha='right')
        self.plt.subplots_adjust(bottom=0.30)
        #self.plt.title('SHT30 Relative Humidity over Time')
        #self.plt.ylabel('Relative Humidity (%)')
        #self.plt.xlabel('Seconds from Code Begin (s)')

        #self.line.set_ydata(self.A*np.sin(self.x+self.v*i))  # update the data
        #return self.line

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