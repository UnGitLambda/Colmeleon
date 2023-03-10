#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import ctypes

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
import os
import pathlib
import tkinter as tk
from tkinter import filedialog
from tkinter import DISABLED, NORMAL
from tkinter import TOP, LEFT, RIGHT, BOTTOM
from PIL import ImageTk
import tkinterdnd2 as tkd
from CorruptedException import CorruptedFileException
from Image import Parser, Image, check_extension, Saver
from Histogram import Histogram, ColorHistogram, GreyHistogram
from tkinter import ttk, messagebox
from CLI import CLI
from Database import Database
from re import match
import pickle
from datetime import datetime
import threading

BLANK_FIG = Figure()
DEFAULT_DND_CANVAS_IMAGE = "../options"+os.sep+"defaultdndtext.jpg"
DEFAULT_RESULT_IMAGE = "../options"+os.sep+"defaultresulttext.jpg"
DEFAULT_MULTISELECT_TEXT = "../options"+os.sep+"defaultmultiselecttext.jpg"
DEFAULT_DB_ERROR_TEXT = "../options"+os.sep+"defaultdberrortext.jpg"

if sys.version_info < (3,7):
    print("This program runs under python 3.7 or more. To use it please get"+
          " you version of python up to date.")
    Mbox("Errors", "This program runs under python 3 or more. To use it"+
         " please get you version of python up to date.")

class CanvasDnD(tk.Canvas):
    """
    ===========================================================================
    This class inherits from the tkinter class Canvas.
    It is supposed to be used with a drag and drop module for tkinter.
    ===========================================================================
    """
    def load_image_drop(self, event, app = None, **kwargs) -> None:
        """
        =======================================================================
        This method get a file contained in a related event and pass it on to
        the load_image_file method.
        =======================================================================
        Arguments:
            event: The event that led to the call of this method
            app: The application calling this method
            
        Calls:
            self.load_image_file
        """
        filename = str(event.data).replace("{", "").replace("}", "")
        self.load_image_file(filename, app);
        
    def _check_file(file, check_extension_method = check_extension,
                    error_message_type = "image", 
                    open_method = lambda x:Image(x).getimg(),
                    verify_method = lambda x:x.verify()) -> bool:
        """
        =======================================================================
        This method checks the file it has been given as argument.
        It verifies it the file is corrupted or not and if the extension
        correspond to the 
        =======================================================================
        Arguments:
            file: The name of the file containing the valued data (default: 
                                                                   the image)
                
            check_extension_method: The method to check if the file correspond
            to an accepted extension (default: Image).The default value is
            the check_extension function in the module Image.
            
            error_message_type: Indicate what type the object is supposed to be
            and will change the message in the error raised if the extension
            does not match. The default value is image.
            
            open_method: Is the function used to open the type of file needed
            The default value is Image(x).getimg().
            
            verify_method: The function used to verify the integrity of the
            file. The default value it is the verify method of the PIL.Image 
            class.
        
        Calls:
            check_extension_method,
            open_method,
            verify_method
            
        Returns:
            True is the extension matches the task and the file passed the
            verify method.
            
        Raises:
            CorruptedFileException if the files does not pass the verify_method
        """
        assert check_extension_method(file), {"The extension of the file"+
                                       " does not corresponds to a(n) "+
                                       f"{error_message_type}"
                                       " extension."}.pop()
        try:
            with open_method(file) as img:
                verify_method(img)
            return(True)
        except:
            raise CorruptedFileException("The file given seems corrupted.")
    
    def load_image_file(self, Sfile, app = None) -> None:
        """
        =======================================================================
        This method is called by load_image_drop and load_image_selection.
        It is the one really checking the validity of the task and opening the
        file into an Image object. It also creates a "thumbnail" by scaling the
        Image using Parser.scale_image to display on the canvas on the GUI.
        =======================================================================
        Arguments:
            Sfile: The path of the file to open.
            
            app: The Application object calling this method.
        Calls:
            CanvasDnD._check_file,
            Application.show_exception,
            Parser.scale_image,
            self.config,
            self.create_image
            Applcation.show_hist
        """
        matplotlib.use("TkAgg")
        try:
            CanvasDnD._check_file(Sfile)
        except CorruptedFileException as ce:
            app.show_exception(ce)
        if app != None:
            app.cli._args.image = Image(Sfile)
            app.image = app.cli._args.image      
        self.img = Image(Sfile)
        tkimg = Parser.scale_image(self.img)
        self.tkImg = ImageTk.PhotoImage(tkimg)
        self.config(height = self.tkImg.height(), width = self.tkImg.width())
        self.create_image(self.tkImg.width(), self.tkImg.height(), 
                          image = self.tkImg, anchor = tk.SE)
        if app != None:
            app.histCheck.configure(state = "normal")
            app.show_hist()
    
    def load_image_selection(self, app = None) -> None:
        """
        =======================================================================
        This method is the one used by the button open (for the files)
        on the GUI.
        It opens a window allowing the user to browse its file and then reads 
        and load the selected file.
        =======================================================================
        Calls:
            filedialog.askopenfilename,
            self.load_image_file
        """
        typeslist = [("IMG file", ".img"), ("JPG file", ".jpg"), 
                     ("PNG file", ".png"), ("PDF file", ".pdf"), 
                     ("GIF file", ".gif"), ("BITMAP", ".bmp"),
                     ("JPEG file", ".jpeg"), ("*", ".*")]
        Sfile = filedialog.askopenfilename(title = "S??lectionnez un fichier", 
                                           filetypes = typeslist)
        if Sfile != "":
            self.load_image_file(Sfile, app)
        
