#TUFTS ECE SENIOR DESIGN
#YELLOW TEAM PROJECT
#=======================
#PARSE MODULE (PYTHON)
#
#ASSUMPTIONS FOR THIS TO WORK:
# 1. the input will be in the form of
#    a string of ascii numbers, followed
#    by a space ' '. Python's 'split' function
#    defaults to dividing strings at whitespaces
#
#=======================

#GENERAL TO DO
# 1. why won't it quit for real after Xing out?
# 2. do we want the window to keep moving
# 3. change size
# 4. make it look like biankas 

from math import log
import os
import pprint
import random
import sys
import time
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
import threading

frequency = 10              #input frequency in Hz
timer = None
read_int = 1/frequency      #interval for reading data in seconds
inputStream = ''            
iptr= 0                     #maintains the position in the input string
RAW_Q = []                  #raw data 
PLOT_ARRAY = []
back_color = "#002244"; text_color = "#FFFFFF"
graph_bg = "#000000"; graph_ax = "#FFFF00"; graph_gr = 'gray'
exit_flag = False #testing... trying to figure out exit issue
restart     = False

#======== DATA RETRIEVAL ========#
def PortStream():
    """SIMULATE bluetooth data retrieval"""
    global inputStream
    countdown = 20
    while(countdown):
        countdown -= 1
        inputStream += str(random.uniform(0, 1024))+' '

##################################
        
def readPort():
        global iptr
        global RAW_Q
        global timer

        PortStream()
        #every read_int seconds,
        #get the latest data from the input stream
        instream = inputStream[iptr:]
        #update the point in the string that we have read up to
        iptr += len(instream)
        #parse the data and
        #add the raw data to the raw queue
        for datum in (instream).split(): #split input at whitespace
                #convert all strings to floats
                converted_val = (5*float(datum))/1024
                RAW_Q.append(converted_val)   #convert to voltage reading
                sampleEval(converted_val)
        #timer = threading.Timer(read_int, readPort).start()
        
def sampleEval(datum):
    if(len(RAW_Q)%frequency == 0):
        sample_avg = sum(RAW_Q[-frequency:])/frequency
        PLOT_ARRAY.append(sample_avg)
    else:
        pass


#========= GRAPHING APP =========#
def f(element):
    element.SetForegroundColour(text_color)
    element.SetFont(wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL))
    element.SetBackgroundColour(back_color)

def colorBackground(element):
    element.SetBackgroundColour(back_color)
    
    
class BoundControlBox(wx.Panel):
    """A static box with a couple of radio buttons and a text
    box. Allows to switch between an automatic mode and a 
    manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval

        box = wx.StaticBox(self, -1, label, style=wx.TE_RICH2); f(box); 
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        f(self.radio_auto)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        f(self.radio_manual)
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        f(self.manual_text)
        
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value


class GraphFrame(wx.Frame):
    """The main frame of the application
    """

    title = 'Yellow Team 2013'
    ID_START = wx.NewId()
    
    def __init__(self,):
        """Initialize main frame. Get next data point,
        create the menu, the main panel, the status bar,
        and start the timer."""
        wx.Frame.__init__(self, None, -1, self.title)

        self.data = []       
        self.running= True
        self.paused = False
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        if self.running: readPort()
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(read_int)

    def create_menu(self):
        """Create save/exit/etc menu."""
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "&Exit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)
        f(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        #===create upper panel===#
        self.upper_panel    = wx.BoxSizer(wx.HORIZONTAL) 
        box_font =  wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

        patient_info_box = wx.StaticBox(self.panel, -1, 'Patient Information'); f(patient_info_box)
        patient_info_box.SetFont(box_font)
        patient_info = wx.StaticBoxSizer(patient_info_box, wx.VERTICAL)       
        self.patient_data       = wx.BoxSizer(wx.VERTICAL)
        self.create_data_textbox(self.patient_data,'Patient Name')
        self.create_data_textbox(self.patient_data,'Patient DOB')
        patient_info.Add(self.patient_data)
        

        eye_info_box = wx.StaticBox(self.panel, -1, 'Eye Information'); f(eye_info_box)
        eye_info_box.SetFont(box_font)
        eye_info = wx.StaticBoxSizer(eye_info_box, wx.VERTICAL)       
        self.eye_data       = wx.BoxSizer(wx.VERTICAL)
        self.create_data_textbox(self.eye_data,'IOP')
        self.create_data_textbox(self.eye_data,'AO')
        eye_info.Add(self.eye_data)
        

        self.upper_panel.Add(patient_info, border=5, flag=wx.ALL)
        self.upper_panel.AddSpacer(75)
        self.upper_panel.Add(eye_info,     border=5, flag=wx.ALL)

        #===create bottom panel===#
        self.start_button   = wx.Button(self.panel, self.ID_START, "Start")
##        self.Bind(wx.EVT_BUTTON, self.on_start_button, self.start_button)
##        self.Bind(wx.EVT_UPDATE_UI, self.on_update_start_button, self.start_button)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.start_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)


        #===layout main frame===#
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.upper_panel, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
       
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
                                    
    def create_data_textbox(self, pnl, title, val=''):
        self.pbox = wx.BoxSizer(wx.HORIZONTAL)
        self.plab = wx.StaticText(self.panel, -1, title, size=(100+len(title),-1)); f(self.plab)
        self.pdata = wx.TextCtrl(self.panel, -1, size=(200,20), value=val); f(self.pdata); 
        self.pbox.Add(self.plab, border=5,flag=wx.ALL)
        self.pbox.Add(self.pdata, border=5,flag=wx.EXPAND)
        pnl.Add(self.pbox, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
                                    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((4.0, 4.0), dpi=self.dpi, facecolor=back_color)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor(graph_bg)
        self.axes.set_title('Tonographer Output', size=14, color=text_color)
        self.axes.set_xlabel('Time (s)',size=12,color=text_color)
        self.axes.set_ylabel('Voltage (volts)',size=12, color=graph_ax)

        pylab.setp(self.axes.get_xticklabels(), fontsize=10, color=text_color)
        pylab.setp(self.axes.get_yticklabels(), fontsize=10, color=graph_ax)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        self.plot_data = self.axes.plot(
            self.data, 
            linewidth=1,
            color=(1, 1, 0),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # xmin "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        xmax = len(self.data) if len(self.data) > 120 else 120          
        xmin = xmax - 120
        ymin = 0
        ymax = 5        

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #

        self.axes.grid(True, color=graph_gr)       
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        
        self.canvas.draw()
        
    def on_start_button(self, event):
 #       if restart:
            #double check about saving first
            #clear form
            #start again
 #           self.on_exit(event)
        self.running = not self.running
    
    def on_update_start_button(self, event):
 #       global restart
        label = "Stop" if self.running else "Start"
 #       if label is "Restart": restart = True
        self.start_button.SetLabel(label)
        
    def on_pause_button(self, event):
        self.paused = not self.paused
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        """redraws plot; if paused/not running or no new data in PLOT_ARRAY,
        do not add data to the plot, but still redraw the plot
        (to respond to scale modifications, grid change, etc.)"""
        if ((not (self.paused or not self.running))
            and (len(RAW_Q)%frequency == 0)):
            readPort()
            nxt = len(self.data) #this is set for the case that
                                 #PLOT_ARRAY is updating faster than the graph
                                 #is being drawn
            self.data.append(PLOT_ARRAY[nxt])
        self.draw_plot()
    
    def on_exit(self, event):
        global exit_flag
        exit_flag = True
        self.Destroy()
        
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()


