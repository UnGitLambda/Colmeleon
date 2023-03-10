#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2

class Histogram:
    """
    ===========================================================================
    Class reprensenting histogram, by default, it instantiate a ColorHistogram
    ===========================================================================
    """
    def __init__(self, img,bins=255, grey = False):
        self.image = img
        self.imageArray = np.asarray(self.image.getimg())
        self.bins = bins
        h,s,v = cv2.split(cv2.cvtColor(cv2.imread(img.getpath()),
                                        cv2.COLOR_BGR2HSV))
        if grey or (s==0).all():
            self.histograms =  GreyHistogram(self.imageArray, self.bins)
        else:
            self.histograms = ColorHistogram(self.imageArray, self.bins)
    
    def color_axes(histo, rgBinsNumber = 16, byBinsNumber = 16,
                wbBinsNumber = 8) ->np.ndarray:
        """
        =======================================================================
        This function will create the color axes used in incremental
        intersection
        =======================================================================
        Argument :
            histo : The concerned histogram
            rgBinsNumber : The number of bins for the rg color axe 
                            (default : 16)
            byBinsNumber : The number of bins for the by color axe 
                            (default : 16)
            wbBinsNumber : The number of bins for the wb color axe 
                            (default :  8)
        Return :
            The keys of rg,by and wb values concatenated into a single vector
            (the key of a value is the fraction of the total number of pixels)
        Raises :
            Exception error if the histogram in input doesn't possess a
                ColorHistogram or a GreyHistogram
        """
        assert type(histo) is Histogram

        #Retrieve the original RGB channels
        if isinstance(histo.histograms, ColorHistogram) :
            r = histo.imageArray[:,:,0]
            g = histo.imageArray[:,:,1]
            b = histo.imageArray[:,:,2]
        elif isinstance(histo.histograms, GreyHistogram) :
            r = histo.imageArray[:,:]
            g,b = r,r
        #Raise an Exception if RGB channels cannot be retrieved
        else :
            raise Exception("The histogram in argument doesn't have a "+
                        "ColorHistogram nor a GreyHistogram, so it isn't "+
                        "possible to create the associated bins histogram")

        #Calculate the new color axes : rg, by, wb
        rg = r - g
        by = 2 * b - r -g
        wb = r + g + b

        #Create histograms of the new color axes
        rgBins = plt.hist(rg.flatten(), bins = rgBinsNumber, 
                                                        range = [0,255])
        byBins = plt.hist(by.flatten(), bins = byBinsNumber, 
                                                        range = [0,255])
        wbBins = plt.hist(wb.flatten(), bins = wbBinsNumber, 
                                                        range = [0,255])

        #Return a single vector of the normalized bins
        total_pixel = len(histo.imageArray[0]) * len(histo.imageArray)
        return np.concatenate([rgBins[0],byBins[0],wbBins[0]])/total_pixel

    def __hash__(self) -> int:
        """
        =======================================================================
        Return the hash value of the histogram subclass
        =======================================================================
        Returns :
            The hash number associated to this object
        """
        return(hash(self.histograms))
            
class GreyHistogram(Histogram) :
    """
    ===========================================================================
    Class reprensenting the case of a histogram in greyscale
    It uses the openCV method to grayscale the image
    The formula is : 0,299*R + 0.587*G + 0.114*B
    ===========================================================================
    """
    def __init__(self, imgArray, bins):
#        self.grey = cv2.cvtColor(imgArray, cv2.COLOR_BGR2GRAY)
        self.greyHistogram = plt.hist(imgArray[:,:].flatten(),range=[0,255], 
                                      color = "grey", 
                                      alpha = 0.5, 
                                      bins = bins)
        
    def get_grey(self) -> np.ndarray:
        """
        =======================================================================
        Return a list of all bins value of the greyscale
        =======================================================================
        Returns :
            The list of the bins value of grey
        """
        return self.greyHistogram[0].astype(int)
    
    def set_grey(self, hist)-> None:
        """
        =======================================================================
        Modify the list of all bins value of the greyscale with the list 
        passing in argument
        =======================================================================
        Arguments:
            hist : The list replacing the current histogram's list
        """
        self.greyHistogram[0] = hist
        
    def __hash__(self) -> int:
        """
        =======================================================================
        Create and return the hash value of the GreyHistogram
        =======================================================================
        Returns :
            The hash number associated to this object
        """
        res = 0
        grey = self.get_grey()
        for i in range(len(grey)):
            res += i*grey[i]
        return int(res)
            
        
class ColorHistogram(Histogram) :
    """
    ===========================================================================
    Class reprensenting the three colored histograms, red, green and blue
    ===========================================================================
    """
    def __init__(self, imgArray, bins):
        self.redHistogram = plt.hist(imgArray[:,:,0].flatten(),range=[0,255], 
                                     color = "red", 
                                     alpha = 0.5, 
                                     bins = bins)
        self.greenHistogram = plt.hist(imgArray[:,:,1].flatten(),
                                       range=[0,255], 
                                       color = "green", 
                                       alpha = 0.5, 
                                       bins = bins)
        self.blueHistogram = plt.hist(imgArray[:,:,2].flatten(),
                                      range=[0,255], 
                                      color = "blue", 
                                      alpha = 0.5, 
                                      bins = bins)
        
    
    def get_red(self)-> np.ndarray:
        """
        =======================================================================
        Return a list of all bins value of the color red
        =======================================================================
        Returns :
            The list of the bins value of red
        """
        return self.redHistogram[0].astype(int)
    
    def get_green(self)-> np.ndarray:
        """
        =======================================================================
        Return a list of all bins value of the color green
        =======================================================================
        Returns :
            The list of the bins value of green
        """
        return self.greenHistogram[0].astype(int)
        
    def get_blue(self) -> np.ndarray:
        """
        =======================================================================
        Return a list of all bins value of the color blue
        =======================================================================
        Returns :
            The list of the bins value of blue
        """
        return self.blueHistogram[0].astype(int)
    
    def set_red(self, hist) -> None:
        """
        =======================================================================
        Modify the list of all bins value of the color red with the 
        list passing in argument
        =======================================================================
        Arguments:
            hist : The list replacing the current red histogram's list
        """
        self.redHistogram[0] = hist
        
    def set_green(self, hist) -> None:
        """
        =======================================================================
        Modify the list of all bins value of the color green with the 
        list passing in argument
        =======================================================================
        Arguments:
            hist : The list replacing the current green histogram's list
        """
        self.greenHistogram[0] = hist
        
    def set_blue(self, hist) -> None:
        """
        =======================================================================
        Modify the list of all bins value of the color blue with the 
        list passing in argument
        =======================================================================
        Arguments:
            hist : The list replacing the current blue histogram's list
        """
        self.blueHistogram[0] = hist
        
    def __hash__(self) -> int:
        """
        =======================================================================
        Create and return the hash value of the ColorHistogram
        =======================================================================
        Returns :
            The hash number associated to this object
        """
        res = 0
        red = self.get_red()
        blue = self.get_blue()
        green = self.get_green()
        for i in range(len(red)):
            res += i*red[i] + i*blue[i] + i*green[i]
        return int(res)


