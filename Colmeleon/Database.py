#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import pickle
from Histogram import ColorHistogram, GreyHistogram, Histogram
from Image import Image, check_extension
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from Histogram import Histogram
from shutil import SameFileError

class Database:
    """
    ===========================================================================
    Class taking care of the exploitaation of the database : it creates the
    histograms of all images that are to be taken into account and offers
    methods to retrieve both histograms and images.
    ===========================================================================
    Important public methods :
        histograms : retrieves the histograms of the images that were computed
        images : retrieves the images
        add : allows user to add an image and its histograms to the base
    """

    def __init__(self,directory,tmpdir):
        """
        The path to the directory is given as a String.
        It must be either absolute or relative to the current directory.
        """
        assert type(directory) is str, {"Database: the path to the directory"+
                                        " must be given as a String, it can"+
                                        f" not be {type(directory)}"}.pop()
        assert os.path.exists(directory), {"Database: The path given leads"+
                                           " nowhere, please fix this issue"+
                                           " before trying again."}.pop()
        assert os.path.isdir(directory), {"Database: The path given does not"+
                                          " lead to a directory, please fix"+
                                          " this issue before trying"+
                                          " again."}.pop()
        self._database = str(os.path.abspath(directory))
        self.tmpdir = tmpdir

    def get_dir(self):
        return(self._database)

    def _calculate_histogram(self,file):
        matplotlib.use("Agg")
        """
        =======================================================================
        Instantiates then saves the color histogram and the bins histogram of
        one given file in the database
        =======================================================================
        Argument :
            file : the path to the file, either absolute or relative to the
            current directory.
        Returns :
            a tuple containing : the path to the histogram, the path to the bins
            histogram. Both paths are either absolute or relative to the current
            directory, depends on the path to the database being absolute or not.
        """
        #calculate the histogram
        histo = Histogram(Image(file))
        #save the histogram in the database
        repertory = self._database+os.sep+"histograms"
        name = file[file.rindex(os.sep):len(file)-4]+'_hist'
        with open(repertory+os.sep+name,'wb+') as histo_file:
            pickle.dump(histo,histo_file,protocol=pickle.HIGHEST_PROTOCOL)

        #calculate the bins histogram
        histo_bin = Histogram.color_axes(histo)
        #save the bins histogram in the database
        repertory_bin = self._database+os.sep+"bins_histograms"
        with open(repertory_bin+name+'bin','wb+') as histo_bin_file:
            pickle.dump(histo_bin,histo_bin_file,
                        protocol=pickle.HIGHEST_PROTOCOL)
        
        #calculate the grey histogram
        histo_grey = Histogram(Image.to_grey(Image(file),self.tmpdir),
                               grey = True)
        repertory_grey = self._database+os.sep+"grey_histograms"
        with open(repertory_grey+name+'grey','wb+') as histo_grey_file:
            pickle.dump(histo_grey,histo_grey_file,
                        protocol=pickle.HIGHEST_PROTOCOL)
        
        #returns paths to all histogram files
        return (repertory+name,
                repertory_bin+name+'bin',
                repertory_grey+name+'grey')

    def explore(self, depth=5)->list:
        """
        =======================================================================
        Explore the database down to depth. By default, explore only the first
        directory.
        =======================================================================
        Arguments :
            depth : the depth to which it must be explored. If greater than the
            real depth, all the database will be explored. Should not be
            greater than 5 for efficiency reasons.
        Returns :
            List of the paths of all files in the database, in form of strings.
        """
        res = []
        #supress the last separator to not falsely count it
        directory = self._database.rstrip(os.sep)
        assert os.path.isdir(directory)
        #calculate the depth of first directory to track the depth of the
        #search
        num_sep = directory.count(os.sep)
        #start of exploration
        for root, dirs, files in os.walk(directory):
            #we're only interested in the files
            for file in files :
                res.append(str(os.path.join(root,
                                            file)))
            num_sep_this = root.count(os.sep)
            #if it's already max depth
            if num_sep + depth <= num_sep_this:
                #do not explore deeper
                del dirs[:]
        return res

    def is_computed(self):
        files = self.explore()
        for file in files :
            if file.endswith("histograms.csv") :
                return True
        return False

    def _calculate_histograms(self, max_depth=1):
        """
        =======================================================================
        Computes all images in the database to create their histograms,
        then stocks them in a new directory named "histograms".
        Note : all Histogram objects are pickled before being saved.
        =======================================================================
        Arguments :
            max_depth : the depth of the database. Confere to explore for
            details.
        """
        matplotlib.use("Agg")
        #TODO optimize
        depth = max_depth
        files = self.explore()

        #all histograms are saved in a dedicated repertory
        repertory = self._database+os.sep+"histograms"
        if not os.path.exists(repertory):
            os.makedirs(repertory)

        #all bins_histograms are saved in a dedicated repertory
        repertory_bin = self._database+os.sep+"bins_histograms"
        if not os.path.exists(repertory_bin):
            os.makedirs(repertory_bin)
        
        repertory_grey = self._database+os.sep+"grey_histograms"
        if not os.path.exists(repertory_grey):
            os.makedirs(repertory_grey)

        #if histograms.csv exists in the database
        if self.is_computed() :
            #first find all images that already had their histogram created
            with open(self._database+os.sep+'histograms.csv','r') as csv_file :
                filereader = csv.reader(csv_file)
                images_ready = []
                for item in list(filereader) :
                    if len(item)>0 :
                        images_ready.append(item[0])
            #then add the new images
            with open(self._database+os.sep+"histograms.csv",'a') as csv_file :
                filewriter = csv.writer(csv_file)
                #we'll consider the images that do not already have their
                #histogram
                for file in files :
                    if check_extension(file) and (os.path.abspath(file) not
                                                  in images_ready) :
                        histo = self._calculate_histogram(file)
                        #save the path to image and the histogram in csv
                        filewriter.writerow([os.path.abspath(file),
                                             histo[0],
                                             histo[1],
                                             histo[2]])

        #if there is no histograms.csv file already existing in the directory
        else:
            with open(self._database+os.sep+'histograms.csv','w') as csv_file :
                filewriter = csv.writer(csv_file,delimiter=',')
                for file in files:
                    #we only consider valid image formats
                    if check_extension(file) :
                        histo = self._calculate_histogram(file)
                        #save the path to image and the histogram in csv
                        filewriter.writerow([os.path.abspath(file),
                                             histo[0],
                                             histo[1],
                                             histo[2]])

    def histograms(self):
        """
        =======================================================================
        Generator that unpickle all the histograms and generates one at a time
        with the path to its image.
        =======================================================================
        Yields :
            a tuple (pointer to image,histogram) for each image in the base.
        """
        matplotlib.use("Agg")
        files = os.listdir(self._database)
        #res = []
        #find the histograms.csv file
        if 'histograms.csv' in files :
            with open(self._database+os.sep+'histograms.csv','r') as csv_file :
                #read the file to find the histograms
                filereader = csv.reader(csv_file)
                for item in filereader :
                    #to skip blank lines
                    if len(item)>0:
                        #unpickle the histogram
                        histo = None
                        with open(os.path.abspath(item[1]),
                                  'rb') as pickled_histo :
                            histo = pickle.load(pickled_histo)
                        #res.append((item[0],histo))
                        yield (item[0],histo)
        else :
            print("Caution: the histograms were never calculated"+
                  " for this database.")

        #return res

    def bin_histograms(self):
        """
        =======================================================================
        Generator that unpickle all the bins_histograms and generates one at a
        time with the path to its image.
        =======================================================================
        Yields :
            a tuple (pointer to image,histogram) for each image in the base.
        """
        matplotlib.use("Agg")
        files = os.listdir(self._database)
        #find the histograms.csv file
        if 'histograms.csv' in files :
            with open(self._database+os.sep+'histograms.csv','r') as csv_file :
                #read the file to find the histograms
                filereader = csv.reader(csv_file)
                for item in filereader :
                    #to skip blank lines
                    if len(item)>0:
                        #unpickle the histogram
                        histo = None
                        with open(os.path.abspath(item[2])
                                  ,'rb') as pickled_histo :
                            histo = pickle.load(pickled_histo)
                        #res.append((item[0],histo))
                        yield (item[0],histo)
        else :
            print("Caution: the histograms were never calculated"+
                  " for this database.")
            
    def grey_histograms(self):
        """
        =======================================================================
        Generator that unpickle all the grey_histograms and generates one at a
        time with the path to its image.
        =======================================================================
        Yields :
            a tuple (pointer to image,histogram) for each image in the base.
        """
        matplotlib.use("Agg")
        files = os.listdir(self._database)
        #find the histograms.csv file
        if 'histograms.csv' in files :
            with open(self._database+os.sep+'histograms.csv','r') as csv_file :
                #read the file to find the histograms
                filereader = csv.reader(csv_file)
                for item in filereader :
                    #to skip blank lines
                    if len(item)>0:
                        #unpickle the histogram
                        histo = None
                        with open(os.path.abspath(item[3])
                                  ,'rb') as pickled_histo :
                            histo = pickle.load(pickled_histo)
                        #res.append((item[0],histo))
                        yield (item[0],histo)
        else :
            print("Caution: the histograms were never calculated"+
                  " for this database.")

    def images(self)->list:
        """
        Returns:
            a list containing pointers to all images in the database
        """
        files = os.listdir(self._database)
        res = []
        for file in files:
            if check_extension(file):
                res.append(file)
        return res



    def add(self,img,histo,bin_histo = None):
        """
        =======================================================================
        Allows user to add an image file and its Histogram object to the base.
        Will compute the bin_histogram if not provided and add it too.
        =======================================================================
        Returns :
            true if couple was correctly added to the database.
        Arguments :
            img : the path to the image file to be added
            histo : the Histogram object of the image
            bin_histo : potential bin_histogram. If none, the function compute
            it.
        """
        try:
            matplotlib.use("Agg")
            files = os.listdir(self._database)
            #creates needed directories if need be
            repertory = self._database+os.sep+"histograms"
            if not os.path.exists(repertory):
                os.makedirs(repertory)
            repertory_bin = self._database+os.sep+"bins_histograms"
            if not os.path.exists(repertory_bin):
                os.makedirs(repertory_bin)
            repertory_grey = self._database+os.sep+"grey_histograms"
            if not os.path.exists(repertory_grey):
                os.makedirs(repertory_grey)
            #add image
            name_img = os.path.basename(str(img))
            new_path = os.path.abspath(self._database+os.sep+name_img)
            shutil.copy(str(img),new_path)
            #save the histogram in the database
            if isinstance(histo, ColorHistogram):
                #take care of the color histogram
                name_histo = new_path[new_path.rindex(os.sep):
                                      new_path.rindex(".")-1]+'_hist'
                with open(repertory+os.sep+name_histo,'wb+') as histo_file :
                    pickle.dump(histo,histo_file,
                                protocol=pickle.HIGHEST_PROTOCOL)
                #take care of the grey histogram : needs be created
                name_histo_g = name_histo+"grey"
                histo_g = Histogram(Image.to_grey(Image(img),self.tmpdir))
                with open(repertory_grey+os.sep+name_histo_g,'wb+')\
                    as histog_file:
                    pickle.dump(histo_g,histog_file,
                                protocol=pickle.HIGHEST_PROTOCOL)                
            else:
                #take care of grey histogram that was given
                name_histo_g = new_path[new_path.rindex(os.sep):
                                      new_path.rindex(".")-1]+'_histgrey'
                with open(repertory_grey+os.sep+name_histo_g,'wb+')\
                    as histog_file :
                    pickle.dump(histo,histog_file,
                                protocol=pickle.HIGHEST_PROTOCOL)
                #creates the color histogram
                name_histo = name_histo_g[:-4]
                histo_c = Histogram(Image(img))
                with open(repertory+os.sep+name_histo,'wb+') as histo_file :
                    pickle.dump(histo_c,histo_file,
                                protocol=pickle.HIGHEST_PROTOCOL)
            #create bin_histo if need be
            if bin_histo == None :
                bin_histo = Histogram.color_axes(histo)
            #save the bin_histo
            with open(repertory_bin+os.sep+name_histo+"bin",'wb+') \
                as b_histo_file :
                pickle.dump(bin_histo,b_histo_file,
                            protocol=pickle.HIGHEST_PROTOCOL)
            #
            #check if database isn't empty
            if 'histograms.csv' in files :
                with open(self._database+os.sep+'histograms.csv','a') \
                    as csv_file:
                    #we add the couple of adresses to the csv file
                    filewriter = csv.writer(csv_file)
                    filewriter.writerow([new_path,
                                         repertory+os.sep+name_histo,
                                         repertory_bin+os.sep+name_histo+"bin"])
            #this image is the first in the base
            else :
                print("This is the first image added to that base")
                with open(self._database+os.sep+'histograms.csv','w+') \
                    as csv_file :
                    #we add the couple of adresses to the csv file
                    filewriter = csv.writer(csv_file)
                    filewriter.writerow([new_path,
                                         repertory+os.sep+name_histo,
                                         repertory_bin+os.sep+name_histo+"bin",
                                         repertory_grey+os.sep+name_histo_g])
        except SameFileError as e:
            return()

    def __str__(self):
        return(self._database)

