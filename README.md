# Colmeleon  
## L3F1 2021-2022  
### Mathilde Bonin, Eyal Cohen, Elona Lahmi, Jeremy Vong  
Image Segmentation Framework based on a compact representation of the colour histogram.  
This project was part of my curiculum at University of Paris Cité in year 3.  
  
## Setup
To setup the application, you can click on the executable file in the directory corresponding to you Operation System.  
Another way to setup the application is to go in the Colmeleon directory and to click on the setup.py file.  
### Verify that the setup was done correctly  
A window should appear once you clicked on the previous files for the first time attesting that the setup was successful.  
If not, you can verify that the setup was done by checking in the options directory if the file tosetup.txt still exists. 
If it is absent, then the setup was, at least, run.  
If the application still does not work, the setup may have been unsuccessful. 
To try to run the setup again just create an empty tosetup.txt file in the options directory and do this step once again.
If the problem persists, please try deleting this program all toogether and downloading it again. 
If it still persists, try downloading python again, if it still does not work, you may try to download the following packages by using pip in the console/terminal:
- tkinterdnd2  
- opencv-python  
- matplotlib  
- datetime  
- argparse  
- pathlib  
- numpy  
- deprecated    
  
If after all these steps, the error persists, please refer to the bug reporting section.  
  
## Using the application  
To use the application, you can either opt for a GUI or a command line use.  
### Command Line  
Here is the full version of the command line with the optional argument between brackets and the mandatory arguments without and the elements to replace by their actual value between chevron.  
python3 Segmentation.py \-\-file \<filename\> \-\-database \<Database Path\> \[\-\-depth \<depth\>\] \[\-\-bins \<bins number\>\] \[\-\-save \<directory\>\] \[\-\-add\] \[\-\-incremental\] \[\-\-grey\] \[\-\-saveparams\]  
#### Arguments  
Here an explanation of how to use those arguments:  
- file: The image to input. The one you wish to find matches to in the database.  
- database: The root directory of the database local representation. The database must be represented as nested directories, with the deepest ones containing the images. The program is provided with 2 small database of chameleons.  
- depth: The number of results to retrieve. The default value is 5.  
- bins: The number of bins to use when creating the histograms representing the images. The default value is 256.  
- save: The directory in which you want to save the results retrieved if needed.  
- add: This boolean parameter allows you to save the given image in file in the database.  
- incremental: This boolean parameter allows you to use the incremental intersection method instead of the classic intersection method.  
- grey: This boolean parameter allows you to use grey level histograms instead of the classic colour histograms.  
- saveparams: This boolean parameter allows you to save the parameters of this instance as a serialization of these. 
Then you can run the program without entering the parameters and the same instance will be used. 
To put the values of boolean parameters back to false, you must go in the options file and set them manually.  

### GUI (Graphical User Interface)
To use the GUI, please read the previous section, about the command line usage of the program.  
The same arguments will be present but here, the boolean parameters will be in tickboxes and the other parameters will be entries.  
The optional parameters will all have their default values written at the launch of the GUI.  
If you saved a new default value in another run, this will be the new value in the GUI, 
no matter if you saved it using the command line, manually in the file or using the GUI.  
During computation, the GUI may freeze a bit or lag. 
Please do not try to close it just because of that, you will have to compute it all over again.  


## Copyright
Copyright (c) 2022, Mathilde Bonin, Eyal Cohen, Elona Lahmi, Jeremy Vong, Laurent Wendling  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.  

