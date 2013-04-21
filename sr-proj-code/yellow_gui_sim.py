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
# 2. Whywon't it continue after saving
# 3. be able to print
# 4. why are colors of axes off for inv
# 5. save to excel form
# 6. have "open" functionality
# 7. have "new" functionality


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
import datetime

import threading

frequency = 10              #input frequency in Hz
timer = None
read_int = (float(1)/frequency)*100 #interval for reading data in seconds
inputStream = ''            
iptr= 0                     #maintains the position in the input string
RAW_Q = []                  #raw data 
PLOT_ARRAY = []
colors = {'bg': "#002244",
          'text' : "#FFFFFF",
          'graph_bg' : "#000000",
          'graph_dat' : "#FFFF00",
          'graph_gr' : "#C0C0C0"}

exit_flag = False #testing... trying to figure out exit issue
restart     = False

#========= DATA STORAGE =========#

status = {'exit': False, 'restart': False, 'empty': [], 'saved': False}


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
    """Every read_int seconds, get the latest data
from the input stream, update the point (iptr) in
the string that we have read up to, parse the new
data and add the raw data to the 'raw queue'"""
    global iptr
    global RAW_Q
    global timer

    PortStream()
    instream = inputStream[iptr:]
    iptr += len(instream)
    for datum in (instream).split(): #split input at whitespace
            converted_to_volts = (5*float(datum))/1024
            RAW_Q.append(converted_to_volts)
            sampleEval(converted_to_volts)
    #timer = threading.Timer(read_int, readPort).start()
        
def sampleEval(datum):
    if(len(RAW_Q)%frequency == 0):
        sample_avg = sum(RAW_Q[-frequency:])/frequency
        PLOT_ARRAY.append(sample_avg)
    else:
        pass