class HelpWindow:
    """
    ===========================================================================
    The HelpWindow class represets a window invoked for a help option.
    It is designed for the Colmeleon project, so the text in the first canva
    is adapted to this project but that apart it can be used easily for any
    project.
    ===========================================================================
    """
    def __init__(self, app, directory = ".."+os.sep+"options"):
        """
        =======================================================================
        This initialisation method creates a window and stores the directory
        containing the informations (the .help files). It also stores the
        Application calling and creating this window so it can toggle its
        help_open value.
        =======================================================================

        Parameters
        ----------
        app : Application
            The application that needs a help window. In this project it will
            always be the main iteration of the Application class.
        directory : String, optional
            The path to the directory containing the .help files.
            The default is "."+os.sep+"options".
        """
        assert isinstance(app, Application) 
        self.dir = directory
        self.word_list = [x[:x.index(".help")] for x in os.listdir(self.dir) 
                          if x.endswith(".help")]
        self.application = app
        self.helpWindow = tk.Tk()
        self.helpWindow.title("help")
        self.helpWindow.geometry("686x480")
        self.helpWindow.config(bg = "#111111")
        self.helpFrame = tk.Frame(self.helpWindow, 
                                   height = 30, 
                                   width = 86)
        self.helpFrame.pack()
        self.accepted_helpText = tk.Text(self.helpFrame, 
                                          height = 4, 
                                          width = 84)
        self.accepted_helpText.pack(side = TOP)
        self.helpText = tk.Text(self.helpFrame, 
                                 height = 28, 
                                 width = 84, 
                                 state = DISABLED)
        self.boxFrame = tk.Frame(self.helpFrame, 
                                     height = 5, 
                                     width = 84)
        self.boxFrame.pack(side = TOP)
        self.wordBox = ttk.Combobox(self.boxFrame, 
                                  values = self.word_list,
                                  state = "readonly")
        self.wordBox.bind("<<ComboboxSelected>>", self.words_help)
        self.wordBox.pack(side = TOP)
        self.helpText.pack(side = TOP)
        self.accepted_helpText.insert("end", "The help about technical terms"+
                    " about the segmentation of an image based on a compact\n"+
                    "representation of the color histogram.\n")
        self.accepted_helpText["state"] = DISABLED
        self.helpWindow.protocol("WM_DELETE_WINDOW", 
                                 self.on_closing_help)
        
    def words_help(self, event) -> None:
        """
        =======================================================================
        This method is called, usually, on a ComboboxSelected event.
        It shows the content of the file wearing the name of the word selected.
        =======================================================================

        Parameters
        ----------
        event : Event
            The event supposed to call this method, in the current project,
            a ComboboxSelected event
        """
        word = self.wordBox.get()
        self.helpText["state"] = NORMAL
        self.helpText.delete("1.0", "end")
        with open(self.dir + os.sep + word + ".help", "r") as help_file:
            self.helpText.insert("end", help_file.read())
        self.helpText["state"] = DISABLED
        
    def on_closing_help(self) -> None:
        """
        =======================================================================
        The on_closing protocol just makes sure that the application knows that
        the HelpWindow has been desttroyed and proceeds to destroy it.
        =======================================================================
        """
        self.application.helpWindow = None
        self.application.helpOpen = False
        self.helpWindow.destroy()
        del(self)
        
    def lift(self) -> None:
        """
        =======================================================================
        This method is used to avoid having to create a second instance of the
        HelpWindow. It just focuses the screen on this window putting it in the
        forground.
        =======================================================================
        """
        self.helpWindow.lift()
        self.helpWindow.focus_force()
        self.helpWindow.grab_set()
        self.helpWindow.grab_release()
        
