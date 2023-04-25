#!/usr/bin/env python3

import enum
import getopt
import logging
import sys
import tkinter as tk
import back_end

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


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.geometry(str(screen_width)+"x"+str(screen_height))
        self.title(PROGRAM_NAME)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # declare menu bar
        menu_bar = tk.Menu(self)
        menu_bar.add_command(label="Settings", command=settings_window)
        self.config(menu=menu_bar)

        frame = Menu(container, self)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.tkraise()


class Menu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # declare widgets
        greeting = tk.Label(self, text='Ossilla Enviornnmental Control', font='LARGEFONT')
        label_frame = tk.LabelFrame(self, text="Readings", )
        rh_label = tk.Label(label_frame, text="ToDo")
        
        # dehumidifcation button
        dehumidify_button_tvar = tk.StringVar(value=back_end.DHUMID_IDLE)
        dehumidify_button = tk.Button(self, textvariable=dehumidify_button_tvar, command= lambda: back_end.dehumidifcation_button(tvar=dehumidify_button_tvar, button=dehumidify_button))

        # record data button
        record_button_tvar = tk.StringVar(value=back_end.RECORD_IDLE)
        record_button = tk.Button(self, textvariable=record_button_tvar, command= lambda: back_end.record_button(tvar=record_button_tvar, button=record_button))

        # Export data button
        export_button_tvar = tk.StringVar(value=back_end.EXPORT_IDLE)
        export_button = tk.Button(self, textvariable=export_button_tvar, command= lambda: back_end.export_button(tvar=export_button_tvar, button=export_button))

        #place widgets
        rh_label.pack(fill="both", expand="yes")
        greeting.grid(row=0, column=0, padx=PADX, pady=PADY)
        label_frame.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="ew")
        dehumidify_button.grid(row=2, column=0, padx=PADX, pady=PADY, sticky='ew')
        record_button.grid(row=3, column=0, padx=PADX, pady=PADY, sticky='ew')
        export_button.grid(row=4, column=0, padx=PADX, pady=PADY, sticky="ew")

def settings_window():
    window = tk.Toplevel()
    window.geometry("500x300")
    newlabel = tk.Label(window, text="Settings")
    newlabel.pack()

# main function
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