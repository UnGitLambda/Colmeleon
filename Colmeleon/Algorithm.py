#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from Histogram import ColorHistogram, GreyHistogram, Histogram
from Database import Database
from Image import Image
import numpy as np
import bisect
import matplotlib
from deprecated import deprecated

def jaccard_dist(data1, data2) -> float :
    """
    ===========================================================================
    This function calculate the Jaccard distance of 2 sets
    The result is rounded off to four decimal places.
    ===========================================================================
    Argument : 
        data1 : A set of data
        data2 : A set of data
    Return :
        The Jaccard distance of the two given set
    Raises :
        TypeError when datas in argument can't be converted to a set data
    """

    if isinstance(data1, list) or isinstance(data1, np.ndarray) :
        data1 = set(data1)
    if isinstance(data2, list) or isinstance(data1, np.ndarray) :
        data2 = set(data2)
    
    if not isinstance(data1, set) and not isinstance(data2, set) :
        raise TypeError("Datas in argument aren't of type list or np.ndarray,"+
                        " It is not possible to calculate the jaccard "+
                        "distance if data can't be converted to set.")
    intersect = set.intersection(data1,data2)
    jaccard_index = len(intersect) / (len(data1)+len(data2)-len(intersect))

    #jaccard_distance = 1 - jaccard_index
    return np.around(1 - jaccard_index,decimals = 4)


def euclidean_dist(data1, data2) -> float :
    """
    ===========================================================================
    This function calculate the Euclidean distance of 2 sets
    The result is rounded off to four decimal places.
    ===========================================================================
    Argument : 
        data1 : A set of data
        data2 : A set of data
    Return :
        The Euclidean distance of the two given set
    Raises :
        TypeError when datas in argument can't be converted to np.ndarray
    """
    if isinstance(data1, list) or isinstance(data1, set) :
        data1 = np.array(list(data1))
    if isinstance(data2, list) or isinstance(data2, set) :
        data2 = np.array(list(data2))

    if isinstance(data1, np.ndarray) and isinstance(data2, np.ndarray) :
        return np.around(np.sqrt(np.sum(((data1 - data2) ** 2))),decimals = 4)
    else :
        raise TypeError("Datas in argument aren't of type list or np.ndarray,"+
                        " It is not possible to calculate the euclidean "+
                        "distance in this case.")
   