class Application:
    """
    ===========================================================================
    The main class of the module. It represents the GUI itself.
    This class is a GUI for the project Colmeleon.
    The default arguments are shared with the CLI class and can be found in the
    options/CLI.init file.
    ===========================================================================
    """
    def __on_closing(self) -> None:
       """
       ========================================================================
       This is the closing protocol, it is activated on the closing of the 
       main window.
       Its purpose is to delete every temporary file that has been created 
       during the session and then to destroy the window.
       If a help window is open this protocol will close it before destroying 
       the window.
       ========================================================================
       Calls:
           HelpWindow.on_closing_help
           os.remove,
           os.rmdir,
           TkinterDnD.Tk.destroy,
           TkinterDnD.Tk.quit
       """
       self.histCheckValue.set(False)
       self.show_hist()
       plt.close("all")
       if self.helpOpen:
           self.helpWindow.on_closing_help()
       try:
           for file in os.scandir(self.tmpPath):
               os.remove(file)
           os.rmdir(self.tmpPath)
       except:
           pass
       self.window.destroy()
       self.window.quit()
                
    def show_help(self) -> None:
        """
        =======================================================================
        This method checks if there is already a HelpWindow linked to this
        instance. If there is one, it juste lifts it, if not it instantiate it.
        =======================================================================
        """
        if(self.helpOpen):
            self.helpWindow.lift()
        else:
            self.helpOpen = True
            self.helpWindow = HelpWindow(self)
            self.helpWindow.lift()
    
    def save(self) -> None:
        """
        =======================================================================
        This method is called when the user wants to save the results of the
        retrieval somewhere on their computer. 
        =======================================================================
        The method opens a askdirectory window and saves the selected elements
        in the resultListBox (if none is selected, saves every elements in
        results) into the selected/designated directory (creates one if the
        given path does not lead anywhere).
        """
        defaultDir = {"."+os.sep+"save"
                      +str(datetime.now().strftime("%d-%m-%y-%H-%M-%S")) 
                      if self.cli._args.database == None 
                      else self.cli._args.database}.pop()
        directory = filedialog.askdirectory(title = "Save result to:",
                                            initialdir = defaultDir)
        if directory == "" or directory == None:
            return()
        if not os.path.exists(directory):
            os.mkdir(directory)
        assert os.path.isdir(directory), {"The path for the saver"+
                                          " must lead to a directory."}.pop()
        saver = Saver(directory)
        toSave = [self.cli.results[x] for x 
                  in self.resultListBox.curselection()]
        if len(toSave)==0:
            toSave = self.results
        
        for img in toSave:
            saver.save(img[1])
        return()
    
    def compute(self) -> None:
        """
        =======================================================================
        This method is somewhat the main method of the GUI of Colmeleon.
        It takes into account the arguments and calls the CLI.compute method.
        It then shows the results in the resultListBox.
        It also deactivates almost every option of the GUI during the
        processing. 
        If the database is not yet computed (the histograms have not yet been
        computed and stored) it will ask the user if they want to do it now and
        if yes it calls the Database._calculate_histograms method.
        =======================================================================
        
        Calls :
            CLI.compute
            Database._calculate_histograms
        """
        self.compute_options_to_disabled()
        try:
            self.cli._args.database = Database(self.databaseName.get(),
                                               self.tmpPath)
        except:
            self.resultCanvas.load_image_file(DEFAULT_DB_ERROR_TEXT)
            self.compute_options_to_normal()
            return()
        if not self.cli._args.database.is_computed():
            res = messagebox.askyesno("Database", 
                                "Warning : The database has not been"+
                                " computed yet.\n"+
                                "Are you sure you want to calculate every"+
                                " histogram now?(y/n)")
            if res:
                self.cli._args.database._calculate_histograms()
            else:
                self.compute_options_to_normal()
                return()        
        self.cli._args.depth = self.depthValue.get()
        self.cli._args.bins = self.binsValue.get()
        self.cli._args.incremental = self.incrementalVal.get()
        self.cli._args.grey = self.greyValue.get()
        self.cli._args.noadd = not self.addValue.get()
        self.cli.compute(tmpPath = self.tmpPath)
        self.cli._args.image = self.image
        self.canvas.load_image_file(self.cli._args.image.getpath(), self)
        self.resultListBox.delete(0,tk.END)
        for i in range(len(self.cli.results)):
            self.resultListBox.insert(i, self.cli.results[i][1])
        self.compute_options_to_normal()
        
    def compute_options_to_disabled(self):
        self.addCheck.configure(state = "disabled")
        self.greyCheck.configure(state = "disabled")
        self.incrementalCheck.configure(state = "disabled")
        self.databaseEntry.configure(state = "disabled")
        self.depthEntry.configure(state = "disabled")
        self.binsEntry.configure(state = "disabled")
        self.clearButton.configure(state = "disabled")
        self.computeButton.configure(state = "disabled")
        self.saveOption.configure(state = "disabled")
        
    def compute_options_to_normal(self):
        self.computeButton.configure(state = "normal")
        self.addCheck.configure(state = "normal")
        self.greyCheck.configure(state = "normal")
        self.incrementalCheck.configure(state = "normal")
        self.databaseEntry.configure(state = "normal")
        self.depthEntry.configure(state = "normal")
        self.binsEntry.configure(state = "normal")
        self.clearButton.configure(state = "normal")
        self.saveOption.configure(state = "normal")
    
    def _show_listbox_selection(self, event) -> None:
        """
        =======================================================================
        Called when the user selects a new element on the result listbox.
        It shows the image selected on the result canvas if only one is
        currently selected.
        It shows the DEFAULT_MULTISELECT_TEXT if more than one are currently
        selectted.
        It shows the DEFAULT_RESULT_IMAGE if none are selected.
        =======================================================================

        Parameters
        ----------
        event : Event
            What caused this function to be called. In this GUI it is a 
            # ListboxSelect.
        """
        images = event.widget.curselection()
        wid = event.widget
        if len(images) > 1:
            self.resultCanvas.load_image_file(DEFAULT_MULTISELECT_TEXT)
        elif len(images) == 1:
            self.resultCanvas.load_image_file(wid.get(images[0]))
        else:
            self.resultCanvas.load_image_file(DEFAULT_RESULT_IMAGE)
    
    def parse_background_color(self) -> str:
        """
        =======================================================================
        This method is the parser for default value of the attribute color of
        the background.
        It finds the default value in the self.cli.default file.
        =======================================================================
        Returns:
            Integer stated in the self.default file.
            255 if the default value is None 
            (255 is the default value at initialisation of the Application)
        """
        for s in self.cli.default:
            if match(r"background_color", s):

                if s.endswith("None"):
                    return("#000000")
                else:
                    return(str(s[s.index("=")+1:].strip()))
    
    def show_hist(self) -> None:
        """
        =======================================================================
        This method is linked to the show hisstogram checkbox. It shows a
        matplotlib figure in the TkAgg environnement when called.
        =======================================================================
        """
        matplotlib.use("TkAgg")
        if self.histCheckValue.get() == 1 and self.cli._args.image != None:
            if self.figure == BLANK_FIG:
                self.figure = plt.figure(dpi = 300)
            plt.clf()
            imgpath = self.cli._args.image.getpath()
            try:
              filename=self.cli._args.image.getpath()[imgpath.rindex(os.sep)+1:
                                imgpath.index(".")]
            except:
              filename = pathlib.Path(self.cli._args.image.getpath()).name
            if os.path.exists(self.tmpPath +os.sep+f"Hist{filename}.png"):
                plt.close()
                with open(self.tmpPath+os.sep+f"Hist{filename}.hist", "rb")\
                    as file:
                    self.histo = pickle.load(file)
            else:
                self.histo = Histogram(self.cli._args.image)
                
                if isinstance(self.histo, ColorHistogram):
                    plt.hist(self.histo.get_red())
                    plt.hist(self.histo.get_green())
                    plt.hist(self.histo.get_blue())
                elif isinstance(self.histo, GreyHistogram):
                    plt.hist(self.histo.get_grey())
                    
                plt.show()
                plt.draw()    
                plt.rcParams["figure.figsize"] = (5,4.5)
            
                with open(self.tmpPath+os.sep+f"Hist{filename}.hist", "wb") as file:
                    pickle.dump(self.histo, file, 
                                protocol=pickle.HIGHEST_PROTOCOL)
                plt.savefig(self.tmpPath +os.sep+f"Hist{filename}.png", format="PNG")
        else:
