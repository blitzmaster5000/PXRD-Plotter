from os import path
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import matplotlib
import matplotlib.ticker as ticker
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pylab import * #imports matplotlib (and ???)
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)


minor_locator = AutoMinorLocator(2)
matplotlib.rcParams.update({'figure.autolayout': True})
dataColor = 'k'  # black
fitColor = 'tab:blue'
diffColor = 'tab:orange'
matplotlib.rc('font', **{'family': "arial"})
graphCounter = 0



# python 3 app
class IoPlot(tk.Tk):   # IoPlot will inherit attributes from the tkinter module. the (tk.TK) is not technically necesary


    def __init__(self, *args, **kwargs):  # this is here to always load the following. always run when IoPlot is called
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "PXRD Plotter")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=0)
        container.grid_columnconfigure(0, weight=0)

        self.frames = {}

        for F in (StartPage, GraphTemplateFrame):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Graph:
    hkl_loaded = 0
    def __init__(self):
        pass

    def hklOpen(self):
        self.hkl_file = filedialog.askopenfilename(initialdir="/", title="Select hkl file",
                                               filetypes=(("hkl files", "*.txt"), ("all files", "*.*")))

        self.arr_hkl = np.genfromtxt(self.hkl_file, dtype='float', delimiter=',', skip_header=1)
        Graph.hkl_loaded = 1
        return Graph.hkl_loaded

    def fileOpen(self):
        self.TopasFile = filedialog.askopenfilename(initialdir="/", title="Select TOPAS file",
                                               filetypes=(("TOPAS files", "*.txt"), ("all files", "*.*")))

        self.rowSkip = 1
        self.firstGraphPlot = 0

        with open(self.TopasFile, "r") as f: #figure out how much metadata there is
            self.content = f.readlines(300) #300 should definitely cover enough characters to find all meta
            comma_count = str(self.content[1:2]).count(',')
            row_text = str(self.content[:self.rowSkip])
            strip_row_number = str(row_text[:-4])
            print(row_text)
            print(strip_row_number)

            while re.search('[a-zA-Z]', strip_row_number): #counts num of metadata lines; returns rowskip (lines to pass
                self.rowSkip += 1
                row_text = str(self.content[self.rowSkip-1:self.rowSkip])
                strip_row_number = row_text[:-4]
                # print(strip_row_number)

            arr = np.genfromtxt(self.TopasFile, dtype='str', delimiter=',', skip_header=self.rowSkip-2, max_rows=1)
            self.column_count = np.size(arr)
            counter = 4

            for columns in range(self.column_count):
                counter -= 1

            if np.where(arr == "'x"):  # this code determines which columns were exported from topas
                self.x_col = True
                self.x_col_loc = re.findall('[0-9]', str(np.where(arr == "'x")))[0]  # which column x is in
            else:
                self.x_col = False

            if np.where(arr == "Diff"):
                self.diff_col = True
                self.diff_col_loc = re.findall('[0-9]', str(np.where(arr == "Diff")))[0]  # which column diff is in
            else:
                self.diff_col = False

            if np.where(arr == "Ycalc"):
                self.ycalc_col = True
                self.ycalc_col_loc = re.findall('[0-9]', str(np.where(arr == "Ycalc")))[0]  # which column calculated is

            else:
                self.ycalc_col = False

            if arr[1:2] != "'x" and arr[1:2] != "Diff" and arr[1:2] != "Ycalc" and arr[1:2] != "Bkg":  # raw data column
                self.raw_col = True
                self.raw_col_loc = 1
            else:
                self.raw_col = False

            if np.where(arr == "Bkg"):
                self.bkg_col = True
                self.Bkg_col_loc = re.findall('[0-9]', str(np.where(arr == "Bkg")))[0] #which column diff curve is in
            else:
                self.bkg_col = False

            if np.where(arr == "xy_cumchi2"):
                self.cumchi2_col = True
                self.xy_cumchi2_col_loc = re.findall('[0-9]', str(np.where(arr == "xy_cumchi2")))[0] #column xy_cumchi2 is in
            else:
                self.cumchi2_col = False
        self.NoFileChecker = 1
        StartPage.dialogueBox(self)
        StartPage.LoadGraph(self)



