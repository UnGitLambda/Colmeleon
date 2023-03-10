#!/usr/bin/env python3
# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import sys
    import ctypes

    def Mbox(title, text, style):
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)
    
    if sys.version_info < (3,7):
        print("This program runs under python 3.7 or more. To use it please "+
              "get you version of python up to date.")
        Mbox("Errors", "This program runs under python 3 or more. To use it"+
             " please get you version of python up to date.")

from argparse import ArgumentParser, ArgumentTypeError
import pathlib
import os
from sys import argv
from Image import Saver,Image
from Database import Database
import Algorithm
from Histogram import Histogram

DEFAULT_CLI_OPTIONS = ["image=None\n",
                "database=.."+os.sep+"Colmeleon"+os.sep+"chameleon_smallDB\n",
                "depth=5\n",
                "bins=255\n","saver=None\n","noadd=False\n",
                "incremental=False\n","grey=False\n",
                "background_color=#554356\n"]

class CLI():
    """
    ===========================================================================
    The CLI class represents the Command-Line Interface.
    Meaning that it is instanciated when calling the program as a command line.
    ===========================================================================
    The syntax of the command line is:
        --image,--file,-f, the name of the file containing the image to process
        --database, -db, the path to the database, represented by a directory
        full of images, or full of directories full of images, etc. (Please
        avoid to much depth, as it would slow the program), for more 
        information see documentation of Database.py
        --depth, -d, the number of images supposed to be returned by the 
        retrieval
        --bins, -b, the number of bins when creating an Histogram 
        (see Histogram.py)
        --saver,--save, -s, the directory in which the images from the 
        retrieval will be saved
        --noadd, if present will negate the operation of adding the image used
        to the database
        --incremental, if present will use the incremental intersection
        algorithm instead of the normal intersection
        --grey, if present will use grey scale histograms instead color
        histograms
        --saveparams, if present will save the given parameters as default in
        the CLI.init file
        --reset, --clear, -c, if present the program will not consider any
        other argument and reset the file CLI.init to the default values 
        (see DEFAULT_CLI_OPTIONS)
    """
    def __init__(self, defaultFile = "CLI.init", defaultDir = ".."+os.sep+"options",
                 tmpPath = None):
        """
        =======================================================================
        This init creates an object based on the current sys.argv and the 
        values in the self.default file.
        To see what each argument does, look at the documentation of the class.
        The call to this method will only create the CLI object, for the
        program to run, use the start method.
        =======================================================================
        """
        self.tmpPath = tmpPath
        self.defaultDir = defaultDir
        self.defaultFile = defaultFile
            
        if not os.path.exists(defaultDir):
            os.mkdir(defaultDir)
        self.default_path = defaultDir + os.sep + defaultFile
        if not os.path.exists(self.default_path):
            with open(self.default_path, "w+") as file:
                file.writelines(DEFAULT_CLI_OPTIONS)
        with open(self.default_path, "r") as file:
            self.default = file.read().split("\n")
        if self.default[-1] == "":
            self.default.remove("")
        self.parser = ArgumentParser()
        self._add_arguments(self.parser)
        self._args, self._unknown = self.parser.parse_known_args(argv)
        del(self._unknown[0])
        
    def start(self) -> None:
        """
        =======================================================================
        This method runs the program intended for Segmentation tool.
        It will do, according to the given parameters actions in a sequence.
        It will start by cheking the number of args present in argv and if
        none are given, it will present the software to the user.
        Then if the argument reset (or clear or c) is present it will not
        consider any other argument and just reset the CLI.init file.
        Then if the saveparams argument is used, it will save the given params
        to the CLI.init file as new default arguments.
        Finally it will make calls according to the given arguments in the CLI.
        =======================================================================
        """
        if len(argv) == 1:
            print("Color histogram based segmentation tool\n"+
                  "Version: 1.0\nauthors: Group L3F1\nMembers : "+
                  "Mathilde Bonin, Eyal Cohen, Elona Lahmi, J??r??my Vong\n")
            if self.default == DEFAULT_CLI_OPTIONS.split("\n"):
                return
        if self._args.reset:
            self.default.close()
            self._reset()
            return
        if self._args.saveparams:
            if not self._saveparams():
                return
        if self._args.image == None:
            raise ArgumentTypeError("--image, --file or -f argument not "+
                    "used but no default value found.\nPlease state "+
                    "the file containing the image to process.")
        if self._args.database == None:
            raise ArgumentTypeError("--database or -db argument not "+
                    "used but no default value found.\nPlease state "+
                    "the directory containing the database for "+
                    "retrieval.")
        self.compute()
        for img in self.results:
            print(img[1] + "                 ||||| distance: " + str(img[0]))
            
    def _reset(self) -> None:
        """
        =======================================================================
        This method is called when the --reset, --clear or -c argument is used.
        It is also called when there is an error while saving the parameters.
        It could be called whenever data is lost about the self.default file.
        It erases anything in the file and writes the arguments stated as
        default at the beggining of the file.
        =======================================================================
        """
        with open(self.default_path, "w+") as file:
            file.writelines(DEFAULT_CLI_OPTIONS)
        
    def _add_arguments(self, parser) -> None:
        """
        =======================================================================
        This method is called at the initialisation.
        It initialise the different arguments in the parser from argparse.
        It just uses the function argparse.ArgumentParser.add_argument.
        For more information check the documentation of the argparse module.
        =======================================================================
        Arguments:
            parser: argparse.ArgumentParser used to parse the command line
        """
        parser.add_argument("--image",
                            "--file", 
                            "-f", 
                            metavar = "<file>", 
                            type = Image, 
                            default = self.parse_default_image(),
                            help = "the name of the file "+
                            "containing the image to process")
        parser.add_argument("--database", 
                            "-db", 
                            metavar = "<path>", 
                            type = Database, 
                            default = self.parse_default_database(),
                            help = "the path to the database"+
                            ", represented by a directory full of images, or"+
                            " full of directories full of images, etc. (Pleas"+
                            "e avoid to much depth, as it would slow the prog"+
                            "ram), for more information see documentation of"+
                            " Database.py")
        parser.add_argument("--depth", 
                            "-d", 
                            type = int, 
                            metavar = "<depth>", 
                            default = self.parse_default_depth(),
                            help = "the number of images"+
                            " supposed to be returned by the retrieval")
        parser.add_argument("--bins", 
                            "-b", 
                            type = int, 
                            metavar = "<bins number>", 
                            default = self.parse_default_bins(),
                            help = "the number of bins when"+
                            " creating an Histogram (see Histogram.py)")
        parser.add_argument("--saver",
                            "--save", 
                            "-s", 
                            metavar = "<directory>", 
                            type = Saver, 
                            default = self.parse_default_saver(),
                            help = "the directory in wh"+
                            "ich the images from the retrieval will be saved")
        parser.add_argument("--noadd", 
                            action = "store_true", 
                            default = self.parse_default_noadd(),
                            help = "if present will negate the"+
                            " operation of adding the image used to the"+
                            " database")
        parser.add_argument("--incremental", 
                            action = "store_true", 
                            default = self.parse_default_incremental(),
                            help = "if present will use the"+
                            " incremental intersection algorithm instead of"+
                            " the normal intersection")
        parser.add_argument("--grey", 
                            "-g", 
                            action = "store_true", 
                            default = self.parse_default_grey(),
                            help = "if present will use grey scale"+
                            " histograms instead color histograms")
        parser.add_argument("--saveparams", 
                            "-sp", 
                            action = "store_true", 
                            default = False,
                            help = "if present will save the "+
                            "given parameters as default in the CLI.init file")
        parser.add_argument("--reset", 
                            "--clear", 
                            "-c", 
                            action = "store_true", 
                            default = False,
                            help = "if present the"+
                            " program will not consider any other argument "+
                            "and reset the file CLI.init to the default value"+
                            "s (see DEFAULT_CLI_OPTIONS)")
        
    def parse_default_image(self) -> Image:
        """
        =======================================================================
        This method is the parser for default value of the attribute image.
        It is called when the --image, --file or -f argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Image created using the path stated in the self.default file.
            (None is the default value at initialisation of the Application)
        Raises:
            argparse.ArgumentError if the default value is None.
        """
        for s in self.default:
            if s.startswith("image"):
                if s.endswith("None"):
                    return(None)
                else:
                    return(Image(s[s.index("=")+1:].strip().replace('"','')))
        return(None)
        
    def parse_default_database(self) -> pathlib.Path:
        """
        =======================================================================
        This method is the parser for default value of the attribute database.
        It is called when the --database or -db argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Database created using the path stated in the self.default file.
            (None is the default value at initialisation of the Application)
        Raises:
            argparse.ArgumentError if the default value is None.
        """
        for s in self.default:
            if s.startswith("database"):
                if s.endswith("None"):
                    return(None)
                else:
                    return(Database(s[s.index("=")+1:].strip().replace('"',
                                                                       ''),
                                    self.tmpPath))
        return(None)
    
    def parse_default_depth(self) -> int:
        """
        =======================================================================
        This method is the parser for default value of the attribute database.
        It is called when the --depth or -d argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Integer stated in the self.default file.
            5 if the default value is None 
            (5 is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("depth"):
                if s.endswith("None"):
                    return(5)
                else:
                    return(int(s[s.index("=")+1:].strip().replace('"','')))
        return(15)
    
    def parse_default_bins(self) -> int:
        """
        =======================================================================
        This method is the parser for default value of the attribute database.
        It is called when the --database or -db argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Integer stated in the self.default file.
            255 if the default value is None 
            (255 is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("bins"):
                if s.endswith("None"):
                    return(255)
                else:
                    return(int(s[s.index("=")+1:].strip().replace('"','')))
        return(255)
    
    def parse_default_saver(self) -> Saver:
        """
        =======================================================================
        This method is the parser for default value of the attribute saver.
        It is called when the --saver, --save or -s argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Saver created using the path stated in the self.default file.
            None if the default value is None 
            (None is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("saver"):
                if s.endswith("None"):
                    return(None)
                else:
                    return(Saver(s[s.index("=")+1:].strip().replace('"','')))
        return(None)
    
    def parse_default_noadd(self) -> bool:
        """
        =======================================================================
        This method is the parser for default value of the attribute noadd.
        It is called when the --noadd argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Boolean based on the information in the self.default file.
            (False is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("noadd"):
                if s.endswith("None"):
                    return(False)
                else:
                    return({s[s.index("=")+1:].strip().replace('"','').lower()
                            =="true"}.pop())
        return(False)
    
    def parse_default_incremental(self) -> bool:
        """
        =======================================================================
        This method is the parser for default value of the attribute
        incremental.
        It is called when the --incremental argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Boolean based on the information in the self.default file.
            (False is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("incremental"):
                if s.endswith("None"):
                    return(False)
                else:
                    return({s[s.index("=")+1:].strip().replace('"','').lower()
                            =="true"}.pop())
        return(False)
    
    def parse_default_grey(self) -> bool:
        """
        =======================================================================
        This method is the parser for default value of the attribute grey.
        It is called when the --grey argument is not used.
        It finds the default value in the self.default file.
        =======================================================================
        Returns:
            Boolean based on the information in the self.default file.
            (False is the default value at initialisation of the Application)
        """
        for s in self.default:
            if s.startswith("grey"):
                if s.endswith("None"):
                    return(False)
                else:
                    return({s[s.index("=")+1:].strip().replace('"','').lower()
                            =="true"}.pop())
        return(False)
            
    
    def parse_default_all(self) -> None:
        self._args, self._unknown = self.parser.parse_known_args([])
        
    def _saveparams(self) -> bool:
        """
        =======================================================================
        This method is called when the argument --saveparams or -sp is used.
        It saves the given parameters as default in the self.default file.
        =======================================================================
        Returns:
            True if everything went well
            False if not
        """
        with open("."+os.sep+"options"+os.sep+"CLI.init", "r") as options:
            data = options.read().split("\n")
        while("" in data):
            data.remove("")
        for i in range(len(data)):
            try:
                if data[i].startswith("background_color"):
                    continue
                info = data[i]
                attr = info[:info.index("=")].strip()
                data[i] = f"{attr} = {self._args.__getattribute__(attr)}\n"
            except:
                print("An error was raised when saving the parameters."+
                      "The file CLI.init has been reseted. (--reset)"+
                      "Sorry for the inconveniance.")
                self._reset()
                return(False)
        with open("."+os.sep+"options"+os.sep+"CLI.init", "w") as options:
            options.writelines(data)
        return(True)
    
    
    def compute(self, tmpPath = None) -> None:
        if tmpPath == None:
            tmpPath = self.tmpPath
        if self._args.grey:
            self._args.image = Image.to_grey(self._args.image, tmpPath)
        self.histogram = Histogram(self._args.image, bins = self._args.bins)
        if not self._args.database.is_computed():
            if __name__ == "__main__":
                ans = ""
                while ans != "y" and ans != "n" and ans != "yes" and ans!="no":
                    print("Warning : The database has not been computed yet."+
                          "\nAre you sure you want to calculate every "+
                          "histogram now?(y/n)")
                    ans = input().strip().lower()
                    if(ans == "y" or ans == "yes"):
                        self._args.database._calculate_histograms()
        self.results = Algorithm.retrieval(self._args.database, 
                                    self.histogram, 
                                    depth = self._args.depth,
                                    incremental = self._args.incremental,
                                    compareFunction= Algorithm.euclidean_dist)
        if not self._args.noadd:
            self._args.database.add(self._args.image.getpath(), self.histogram)
        if self._args.saver != None:
            for img in self.results:
                self._args.saver.save(img[1])
                
if __name__ == "__main__":
    tmpPath = "temp"
    while os.path.exists(tmpPath):
        tmpPath += "p"
    os.mkdir(tmpPath)
    cli = CLI(tmpPath)
    try:
        cli.start()
    except PermissionError:
        print("It seems that there was a problem with the permissions of the"
              +" given file. We could not save the image. Please try again "+
              "after fixing this.")
        pass
    except AssertionError as e:
        print("There was an error during the execution : " + str(e))
        pass
    except SystemExit as e:
        if e.code == 0:
            pass
        else:
            print("There seems to be an Error. " + str(e))
            pass
    try:
        for file in os.scandir(tmpPath):
            os.remove(file)
        os.rmdir(tmpPath)
        if "temp" in os.listdir(cli.defaultDir):
            os.remove(cli.defaultDir + os.sep + "temp")
    except:
        pass