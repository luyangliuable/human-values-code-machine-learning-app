import unittest
import sys
sys.path.append('../')
from modifier import csv_modifier as modifier

class test_modifier(unittest.TestCase):

    def setUp(self):
        self.file_modifer = modifier()

    def test_check_file_is_same_format(self):
        filename = "a.testformat"

        test_format = self.file_modifer.check_file_is_same_format(filename, '*.testformat')

        test_format_false = self.file_modifer.check_file_is_same_format(filename, '*.randomformat')

        self.assertTrue(test_format)

        self.assertFalse(test_format_false)


def main():
    # Create a test suit
    suit = unittest.TestLoader().loadTestsFromTestCase(test_modifier)
    # Run the test suit
    unittest.TextTestRunner(verbosity=2).run(suit)

main()
