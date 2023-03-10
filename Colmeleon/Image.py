#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import PIL
import os
from Histogram import Histogram
import cv2
import shutil
import pathlib

class Image:
    
    def __init__(self, file, img = None):
        """
        The path to the file is given as a String.
        """
        assert type(file) is str
        assert check_extension(file)
        assert os.path.exists(file)
        file = file.strip()
        if img == None:
            self._path = file
            self._img = Parser._parse(file)
        else:
            self._img = img
            self._path = file

    def to_grey(img, tmpdir): 
        assert type(img) is Image
        image = cv2.imread(img.getpath())
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(tmpdir+os.sep+"grey"+pathlib.Path(img.getpath()).name, grey)
        return(Image(tmpdir+os.sep+"grey"+pathlib.Path(img.getpath()).name))
    
    def display(self):
        return(self._img)
    
    def __str__(self):
        return self._path
    
    def width(self):
        return(self._img.width)
    def height(self):
        return(self._img.height)
    def resize(self, width, height):
        return self._img.resize(size = (width, height), 
                                resample=None, 
                                box=None, 
                                reducing_gap=None)
    
    def getpath(self):
        return self._path
    
    def getimg(self):
        return self._img
    
class Parser:
    def _parse(file):
        """
        The path to the file is given as a String.
        """
        assert type(file) is str
        assert check_extension(file)
        assert os.path.exists(file)
        return(PIL.Image.open(file))

    def scale_image(img):
        assert type(img) is Image, {"Parser : the scaling function takes an"+
                                    " image as argument and not"+
                                    f" {type(img)}"}.pop()
        scale = min(512/img.width(),256/img.height())
        return img.resize(int(scale*img.width()), int(scale*img.height()))

    def _color_constancy(hist):
        assert type(hist) is Histogram
        constancy = hist.get_red() + hist.get_green() + hist.get_blue()
        tmpR = hist.get_red() / constancy
        return(tmpR)
    
    def parse(file):
        """
        The path to the file is given as a String.
        """
        assert type(file) is str
        assert check_extension(file)
        assert os.path.exists(file)
        file = file.strip()
        return(Parser._parse(file))
    
class Saver:
    def __init__(self, directory):
        """
        The path to the direcrtory is given as a String.
        """
        assert type(directory) is str, {"Saver : the path to the directory"+
                                        "must be given as a String, it can "+
                                        f"not be {type(directory)}"}.pop()
        directory =  directory.strip()
        if(not os.path.exists(directory)):
            os.mkdir(directory)
        assert os.path.isdir(directory), {"Saver : The path given does not"+
                                    " lead to a directory, please fix"+
                                    " this issue before trying again."}.pop()
        self._directory = os.path.abspath(directory)

    def save(self,image):
        if isinstance(image, str):
            shutil.copy(image, self._directory +os.sep+ pathlib.Path(image).name)
            return()
        image._img.save("{}/{}".format(self._directory,
                                    pathlib.Path(image._path).nameimage._path))
        
    def __eq__(self, o):
        if(not(isinstance(o,Saver))):
            return(False)
        return(hash(self) == hash(o))
    
    def __hash__(self):
        return hash(self._directory)
    
    def __str__(self):
        return(self._directory)
    
def check_extension(file):
    return {file.endswith(".png") or file.endswith(".pdf") or 
                file.endswith(".jpg") or file.endswith(".jpeg") or 
                file.endswith(".bmp") or file.endswith(".gif")}.pop()