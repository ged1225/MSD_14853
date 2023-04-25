#!/usr/bin/env python3
import tkinter as tk
import time

RECORD_IDLE = "Begin Recording"
RECORD_ACTIVE = "End Recording"

DHUMID_IDLE = "Begin Dehumidification Process"
DHUMID_ACTIVE = "End Dehumidification Process"

EXPORT_IDLE = "Export to CSV"
EXPORT_ACTIVE = "Exporting..."

def export_button(tvar: tk.StringVar, button: tk.Button):
    if tvar.get() == EXPORT_IDLE:
        # set the button label to active
        tvar.set(EXPORT_ACTIVE)
        # deactivate button
        button.configure(state=tk.DISABLED)

        # print message --todo make LOG
        print("Exporting...")

        # wait for 1 second -- todo add functionnality here
        time.sleep(5)

        # reset the button label
        tvar.set(EXPORT_IDLE)

        # reactivate the button
        button.configure(state=tk.NORMAL)

        # print message --todo make LOG
        print("Export complete")
    else:
        # print message -- todo make LOG
        print("Button error - pressed while active status")

def dehumidifcation_button(tvar: tk.StringVar, button: tk.Button):
    if tvar.get() == DHUMID_ACTIVE:
        tvar.set(DHUMID_IDLE)
        print("Dehumidification complete...")
    else:
        tvar.set(DHUMID_ACTIVE)
        print("Dehumidifying...")

def record_button(tvar: tk.StringVar, button: tk.Button):
    if tvar.get() == RECORD_ACTIVE:
        tvar.set(RECORD_IDLE)
        print("Record complete")
    else:
        tvar.set(RECORD_ACTIVE)
        print("Recording...")