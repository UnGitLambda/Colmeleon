import unittest as ut
from Histogram import ColorHistogram, GreyHistogram, Histogram
from Image import Image
import os


maindir = os.path.dirname(__file__)
unittestdir = os.path.join(maindir, 'UnitTesting','Histogram' )

expectation = [ 
    #[path , greyscale_boolean , index of the bins values  ]
    [os.path.join(unittestdir,'red_square.png' )    , False , [254,0,0] ],
    [os.path.join(unittestdir,'green_square.png' )  , False , [0,254,0] ],
    [os.path.join(unittestdir,'blue_square.png' )   , False , [0,0,254] ],

    [os.path.join(unittestdir,'magenta_square.png'), False , [254,0,254] ],
    [os.path.join(unittestdir,'cyan_square.png' )  , False , [0,254,254] ],
    [os.path.join(unittestdir,'yellow_square.png' ), False  ,[254,254,0] ],

    [os.path.join(unittestdir,'black_square.png' ) , True , [0] ],
    [os.path.join(unittestdir,'grey_square.png' )  , True , [150] ],
    [os.path.join(unittestdir,'white_square.png' ) , True , [254] ],

]


class TestHistogram(ut.TestCase):
    
    def setUp(self):
        pass

    def test_init(self):
        for path, a,b in expectation :
            histo = Histogram(Image(path),bins=255)
            if not(a) :
                self.assertIsInstance(histo.histograms,ColorHistogram)
                self.assertNotIsInstance(histo.histograms,GreyHistogram)
            else :
                self.assertNotIsInstance(histo.histograms,ColorHistogram)
                self.assertIsInstance(histo.histograms,GreyHistogram)
            
            histo_grey = Histogram(Image(path),bins=255, grey = True)
            self.assertIsInstance(histo_grey.histograms,GreyHistogram)

class TestColorHistogram(ut.TestCase):
    def test_init(self):
        pass

    def test_histograms_length(self):
        testbins = 255
        for path, a,b in expectation :
            histo = Histogram(Image(path),bins=testbins)
            if isinstance(histo.histograms,ColorHistogram) :
                self.assertEqual(len(histo.histograms.get_red()), testbins)
                self.assertEqual(len(histo.histograms.get_green()), testbins)
                self.assertEqual(len(histo.histograms.get_blue()), testbins)
            else :
                self.assertEqual(len(histo.histograms.get_grey()), testbins)
                

    def test_get_color(self):
        testbins = 255
        for path, a,b in expectation :
            histo = Histogram(Image(path),bins=testbins)
            if isinstance(histo.histograms,ColorHistogram) :
                for i in range(len(b)) :
                    expected_list = [0 for j in range(testbins)]
                    expected_list[b[i]] = 10000
                    if i ==0 : 
                        self.assertListEqual(list(histo.histograms.get_red()),expected_list)
                    if i == 1 : 
                        self.assertListEqual(list(histo.histograms.get_green()),expected_list)
                    if i == 2 : 
                        self.assertListEqual(list(histo.histograms.get_blue()),expected_list)

class TestGreyHistogram(ut.TestCase):

    def test_init(self):
        pass

    def test_get_grey(self):
        testbins = 255
        for path, a,b in expectation :
            if a :
                histo = Histogram(Image(path),bins=testbins)
                self.assertIsInstance(histo.histograms,GreyHistogram)
                expected_list = [0 for i in range(testbins)]
                expected_list[b[0]] = 30000
                self.assertListEqual(list(histo.histograms.get_grey()),expected_list)



if __name__ == '__main__':
    ut.main()