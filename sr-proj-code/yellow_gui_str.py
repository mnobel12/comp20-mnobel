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
import wxversion; wxversion.select('2.8')
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
import serial

com_port_ser = "COM5"
com_port_wir = "COM15"

frequency = 10              #input frequency in Hz
timer = None
read_int = 1/frequency      #period for reading data
inputStream = ''            
iptr= 0                     #maintains the position in the input string
RAW_Q = []                  #array of every measurement (converted to volts) 
PLOT_ARRAY = []             #array of every sample mean/data to plot

exit_flag = False #testing... trying to figure out exit issue


#======== DATA RETRIEVAL ========#

def PortStream(bluetooth=True):
    """Retrieve data from bluetooth and add to inputStream string"""
    global inputStream

    if bluetooth:
            com_port = com_port_wir   
    else:
            com_port = com_port_ser

    try:
            serial_port = serial.Serial(com_port, timeout=3, writeTimeout=3, baudrate=9600)
    except Exception as ex:
            print "Failed to create a serial port on port:", com_port
            raise ex

    try:
        data_str = serial_port.readline()
    except Exception as ex:
        raise ex
         
    inputStream += data_str
    try:
        serial_port.close()
    except Exception as ex:
        print "Failed to close the port:", com_port
        raise ex


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
                RAW_Q.append((5*float(datum))/1024)   #convert to voltage reading
        timer = threading.Timer(read_int, readPort).start()


class DataGet(object):
    """ A class that reads in a string of multiple outputs per reading.
    """
    def __init__(self):
        PortStream()
        readPort()
        
    def next(self):
        #for plotting every measurement
        return RAW_Q[len(PLOT_ARRAY)]
        #for plotting every f=frequency measurements (averaged), aka once a second
        

def analysis(datum):
#was here before culture show (adjusting analysis funciton to do the
    #averaging stuff for plot_array, and then you may have to change the
    #plot drawing function so that it doesn't redraw until every 5
#if(len(RAW_Q)%5 == 0):
    PLOT_ARRAY.append(transformed_data)


#========= GRAPHING APP =========#
    
class BoundControlBox(wx.Panel):
    """A static box with a couple of radio buttons and a text
    box. Allows to switch between an automatic mode and a 
    manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
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


        self.dataget = DataGet()
        self.data = [self.dataget.next()]       
        analysis(self.data[-1])
        self.paused = False
        self.running= False
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.redraw_timer.Start(100)

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

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        #===create upper panel===#
        self.upper_panel    = wx.BoxSizer(wx.HORIZONTAL) 

        patient_info_box = wx.StaticBox(self.panel, -1, 'Patient Information')
        patient_info = wx.StaticBoxSizer(patient_info_box, wx.VERTICAL)       
        self.patient_data       = wx.BoxSizer(wx.VERTICAL)
        self.create_data_textbox(self.patient_data,'Patient Name')
        self.create_data_textbox(self.patient_data,'Patient DOB')
        patient_info.Add(self.patient_data)

        eye_info_box = wx.StaticBox(self.panel, -1, 'Eye Information')
        eye_info = wx.StaticBoxSizer(eye_info_box, wx.VERTICAL)       
        self.eye_data       = wx.BoxSizer(wx.VERTICAL)
        self.create_data_textbox(self.eye_data,'IOP')
        self.create_data_textbox(self.eye_data,'AO')
        eye_info.Add(self.eye_data)

        self.upper_panel.Add(patient_info, border=5, flag=wx.ALL)
        self.upper_panel.AddSpacer(75)
        self.upper_panel.Add(eye_info,     border=5, flag=wx.ALL)

        #===create bottom panel===#
        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 5)

        self.start_button   = wx.Button(self.panel, self.ID_START, "Start")
        self.Bind(wx.EVT_BUTTON, self.on_start_button, self.start_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_start_button, self.start_button)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)

        #===layout main frame===#
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.upper_panel, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
                                    
    def create_data_textbox(self, pnl, title, val=''):
        self.pbox = wx.BoxSizer(wx.HORIZONTAL)
        self.plab = wx.StaticText(self.panel, -1, title, size=(50+len(title),-1))
        self.pdata = wx.TextCtrl(self.panel, -1, size=(100,-1), value=val)
        self.pbox.Add(self.plab, border=5,flag=wx.ALL)
        self.pbox.Add(self.pdata, border=5,flag=wx.ALL)
        pnl.Add(self.pbox, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
                                    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((4.0, 4.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Tonographer Output', size=14)
        self.axes.set_xlabel('Time',size=12)
        self.axes.set_ylabel('Voltage (volts)',size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

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
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control.is_auto():
            xmax = len(self.data) if len(self.data) > 50 else 50
        else:
            xmax = int(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():            
            xmin = xmax - 50
        else:
            xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        if self.ymin_control.is_auto():
            ymin = round(min(self.data), 0) - 1
        else:
            ymin = int(self.ymin_control.manual_value())
        
        if self.ymax_control.is_auto():
            ymax = round(max(self.data), 0) + 1
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        
        self.canvas.draw()
    def on_start_button(self, event):
        self.running = not self.running
    
    def on_update_start_button(self, event):
        label = "Stop" if self.running else "Start"
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
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if len(PLOT_ARRAY) == len(RAW_Q):
            pass
        elif not self.paused:
            self.data.append(self.dataget.next())
            analysis(self.data[-1])
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