class StartPage(Graph, tk.Frame):

    def __init__(self, parent, controller): # setup the layout of the page
        tk.Frame.__init__(self, parent)
        self.graphCounter = 0
        self.LegendBool = 0
        self.legLoc = "upper right"
        self.allSized = 18 #default size of all text
        self.LegendTextSizeValue = 18  # Whatever you want all the text size to be.
        gridcounter = 0  # This is what allows you to easily add new grid elements; just add gridcounter +=1
        self.GraphCount = 1  # default value of amount of graphs to be plotted
        self.NoFileChecker = 0 # looks to see at least 1 Topas file has been loaded at all; 0 = none loaded

        # this stuff takes care of setting up the data set entry drop down menu. Location etc #
        numGraphslbl = Label(self, text="Number of datasets:")
        numGraphslbl.grid(sticky=W, row=gridcounter, column=0)
        Graph2mod = Spinbox(self, state="readonly", width=2, from_=1, to=6)
        Graph2mod.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        ChangeLayout = ttk.Button(self, text="setup graph layout",
                        command=lambda: controller.show_frame(GraphTemplateFrame))
        ChangeLayout.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        upload_button = ttk.Button(self, text="Open TOPAS file",command=lambda: self.fileOpen())
        upload_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        hkl_button = ttk.Button(self, text="Open hkl file", command=lambda: self.hklOpen())
        hkl_button.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        graphPropertieslbl = Label(self, text="Graph properties:")
        graphPropertieslbl.grid(sticky=W, row=gridcounter, column=0)




        xRange = Label(self, text="x-axis range (2theta):")
        xRange.grid(sticky=W, row=gridcounter, column=0)
        self.xRangeLow = Entry(self, width=3)
        self.xRangeLow.insert(5, "5")
        self.xRangeLow.grid(sticky=W, row=gridcounter, column=1)
        xRangeTo = Label(self, text="to")
        xRangeTo.grid(sticky=W, row=gridcounter, column=2)
        self.xRangeHigh = Entry(self, width=3)
        self.xRangeHigh.insert(50, "50")
        self.xRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        gridcounter += 1

        yRange = Label(self, text="y-axis range (intensity):")
        yRange.grid(sticky=W, row=gridcounter, column=0)
        self.yRangeLow = Entry(self, width=5)
        self.yRangeLow.grid(sticky=W, row=gridcounter, column=1)
        self.yRangeLow.insert(-2000, "-2000")
        yRange = Label(self, text="to", anchor=W, justify=LEFT)
        yRange.grid(sticky=W, row=gridcounter, column=2)
        self.yRangeHigh = Entry(self, width=5)
        self.yRangeHigh.grid(sticky=W, row=gridcounter, column=3)
        self.yRangeHigh.insert(6000, "6000")
        gridcounter += 1

        xTickTogglelbl = Label(self, text="Specify x-axis ticks:")
        xTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.xTickToggle = ttk.Checkbutton(self, command=lambda: self.SetxTickState())
        self.xTickToggle.state(['!alternate'])
        self.xTickToggle.state(['!selected'])
        self.xTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        yTickTogglelbl = Label(self, text="Specify y-axis ticks:")
        yTickTogglelbl.grid(sticky=W, row=gridcounter, column=0)
        self.yTickToggle = ttk.Checkbutton(self, command=lambda: self.SetyTickState())
        self.yTickToggle.state(['!alternate'])
        self.yTickToggle.state(['!selected'])
        self.yTickToggle.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        xMjTicklbl = Label(self, text="x- major/minor tick interval:")
        xMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.xMjTick = Entry(self, width=3)
        self.xMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.xMjTick.insert(10, "10")
        self.xMjTick.config(state=DISABLED)
        xMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        xMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.xMiTick = Entry(self, width=3)
        self.xMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.xMiTick.insert(5, "5")
        self.xMiTick.config(state=DISABLED)
        gridcounter += 1

        yMjTicklbl = Label(self, text="y- major/minor tick interval:")
        yMjTicklbl.grid(sticky=W, row=gridcounter, column=0)
        self.yMjTick = Entry(self, width=5)
        self.yMjTick.grid(sticky=W, row=gridcounter, column=1)
        self.yMjTick.insert(1000, "1000")
        self.yMjTick.config(state=DISABLED)
        yMjTicklbl2 = Label(self, text="/", anchor=W, justify=LEFT)
        yMjTicklbl2.grid(sticky=W, row=gridcounter, column=2)
        self.yMiTick = Entry(self, width=5)
        self.yMiTick.grid(sticky=W, row=gridcounter, column=3)
        self.yMiTick.insert(500, "500")
        self.yMiTick.config(state=DISABLED)
        gridcounter += 1

        ticksButtonlbl = Label(self, text="Show hkl ticks:")
        ticksButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButton = ttk.Checkbutton(self, command=lambda: StartPage.hklToggle(self))
        self.ticksButton.state(['!alternate'])
        self.ticksButton.state(['selected'])
        self.ticksButton.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        ticksoffsetlbl = Label(self, text="hkl ticks offset:")
        ticksoffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.ticksButtonOffset = ttk.Entry(self, width=5)
        self.ticksButtonOffset.insert(-40, "-40")
        self.ticksButtonOffset.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        DiffCurveButtonlbl = Label(self, text="Show difference curve:")
        DiffCurveButtonlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveButton = ttk.Checkbutton(self, command=lambda: StartPage.SetDiffCurvState(self))
        self.DiffCurveButton.state(['!alternate'])
        self.DiffCurveButton.state(['selected'])
        self.DiffCurveButton.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

        DiffCurveOffsetlbl = Label(self, text="Difference Curve offset:")
        DiffCurveOffsetlbl.grid(sticky=W, row=gridcounter, column=0)
        self.DiffCurveOffset = ttk.Entry(self, width=5)
        self.DiffCurveOffset.insert(-500, "-500")
        self.DiffCurveOffset.grid(sticky=W, row=gridcounter, column=1)
        gridcounter += 1

    # this stuff takes care of setting up the legend. Location etc #
        LegendLocater = ttk.Menubutton(self, text="Legend Position")
        LegendLocater.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        LegendLocater.menu = Menu(LegendLocater, tearoff=0)
        LegendLocater["menu"] = LegendLocater.menu
        self.LegendTopRight = tk.IntVar()
        self.LegendTopLeft = tk.IntVar()
        self.LegendBotLeft = tk.IntVar()
        self.LegendBotRight = tk.IntVar()
        self.LegendOff = tk.IntVar()

        LegendLocater.menu.add_checkbutton(label="Top right", variable=self.LegendTopRight, command=lambda: StartPage.LegendTR(self))
        LegendLocater.menu.add_checkbutton(label="Top left", variable=self.LegendTopLeft, command=lambda: StartPage.LegendTL(self))
        LegendLocater.menu.add_checkbutton(label="Bottom right",variable=self.LegendBotRight, command=lambda: StartPage.LegendBR(self))
        LegendLocater.menu.add_checkbutton(label="Bottom left", variable=self.LegendBotLeft, command=lambda: StartPage.LegendBL(self))
        LegendLocater.menu.add_checkbutton(label="Turn legend off", variable=self.LegendOff, command=lambda: StartPage.LegendLO(self))
        gridcounter += 1

        LegendTextSizelbl = Label(self, text="Legend text size:")
        LegendTextSizelbl.grid(sticky=W, row=gridcounter, column=0)
        self.LegendTextSize = Entry(self, width=3)
        self.LegendTextSize.grid(sticky=W, row=gridcounter, column=1)
        self.LegendTextSize.insert(18, "18")
        gridcounter += 1



        UpdateGraph = ttk.Button(self, text="Update graph", command=lambda: StartPage.LoadGraph(self))
        UpdateGraph.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        SaveFig = ttk.Button(self, text="Save figure", command=lambda: StartPage.saveFigFunc(self))
        SaveFig.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        dialoguelbl = Label(self, text="Datasets currently open:")
        dialoguelbl.grid(sticky=NW, row=gridcounter, column=0, pady=4, padx=4)
        gridcounter += 1

        self.gridcounter2 = gridcounter
        dialoguelbl = Label(self, text=StartPage.dialogueBox(self))
        dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
        gridcounter += 1

    def dialogueBox(self):
        if self.NoFileChecker == 0:
            self.datasetString = str("No datasets loaded.")
            return self.datasetString
        else:
            self.datasetString = str(path.basename(self.TopasFile))
            dialoguelbl = Label(self, text=self.datasetString)
            dialoguelbl.grid(sticky=NW, row=self.gridcounter2, column=0, pady=4, padx=4, columnspan=2)
            return self.datasetString

    def CheckGraphCounter(self):
        print(self.GraphCount)
        self.GraphCount = self.GraphCount



    def DatasetFunc1(self):
        self.NumberDatasets2.set(0)
        self.NumberDatasets3.set(0)
        self.NumberDatasets4.set(0)
        self.NumberDatasets5.set(0)
        self.GraphCount = 1

    def DatasetFunc2(self):
        self.NumberDatasets1.set(0)
        self.NumberDatasets3.set(0)
        self.NumberDatasets4.set(0)
        self.NumberDatasets5.set(0)
        self.GraphCount = 2

    def DatasetFunc3(self):
        self.NumberDatasets1.set(0)
        self.NumberDatasets2.set(0)
        self.NumberDatasets4.set(0)
        self.NumberDatasets5.set(0)
        self.GraphCount = 3


    def DatasetFunc4(self):
        self.NumberDatasets1.set(0)
        self.NumberDatasets2.set(0)
        self.NumberDatasets3.set(0)
        self.NumberDatasets5.set(0)
        self.GraphCount = 4

    def DatasetFunc5(self):
        self.NumberDatasets1.set(0)
        self.NumberDatasets2.set(0)
        self.NumberDatasets3.set(0)
        self.NumberDatasets4.set(0)
        self.GraphCount = 5

    def LegendTR(self):
        self.LegendTopLeft.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper right'  # location of the legend
        self.LegendBool = 0

    def LegendTL(self):
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'upper left'  # location of the legend
        self.LegendBool = 0

    def LegendBR(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower right'  # location of the legend
        self.LegendBool = 0

    def LegendBL(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotRight.set(0)
        self.LegendOff.set(0)
        self.legLoc = 'lower left'  # location of the legend
        self.LegendBool = 0

    def LegendLO(self):
        self.LegendTopLeft.set(0)
        self.LegendTopRight.set(0)
        self.LegendBotLeft.set(0)
        self.LegendBotRight.set(0)
        self.LegendBool = 1

    def LoadGraph(self):
        #setup the graphical elements; fonts, colors, etc
        matplotlib.rc('font', size=self.allSized, **{'family': "arial"})  # controls default text sizes
        matplotlib.rc('axes', titlesize=self.allSized)  # fontsize of the axes title
        matplotlib.rc('axes', labelsize=self.allSized)  # fontsize of the x and y labels
        matplotlib.rc('xtick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('ytick', labelsize=self.allSized)  # fontsize of the tick labels
        matplotlib.rc('legend', fontsize=self.allSized)  # legend fontsize
        matplotlib.rc('figure', titlesize=self.allSized)  # fontsize of the figure title
        self.diffColor = "blue"
        self.fitColor = "red"
        self.dataColor = "black"
        self.arr_graph = np.loadtxt(self.TopasFile, delimiter=',', dtype='float', skiprows=self.rowSkip - 1,
                                    unpack=True)
        self.f = Figure(figsize=(6, 6), dpi=100)
        self.ax1 = self.f.add_subplot(111)
        self.ax1.set_ylabel('Intensity (Counts)')
        self.ax1.set_xlabel('2$\Theta$ ($^\circ$, CuK$_{\\alpha}$)')
        if self.x_col:
            if self.raw_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[1],
                              color=self.dataColor, marker='o', lineStyle='None', label='Data', markersize=4)
            else:
                print("there is no raw data")
            if self.ycalc_col:
                self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[int(self.ycalc_col_loc)],
                              color=self.fitColor, lineStyle='-', label='Calculated')
            else:
                print("there is no ycalc data")
            if self.diff_col:

                if Graph.hkl_loaded == 1 & self.ticksButton.instate(['selected']):
                    self.maxDiff = np.max(self.arr_graph[int(self.diff_col_loc)]) + 60
                else:
                    self.maxDiff = np.max(self.arr_graph[int(self.diff_col_loc)]) + 10
                a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], self.arr_graph[int(self.diff_col_loc)] - self.maxDiff,
                              color=self.diffColor, lineStyle='-', label='Difference')

            else:
                print("there is no diff data")
        else:
            print("there is no x-axis data")

        if Graph.hkl_loaded == 1 & self.ticksButton.instate(['selected']):
            self.ax1.plot(self.arr_hkl, (self.arr_hkl - self.arr_hkl) + int(self.ticksButtonOffset.get()),
                          color=self.fitColor, marker='|', label='hkl phase', linestyle='None', markerSize=20)
            print(self.arr_hkl[1])
        else:
            pass
            print("misses the iff to here")
            print(Graph.hkl_loaded)

        if self.firstGraphPlot == 0: #run this code to setup the initial graph
            self.ax1.xaxis.set_major_locator(ticker.AutoLocator())  # when first plotted, will use autolocator.
            self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())  # when first plotted, will use autolocator.
        else: #run this code to update graph
            #self.f = Figure(figsize=(6, 6), dpi=100)
            # self.f.autolayout: True
            #self.ax1 = self.f.add_subplot(111)
            self.xRangeLowValue = int(self.xRangeLow.get())
            self.xRangeHighValue = int(self.xRangeHigh.get())
            self.yRangeLowValue = int(self.yRangeLow.get())
            self.yRangeHighValue = int(self.yRangeHigh.get())
            self.DiffCurveOffsetValue = int(self.DiffCurveOffset.get())

            if self.diff_col:
                for handle in a: #removes the current diff curve as this function moves it based on the following
                    handle.remove()

                if self.DiffCurveButton.instate(['selected']) == TRUE: # checks if show diff is true
                    a = self.ax1.plot(self.arr_graph[int(self.x_col_loc)], # plots curve based on offset value
                                           (self.arr_graph[int(self.diff_col_loc)]+self.DiffCurveOffsetValue),
                                           color=self.diffColor, lineStyle='-', label='Difference')
                    print(self.DiffCurveOffsetValue)
                else:
                    print("curve has been deleted") # code w/ handle above has already deleted line, so just pass
            self.ax1.set_xlim(self.xRangeLowValue, self.xRangeHighValue)
            self.ax1.set_ylim(self.yRangeLowValue, self.yRangeHighValue)
            if self.xTickToggle.instate(['selected']) == TRUE:
                self.ax1.xaxis.set_major_locator(ticker.MultipleLocator(float(self.xMjTick.get())))
                self.ax1.xaxis.set_minor_locator(ticker.MultipleLocator(float(self.xMiTick.get())))
            else:
                self.ax1.xaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

            if self.yTickToggle.instate(['selected']) == TRUE:
                self.ax1.yaxis.set_major_locator(ticker.MultipleLocator(float(self.yMjTick.get())))
                self.ax1.yaxis.set_minor_locator(ticker.MultipleLocator(float(self.yMiTick.get())))
            else:
                self.ax1.yaxis.set_major_locator(ticker.AutoLocator())
                self.ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())

        if self.LegendBool == 1:
            self.ax1.legend().remove()
        else:
            self.ax1.legend(loc=self.legLoc, prop={'size': self.LegendTextSize.get()}, frameon=False, bbox_transform=plt.gcf().transFigure)

        canvas = FigureCanvasTkAgg(self.f, self)
        canvas.draw()
        canvas._tkcanvas.grid(row=0, column=3, columnspan=1000, rowspan=1000, padx=50, pady=5)
        self.firstGraphPlot = 1  # this makes sure you will only update the plot from now on using the following
        print("can you plot")

    def hklToggle(self):
        if self.ticksButton.instate(['selected']):
            self.ticksButtonOffset.config(state=NORMAL)
        elif self.ticksButton.instate(['!selected']):
            self.ticksButtonOffset.config(state=DISABLED)


    def SetxTickState(self):
        if self.xTickToggle.instate(['selected']):
            self.xMjTick.config(state=NORMAL)
            self.xMiTick.config(state=NORMAL)

        elif self.xTickToggle.instate(['!selected']):
            self.xMjTick.config(state=DISABLED)
            self.xMiTick.config(state=DISABLED)

    def SetyTickState(self):
        if self.yTickToggle.instate(['selected']):
            self.yMjTick.config(state=NORMAL)
            self.yMiTick.config(state=NORMAL)

        elif self.yTickToggle.instate(['!selected']):
            self.yMjTick.config(state=DISABLED)
            self.yMiTick.config(state=DISABLED)

    def SetDiffCurvState(self):
        if self.DiffCurveButton.instate(['selected']):
            self.DiffCurveOffset.config(state=NORMAL)
        elif self.DiffCurveButton.instate(['!selected']):
            self.DiffCurveOffset.config(state=DISABLED)

    def saveFigFunc(self):
        self.SaveFig = filedialog.asksaveasfilename(initialdir="/", title="save figure name:",
                                                filetypes=(("png", "*.png"), ("all files", "*.*")))
        self.f.savefig(self.SaveFig, dpi=300, facecolor='white', bbox_inches='tight')

    def initiateGraph(self):

        if self.graphCounter == 0:
            # graph_1.LoadGraph()
            graph_1 = Graph()
            graph_1.fileOpen()
            self.graphCounter = 1
        elif graphCounter == 1:
            graph_2 = Graph()
            graph_2()
            self.graphCounter = 2
        elif graphCounter == 2:
            graph_3 = Graph()
            graph_3()
            self.graphCounter = 3
        elif graphCounter == 3:
            graph_4 = Graph()
            graph_4()
            self.graphCounter = 4


class GraphTemplateFrame(tk.Frame):
    def __init__(self, parent, controller): # setup the layout of the page
        tk.Frame.__init__(self, parent)
        ChangeLayout = ttk.Button(self, text="setup graph layout")
        ChangeLayout.grid(sticky=NW, row=1, column=0, pady=4, padx=4)












app = IoPlot()
app.geometry("1000x600")
app.resizable(width=False, height=False)
app.mainloop()