def intersection(histo_image, histo_model)-> list:
    """
    ===========================================================================
    This function calculates the intersection of two histograms.
    It takes the minimum of each composants (red, green blue and grey) between 
    the model histogram and the image given. 
    ===========================================================================
    Arguments : 
        histo_image : The Histogram object of the image
        histo_model : The Histogram object of the model
    Returns: the histogram data of the intersection of the two histograms.
    
    """
    assert type(histo_image) is Histogram
    assert type(histo_model) is Histogram
    matplotlib.use("Agg")
    histo=[]
    #Defines which histogram is the largest and smallest 
    histo_min = {histo_image if histo_image.bins <= histo_model.bins 
                 else histo_model}.pop()
    histo_max = {histo_image if histo_image.bins >= histo_model.bins 
                 else histo_model}.pop()
    #Calculates the ratio between the size of the two histograms
    ratio = histo_min.bins/histo_max.bins
    
    #Treat all cases : 
    # - image histogram and model histogram are both instance of ColorHistogram
    # - image histogram and model histogram are both instance of GreyHistogram
    # - image histogram is an instance of ColorHistogram and model histogram 
    #   is an instance of GreyHistogram
    # - image histogram is an instance of GreyHistogram and model histogram 
    #   is an instance of ColorHistogram
    if(isinstance(histo_image.histograms, ColorHistogram) 
        and isinstance(histo_model.histograms, ColorHistogram)):      
        histo.append([])
        histo.append([])
        histo.append([])
        
        for j in range(histo_min.bins):
            #To avoid loss of information
            if (j%2) == 0:
                ratio=math.ceil(ratio)
            else:
                ratio=math.floor(ratio)
            #The largest histogram needs to scale up to the smallest
            red = sum(((histo_max.histograms.get_red())
                       [ratio*j : ratio*(j+1)]))
            blue = sum(((histo_max.histograms.get_blue())
                        [ratio*j : ratio*(j+1)]))
            green =sum(((histo_max.histograms.get_green())
                        [ratio*j : ratio*(j+1)]))
            #Add the smaller of the two data
            histo[0].append(min((histo_min.histograms.get_red())[j], red))
            histo[1].append(min((histo_min.histograms.get_blue())[j], blue))
            histo[2].append(min((histo_min.histograms.get_green())[j], green))
        return histo
    if(isinstance(histo_image.histograms, GreyHistogram) 
       and isinstance(histo_model.histograms, GreyHistogram)):
        for j in range(histo_min.bins):
            if (j%2)==0:
                ratio=math.ceil(ratio)
            else: 
                ratio=math.floor(ratio)
            grey = sum(histo_max.histograms.get_grey()[ratio*j : ratio*(j+1)])
            histo.append(min(histo_min.histograms.get_grey()[j],grey))

        return histo
    if(isinstance(histo_image.histograms, ColorHistogram) 
       and isinstance(histo_model.histograms, GreyHistogram)):
        #Transforms the color histogram of the image into a grey histogram
        his = Histogram(histo_image.image, histo_image.bins, True)
        if histo_image.bins == histo_min.bins:
            for j in range(histo_min.bins):
                if (j%2)==0:
                    ratio=math.ceil(ratio)
                else: 
                    ratio=math.floor(ratio)
                grey = (histo_model.histograms.get_grey())[ratio*j:ratio*(j+1)]
                histo.append(min((his.histograms.get_grey())[j], grey))
        else:
            for j in range(histo_min.bins):
                if (j%2)==0:
                    ratio=math.ceil(ratio)
                else: 
                    ratio=math.floor(ratio)
                grey = (his.histograms.get_grey())[ratio*j : ratio*(j+1)]
                histo.append(min((histo_min.histograms.get_grey())[j],grey))
        return histo
    if(isinstance(histo_image.histograms, GreyHistogram) 
       and isinstance(histo_model.histograms, ColorHistogram)):
        #Transforms the color histogram of the model into a grey histogram
        his = Histogram(histo_model.image, histo_image.bins, True)
        if histo_image.bins == histo_min.bins:
            for j in range(histo_min.bins):
                if (j%2)==0:
                    ratio=math.ceil(ratio)
                else: 
                    ratio=math.floor(ratio)
                grey = (his.histograms.get_grey())[ratio*j:ratio*(j+1)]
                histo.append(min((histo_min.histograms.get_grey())[j], grey))
        else:
            for j in range(histo_min.bins):
                if (j%2)==0:
                    ratio=math.ceil(ratio)
                else: 
                    ratio=math.floor(ratio)
                grey = (histo_max.histograms.get_grey())[ratio*j : ratio*(j+1)]
                histo.append(min((his.histograms.get_grey())[j],grey))
        return histo  

@deprecated("This method does not work well, and the intersection method is"+
            " better and faster.")
def intersection2(histImage, histModel):
    matplotlib.use("Agg")
    if (isinstance(histImage.histograms, ColorHistogram) 
        and isinstance(histModel.histograms, GreyHistogram)):
        grey = True
        to_grey_image = lambda x,y: Histogram(x.image, grey = True, bins = y)
        to_grey_model = lambda x,y: x
    elif (isinstance(histImage.histograms, GreyHistogram) 
        and isinstance(histModel.histograms, ColorHistogram)):
        grey = True
        to_grey_model = lambda x,y: Histogram(x.image, grey = True, bins = y)
        to_grey_image = lambda x,y: x
    else:
        if isinstance(histImage.histograms, GreyHistogram):
            grey = True
        else:
            grey = False
        to_grey_model = lambda x,y: x if y==x.bins else Histogram(x.image, 
                                                                  bins = y)
        to_grey_image = lambda x,y: x if y==x.bins else Histogram(x.image, 
                                                                  bins = y)
    if histImage.bins < histModel.bins:
        bins = histImage.bins
        to_bins_model = lambda x: to_grey_model(x, y = histImage.bins)
        to_bins_image = lambda x: to_grey_image(x, y = histImage.bins)
    elif histModel.bins < histImage.bins:
        bins = histModel.bins
        to_bins_model = lambda x: to_grey_model(x, y = histModel.bins)
        to_bins_image = lambda x: to_grey_image(x, y = histImage.bins)
    else:
        bins = histModel.bins
        to_bins_model = lambda x: to_grey_model(x, y = bins)
        to_bins_image = lambda x: to_grey_image(x, y = bins)
    histModel = to_bins_model(histModel)
    histImage = to_bins_image(histImage)
    
    res = []
    
    if grey:
        for i in range(bins):
            res.append(min(histImage.histograms.get_grey()[i],
                           histModel.histograms.get_grey()[i]))
    else:
        res.append([])
        res.append([])
        res.append([])
        for i in range(bins):
          res[0].append(min(histImage.histograms.get_red()[i],
                           histModel.histograms.get_red()[i]))
          res[1].append(min(histImage.histograms.get_green()[i],
                           histModel.histograms.get_green()[i]))
          res[2].append(min(histImage.histograms.get_blue()[i],
                           histModel.histograms.get_blue()[i]))
    return(res)

