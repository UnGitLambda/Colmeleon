import unittest as ut
from Image import Image 
from Saver import Saver
import csv
import os

class TestImage(ut.TestCase):
    """
    Unit testing class for the module Image.
    """
    #fetch images and related infos in directory unittest/Image
    expectations = ()

    ###Normal use
    image_file = (os.listdir("./UnitTesting/Image"), Image(os.listdir("./UnitTesting/Image")))
    def test_init_image(self):
        """
        Tests structure coherence of image object after initialisation.
        """
        for args in self.image_file:
            result = Image(args[0])
            self.assertEqual(result, args[1])
            
    def test_parse(self):
        """
        Tests consistency between Image object and the given file.
        """

    def test_scale(self):
        """
        Tests if scaled image is the right size and still usable.
        """

    def test_color_constancy(self):
        """
        Tests consistency between image and its corrected version.
        """
    
    with open("../UnitTesting/Image/Saver.csv") as csvfile:
        reader = csv.reader(csvfile)
        saver_directories = [a for a in reader]
    def test_init_saver(self):
        """
        Tests that the directory was created and is now linked to the saver.
        """
        for (directory, H, _) in self.saver_directories:
            result = Saver(directory)
            self.assertEqual(hash(result), int(H))
        

    def test_save(self):
        """
        Tests that image has indeed been saved in the specified directory, in the specified format.
        """
        for directory,_,tosave in self.saver_directories:
            saver = Saver(os.path.abspath(directory))
            img = Image("../UnitTesting/Image/" + tosave)
            saver.save(img)
            self.assertIn(tosave, os.listdir())
            os.remove(directory + "/" + tosave)

    ###Assertions consistency testing
    def test_init_image_assert_type(self):
        """
        Tests robustness against invalid file types given as arguments.
        """
    def test_init_image_assert_format(self):
        """
        Tests robustness against invalid, not image, formats given as arguments.
        """
    def test_init_image_assert_existence(self):
        """
        Tests robustness against non-existing files given as arguments.
        """

    def test_parse_assert_type(self):
        """
        Tests robustness against invalid types given to the parser.
        """
    def test_parse_assert_format(self):
        """
        Tests robustness against invalid formats given to the parser.
        """
    def test_parse_assert_existence(self):
        """
        Tests robustness against non-existing files given to the parser.
        """

    def test_scale_assert_type(self):
        """
        Tests robustness against invalid types given to the scaling method.
        """
    def test_color_constancy_assert_type(self):
        """
        Tests robustness against invalid types given to the color_constancy method.
        """

    def test_init_saver_assert_type(self):
        """
        Tests robustness against invalid types given to the saver.
        """
        
    def test_init_saver_assert_isdir(self):
        """
        Tests robustness against already existing files, not being directories, being given as arguments to the saver.
        """

    def test_save_assert_type(self):
        """
        Tests robustness of the saving method against invalid types.
        """
        
if __name__ == '__main__':
    ut.main()
        
        
        
        
        
        