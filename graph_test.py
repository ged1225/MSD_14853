#---------Imports

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#---------End of imports



from tkinter import Frame,Label,Entry,Button


class Window(Frame):

    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Use Of FuncAnimation in tkinter based GUI")
        self.pack(fill='both', expand=1)     

        #Create the controls, note use of grid

        # used for animation
        self.v = 1.0
        self.A = 1.0

        # declare graph stuff
        tk.Label(self,text="Relative Humidity").grid(column=0, row=3)
        self.fig = plt.Figure()
        self.x = 20*np.arange(0, 2*np.pi, 0.01)        # x-array
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(self.x, np.sin(self.x))        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        # pack graph
        self.canvas.get_tk_widget().grid(column=0,row=4)

        # set graph to animate
        self.ani = animation.FuncAnimation(self.fig, self.animate, np.arange(1, 200), interval=25, blit=False)


    def animate(self,i):
        self.line.set_ydata(self.A*np.sin(self.x+self.v*i))  # update the data
        return self.line


root = tk.Tk()
root.geometry("700x400")
app = Window(root)
tk.mainloop()