#                filename = self.cli._args.image.getpath()[:
#                                    self.cli._args.image.getpath().index(".")]
#                if os.path.exists(self.tmpPath + f"/Hist{filename}.png"):
#                    os.remove(self.tmpPath + "/Hist{filename}.png")
                plt.close()
    
    def saveparams(self)-> None:
        """
        =======================================================================
        This method save the current state of the GUI in the init file
        (default init file is CLI.init).
        This method is linked to the saveparams button and calls on the
        CLI saveparams method.
        =======================================================================
        """
        try:
            self.cli._args.database = Database(self.databaseEntry.get(),
                                               self.tmpPath)
        except:
            self.cli._args.database = None
        self.cli._args.grey = self.greyValue.get()
        self.cli._args.incremental = self.incrementalVal.get()
        try:
            self.cli._args.bins = int(self.binsEntry.get())
        except:
            self.cli._args.bins = 255
        try:
            self.cli._args.depth = int(self.depthEntry.get())
        except:
            self.cli._args.depth = 5
        self.cli._args.noadd = not self.addValue
        self.cli._saveparams()
        
        
    def clear(self) -> None:
        """
        =======================================================================
        This method clears the GUI and the init file. It resets the values of
        of the parameters to the default one. (see DEFAULT_CLI_VALUE)
        =======================================================================
        """
        self.cli._reset()
        self.resultCanvas.load_image_file(DEFAULT_RESULT_IMAGE)
        self.resultListBox.delete(0,tk.END)
        self.results = []
        self.saveOption.configure(state = "disabled")
        self.cli.parse_default_all() 
        self.parseCLIArgs()
        
    def parseCLIArgs(self) -> None:
        """
        =======================================================================
        This method is used to know the arguments of the cli and set the values
        of the GUI. For it to work the CLI must be initialised so the init file
        must be valid of the arguments given another way.
        =======================================================================
        """
        if self.cli._args.database != None:
            self.databaseName.set(str(self.cli._args.database))
        self.binsValue.set({self.cli._args.bins 
                             if self.cli._args.bins!=None
                             else 255}.pop())
        self.depthValue.set({self.cli._args.depth 
                             if self.cli._args.depth!=None
                             else 5}.pop())
        self.addValue.set(not self.cli._args.noadd)
        self.incrementalVal.set(self.cli._args.incremental)
        self.greyValue.set(self.cli._args.grey)
        self.addValue.set(not self.cli._args.noadd)
        if self.cli._args.image != None:
            self.image = self.cli._args.image
            self.canvas.load_image_file(self.cli._args.image.getpath(), self)
        else:
            self.canvas.load_image_file(DEFAULT_DND_CANVAS_IMAGE, self)
    
    def new_compute_thread_start(self) -> None:
        """
        =======================================================================
        This method only creates a thread for the computation to happend
        without impacting on the way the GUI works and avoid the window not
        responding every time the compute button is clicked.
        =======================================================================
        """
        self.computeThread = threading.Thread(target=self.compute)
        self.computeThread.start()
    
    def __init__(self, options = ".."+os.sep+"options"+os.sep+"CLI.init"):
        self.tmpPath = "temp"
        while os.path.exists(self.tmpPath):
            self.tmpPath += "p"
        os.mkdir(self.tmpPath)
        
        self.cli = CLI(defaultDir=options[:options.rindex(os.sep)], 
            defaultFile = options[options.rindex(os.sep)+1:],
            tmpPath=self.tmpPath)
        self.results = []
        
        self.window = tkd.TkinterDnD.Tk()
        self.window.geometry('800x550')
        self.window.config(bg = self.parse_background_color())
        
        self.ws = tk.Frame(self.window)
        self.ws.pack(side = TOP)
        
        self.optionFrame = tk.Frame(self.ws, height = 10, width = 40)
        self.optionFrame.pack(side = TOP)

        self.frame = tk.Frame(self.ws, height = 60, width = 82)
        self.frame.pack(side = LEFT)
        
        self.emptyLabel = tk.Label(self.frame, text = "")
        self.emptyLabel.pack(side = TOP)
        
        self.resultFrame = tk.Frame(self.ws)
        self.resultFrame.pack(side = RIGHT)
        
        self.frameDnD = tk.Frame(self.frame, height = 23, width = 41)
        self.frameDnD.pack(side = TOP)
        
        self.computeFrame = tk.Frame(self.frame)
        self.computeFrame.pack(side = BOTTOM)
        
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.grab_release()
        
        self.image = self.cli._args.image
        self.figure = Figure()
        self.helpOpen = False
        
        self.dndOptions = tk.Frame(self.frameDnD)
        self.dndOptions.grid(row = 7, column = 1, columnspan = 5)
        self.histCheckValue = tk.BooleanVar()
        self.histCheck = tk.Checkbutton(self.dndOptions, 
                                     disabledforeground = "grey", 
                                     text = "See the histogram", 
                                     variable = self.histCheckValue, 
                                     command = self.show_hist, 
                                     state = DISABLED,
                                     onvalue = True,
                                     offvalue = False)
        self.histCheck.grid(row = 0, column = 0)
        
        self.canvas = CanvasDnD(self.frameDnD, height=250, width=500)
        self.canvas.grid(row = 1, column = 0, rowspan = 3, columnspan = 6)
        self.canvas.drop_target_register(tkd.DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', lambda x:
                                         {self.canvas.load_image_drop(x,self) 
                                          or self.histCheck.configure(
                                             state = "normal")})
        
        self.databaseFrame = tk.Frame(self.computeFrame)
        self.databaseFrame.pack(side = TOP)
        self.databaseName = tk.StringVar()
        self.databaseEntry = tk.Entry(self.databaseFrame,
                                      textvariable = self.databaseName)
        self.databaseLabel = tk.Label(self.databaseFrame, text = "Database: ")
        self.databaseLabel.pack(side = LEFT)
        self.databaseEntry.pack(side = TOP)
        
        self.depthFrame = tk.Frame(self.computeFrame)
        self.depthFrame.pack(side = TOP)
        self.depthValue = tk.IntVar()
        self.depthEntry = tk.Entry(self.depthFrame, 
                                   textvariable = self.depthValue,
                                   text = self.depthValue)
        
        self.depthLabel = tk.Label(self.depthFrame, 
                                   text = "Number of results: ")
        self.depthLabel.pack(side = LEFT)
        self.depthEntry.pack(side = TOP)
        
        self.binsFrame = tk.Frame(self.computeFrame)
        self.binsLabel = tk.Label(self.binsFrame, text = "Number of bins:")
        self.binsValue = tk.IntVar()
        self.binsEntry = tk.Entry(self.binsFrame, text = self.binsValue)
        
        self.binsLabel.pack(side = LEFT)
        self.binsEntry.pack(side = RIGHT)
        self.binsFrame.pack(side = TOP)
        
        self.addValue = tk.BooleanVar()
        self.addCheck = tk.Checkbutton(self.dndOptions,
                                       text = "Add to database",
                                       variable = self.addValue,
                                       onvalue = True,
                                       offvalue = False)
        
        self.addCheck.grid(row = 0, column = 1)
        
        self.incrementalVal = tk.BooleanVar()
        self.incrementalCheck = tk.Checkbutton(self.dndOptions,
                                       text = "Use incremental intersection",
                                       variable = self.incrementalVal,
                                       onvalue = True,
                                       offvalue = False)
        self.incrementalCheck.grid(row = 1, column = 0, columnspan = 2)
        
        self.greyValue = tk.BooleanVar()
        self.greyCheck = tk.Checkbutton(self.dndOptions,
                                       text = "Grey histogram",
                                       variable = self.greyValue, 
                                       onvalue = True,
                                       offvalue = False)
        self.greyCheck.grid(row = 1, column = 3, columnspan = 1)
        
        self.openButton = tk.Button(self.frameDnD, 
                                activebackground = "blue", 
                                bg = "white", 
                                text = "Open", 
                                command = lambda :
                                        self.canvas.load_image_selection(self))
        self.openButton.grid(row = 7, column = 0, columnspan = 1)
        
        self.helpOption = tk.Button(self.optionFrame, 
                                activebackground = "red", 
                                bg = "white", 
                                text = "Help", 
                                command = self.show_help)
        self.helpOption.pack(side = LEFT)
        
        self.saveOption = tk.Button(self.optionFrame, 
                                activebackground = "blue", 
                                bg = "white", 
                                text = "Save", 
                                command = self.save,
                                state = DISABLED)
        self.saveOption.pack(side = LEFT)
        
        self.saveparamsButton = tk.Button(self.optionFrame,
                                          activebackground = "blue", 
                                          bg = "white", 
                                          text = "Saveparams", 
                                          command = self.saveparams)
        self.saveparamsButton.pack(side = LEFT)
        
        self.clearButton = tk.Button(self.optionFrame,
                                          activebackground = "blue", 
                                          bg = "white", 
                                          text = "clear", 
                                          command = self.clear)
        self.clearButton.pack(side = LEFT)
        
        self.computeButton = tk.Button(self.computeFrame, 
                height = 8, 
                width = 58, 
                text = "COMPUTE", 
                activebackground = "yellow", 
                bg = "pink", 
                command = self.new_compute_thread_start)
        self.computeButton.pack(side = TOP)
        
        self.resultLabel = tk.Label(self.resultFrame, text = "Results: ")
        self.resultLabel.pack(side = TOP)
        
        self.resultCanvas = CanvasDnD(self.resultFrame, 
                                      height = 256, 
                                      width = 500)
        self.resultCanvas.pack(side = TOP)
        self.resultCanvas.load_image_file(DEFAULT_RESULT_IMAGE)
        
        self.resultListFrame = tk.Frame(self.resultFrame)
        self.resultListFrame.pack(side = BOTTOM)
        self.resultListBox = tk.Listbox(self.resultListFrame,
                                        height = 15,
                                        width = 50,
                                        selectmode = tk.MULTIPLE)
        self.resultListBox.grid(row = 0, column = 0,
                                rowspan = 10, columnspan = 10)
        self.resultListBox.bind("<<ListboxSelect>>", self._show_listbox_selection)
        
        self.resultScrollBar = tk.Scrollbar(self.resultListFrame,
                                            orient = tk.VERTICAL)
        self.resultScrollBar.grid(row = 0, column = 10,
                                  rowspan = 10, sticky = tk.NS)
        self.resultListBox.configure(yscrollcommand = self.resultScrollBar.set)
        self.resultScrollBar.configure(command = self.resultListBox.yview)
        
        self.parseCLIArgs()
        
        self.window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        
        self.window.title("Colmeleon")
        
        self.window.mainloop()

if __name__ == "__main__":
    a = Application()
    del(a)