def match_value(histo_image, histo_model, function = intersection) -> float:
    """
    ===========================================================================
    This function calculates the percentage of correspondence between 
    two histograms. 
    It uses a function that represents the algorithm used.
    ===========================================================================
    Arguments : 
        histo_image : The Histogram object of the image
        histo_model : The Histogram object of the model
        function : the algorithm used for the intersection.
                   By default, it is the intersection function 
    Return : The value of correspondence between two histograms.
    """
    assert isinstance(histo_image, Histogram)
    assert isinstance(histo_model, Histogram)
#    matplotlib.use("Agg")

    histo = function(histo_image, histo_model)
    pixels = {sum(histo_model.histograms.get_red() 
                  if isinstance(histo_model.histograms, ColorHistogram) 
                  else histo_model.histograms.get_grey())}.pop()
    r=0
    b=0
    g=0
    grey=0
    if(isinstance(histo_image.histograms, ColorHistogram) 
       and isinstance(histo_model.histograms, ColorHistogram)):
        for i in range(len(histo[0])):
            r+=histo[0][i]
            b+=histo[1][i]
            g+=histo[2][i]
        value = min([r/pixels,b/pixels,g/pixels])
    else: 
        for i in range(len(histo)):
            grey = histo[i] + grey
        value = grey/pixels
    return value*100


def retrieval(database, histoImage, depth=15, incremental = False, 
                            compareFunction = euclidean_dist,
                            grey = False) -> list:
    """
    ===========================================================================
    This function calculates the closest matching images in the database.
    It returns as many images as the value of depth argument
    ===========================================================================
    Arguments : 
        database    : The Database with all the calculated histograms inside
        histoImage  : The Histogram object of the image
        depth       : The number of Images (paths) thi function will return
        incremental : A boolean reprensenting if the retrieval uses the 
                      Incremental method (True) or not (False).
        compareFunction :The algorithm used for the intersection.
                         By default, it is the euclidean_dist() function
    Return : 
        The n best matched images as a list of tuples (value,pathToImage)
    """
    assert type(depth) is int
    assert type(database) is Database
    assert type(histoImage) is Histogram
    assert type(incremental) is bool
    matplotlib.use("Agg")
   
    result=[]
    value=0

    if incremental : #For incremental method
        histoImage = Histogram.color_axes(histoImage)
        for a in database.bin_histograms():
            if len(result)<depth:
                bisect.insort(result, (compareFunction(histoImage, a[1]), 
                                     a[0]))
            else:
                value=compareFunction(histoImage, a[1])
                if value<result[-1][0]:
                    del(result[-1])
                    bisect.insort(result, (value, a[0]))

    else : #For intersection method
        if grey:
            for a in database.grey_histograms():
                if len(result)<depth:
                    bisect.insort(result, (abs(100-match_value(histoImage,
                                             a[1])), 
                                             a[0]))
                else:
                    value=abs(100.0-match_value(histoImage, a[1]))
                    if value<result[-1][0]:
                        del(result[-1])
                        bisect.insort(result, (value, a[0]))
        else:
            for a in database.histograms():
                if len(result)<depth:
                    bisect.insort(result, (abs(100-match_value(histoImage,
                                             a[1])), 
                                             a[0]))
                else:
                    value=abs(100.0-match_value(histoImage, a[1]))
                    if value<result[-1][0]:
                        del(result[-1])
                        bisect.insort(result, (value, a[0]))
        
    return result
        
        
    
    
def label_images(img):
    """
    ===========================================================================
    This function is a labelling of a given image according to potential(s)
    caracteristic(s)
    ===========================================================================
    """
    assert type(img) is Image

def cluster(db):
    """
    ===========================================================================
    Groups the images in the database according to the labels that have been
    assigned to them
    ===========================================================================
    """
    assert type(db) is Database