#========= GRAPHING APP =========#
def f(element):
    element.SetForegroundColour(colors['text'])
    element.SetFont(wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL))
    element.SetBackgroundColour(colors['bg'])
    
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
        self.file_data = {
            'Patient': {'Patient Name': '', 'Patient DOB': '', 'Age': ''},
            'Eye':{'Left IOP': '', 'Left AO': '', 'Right IOP': '', 'Right AO': ''},
            'Exam':{'Total Running Time': ''}
        }
        self.running= True
        self.paused = False
        
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

        if self.running: readPort()
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(read_int)

    def invert_colors(self):
        for color in colors:
            inv = hex(int('FFFFFF',16)-int(colors[color][1:],16))
            colors[color] = '#'+inv[2:].zfill(6)

    def create_menu(self):
        """Create save/exit/etc menu."""
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_rec = menu_file.Append(-1, "&Save exam record\tCtrl-S", "Save record to file")
        self.Bind(wx.EVT_MENU, self.on_save_file, m_rec)
        m_expt = menu_file.Append(-1, "&Save plot image\tCtrl-P", "Save plot to file")
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
        patient_data       = wx.BoxSizer(wx.VERTICAL)
        self.create_data_textbox(patient_data,'Patient Name')
        self.create_data_textbox(patient_data,'Patient DOB')
        patient_info.Add(patient_data, 1, flag=wx.ALIGN_CENTER)
        

        eye_info_box = wx.StaticBox(self.panel, -1, 'Eye Information'); f(eye_info_box)
        eye_info_box.SetFont(box_font)
        eye_info = wx.StaticBoxSizer(eye_info_box, wx.HORIZONTAL)       
        for side in ['Left','Right']:
            eye_data       = wx.BoxSizer(wx.VERTICAL)
            self.create_data_textbox(eye_data,side+' IOP')
            self.create_data_textbox(eye_data,side+' AO')
            eye_info.Add(eye_data, 1, flag=wx.ALIGN_CENTER)
            eye_info.AddSpacer(20)
        

        self.upper_panel.Add(patient_info, 1, border=5, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        self.upper_panel.AddSpacer(75)
        self.upper_panel.Add(eye_info,    1, border=5, flag=wx.ALIGN_RIGHT | wx.ALIGN_TOP)

        #===create bottom panel===#
        self.start_button   = wx.Button(self.panel, self.ID_START, "Start")
##        self.Bind(wx.EVT_BUTTON, self.on_start_button, self.start_button)
##        self.Bind(wx.EVT_UPDATE_UI, self.on_update_start_button, self.start_button)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.lower_panel = wx.BoxSizer(wx.HORIZONTAL)
        self.lower_panel.Add(self.start_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.lower_panel.AddSpacer(10)
        self.lower_panel.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.lower_panel.AddSpacer(10)


        #===layout main frame===#
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.upper_panel, 0, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.lower_panel, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_TOP)
       
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
                                    
    def create_data_textbox(self, pnl, title, val='', length=80+len(title)):
        self.pbox = wx.BoxSizer(wx.HORIZONTAL)
        self.plab = wx.StaticText(self.panel, -1, title, size=(length,-1)); f(self.plab)
        self.pdata = wx.TextCtrl(self.panel, -1, size=(length,20), value=val); f(self.pdata);

        for subset in self.file_data:
            if title in self.file_data[subset]:
                self.file_data[subset][title] = self.pdata
                
        
        self.pbox.Add(self.plab, border=5, flag=wx.ALL)
        self.pbox.Add(self.pdata, border=5,flag=wx.EXPAND)
        pnl.Add(self.pbox, 1, flag=wx.CENTER | wx.TOP)
                                    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((4.0, 4.0), dpi=self.dpi, facecolor=colors['bg'])

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor(colors['graph_bg'])
        self.axes.set_title('Tonographer Output', size=14, color=colors['text'])
        self.axes.set_xlabel('Time (s)',size=12,color=colors['text'])
        self.axes.set_ylabel('Voltage (volts)',size=12, color=colors['graph_dat'])

        pylab.setp(self.axes.get_xticklabels(), fontsize=10, color=colors['text'])
        pylab.setp(self.axes.get_yticklabels(), fontsize=10, color=colors['graph_dat'])

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        self.plot_data = self.axes.plot(
            self.data, 
            linewidth=1,
            color=colors['graph_dat'],
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
        
        self.axes.grid(True, color=colors['graph_gr'])       
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
        p = self.paused
        self.paused = True
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
            self.canvas.print_figure(path, dpi=self.dpi, facecolor=colors['bg'])

            self.invert_colors(); newpath = path[:-4]+'inv.png'
            self.canvas.print_figure(newpath, dpi=self.dpi, facecolor=colors['bg'])
            self.invert_colors()

            self.flash_status_message("Saved to %s" % path)
            
        self.paused = p
    
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
        global status

        p = self.paused
        self.paused = True

        status['exit'] = True
        
        toquit = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if toquit.ShowModal() == wx.ID_YES:
            if not status['saved']:
                tosave = wx.MessageDialog(None, 'Do you want to save before?', 'Question',
                                          wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                if tosave.ShowModal() == wx.ID_YES:
                    self.on_save_file(event)
            
                self.redraw_timer.Stop()
                for item in wx.GetTopLevelWindows():
                    if not isinstance(item, GraphFrame):
                        if isinstance(item, wx.Dialog):
                            item.Destroy()
                        item.Close()
                self.Destroy()
        else:
            self.paused = False
            
    def on_save_file(self, event):
        global status

        p = self.paused
        self.paused = True

        #check if all the fields are filled
        status['empty'] = []
        for subset in self.file_data:
            for field in self.file_data[subset]:
                try:
                    if self.file_data[subset][field].IsEmpty():
                        status['empty'].append(field)
                        self.file_data[subset][field].SetBackgroundColour('#FF2200')
                    else:
                        self.file_data[subset][field] = self.file_data[subset][field].GetValue()
                except AttributeError:
                    pass
        if status['empty']:
            emptyMsg = "The following required fields have not been filled:\n"
            for f in sorted(status['empty']): emptyMsg += '\t'+f+'\n'
            emptyMsg += "You must fill in these fields before quitting."
            wx.MessageBox(emptyMsg, 'ERROR! Required information missing', wx.OK | wx.ICON_EXCLAMATION)
            return
        
        name= self.file_data['Patient']['Patient Name']
        now = str(datetime.datetime.now())[:16]; now = now[:13]+'.'+now[14:]
        file_choices= "CSV (*.csv)|*.csv"
        
        dlg = wx.FileDialog(
            self, 
            message="Save file as...",
            defaultDir=os.getcwd(),
            defaultFile=name+' '+now,
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            newfile = open(path, 'w')
            line = 'Patient Information'
            line += '\n'.join([(k+','+self.file_data['Patient'][k]) for k in self.file_data['Patient']])
            newfile.write(line+'\n')
            line = 'Exam Information'
            line += '\n'.join([(k+','+self.file_data['Exam'][k]) for k in sorted(self.file_data['Exam'].keys())])
            newfile.write(line+'\n')
            line += '\n'.join([(k+','+self.file_data['Eye'][k]) for k in sorted(self.file_data['Eye'].keys())])
            newfile.write(line)

            newfile.close()
            self.flash_status_message("Saved to %s" % path)
            
            
        self.paused = p
        return
        
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
#    FileMessageBox(None)
    app.MainLoop()


