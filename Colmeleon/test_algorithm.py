import unittest as ut
from Algorithm import *
from Histogram import *


expectations = ()
data1 = [0,1,2,3,4,5]
data1b = set([0,1,2,3,4,5])
data1c = np.array([0,1,2,3,4,5])
data1d = [0,1,2,3,4,5,6,7,8,9,10]
data2 = [0,1,2,3,4,6]
data3 = [10,20,30,40,50,60]
baddata1 = "Lorem ipsum"
baddata2 = "HistogramsAndColor"

class TestAlgorithm(ut.TestCase):
    """
    Unit testing class for the module Image.
    """


    def test_jaccard_dist(self):
        """
        #Test the jaccard distance function
        """
        self.assertIsInstance(jaccard_dist(data1,data1), float)
        self.assertIsInstance(jaccard_dist(data1b,data1c), float)
        self.assertEqual(jaccard_dist(data1,data1), 0)
        self.assertEqual(jaccard_dist(data1,data2), 0.2857)
        self.assertEqual(jaccard_dist(data1,data3), 1)
        with self.assertRaises(TypeError):
            jaccard_dist(baddata1,baddata1)

    def test_euclidean_dist(self):
        """
        Test the euclidean distance function
        """
        self.assertIsInstance(euclidean_dist(data1,data1), float)
        self.assertIsInstance(euclidean_dist(data1b,data1c), float)
        self.assertEqual(euclidean_dist(data1,data1), 0)
        self.assertEqual(euclidean_dist(data1,data2), 1 )
        self.assertEqual(euclidean_dist(data1,data3), 88.0625 )
        with self.assertRaises(TypeError):
            jaccard_dist(baddata1,baddata1)

if __name__ == '__main__':
    ut.main()
        
        
        
        
        
        