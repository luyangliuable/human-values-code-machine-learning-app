import unittest
import os
import inspect
import sys
# relative imports from parent directory ######################################
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
# relative import ends ########################################################
from keyword_filter import keyword_filter as filter
# import src.keyword_filter as filter

class test_keyword_filter(unittest.TestCase):

    def setUp(self):
        self.keyword_filter = filter('./file.csv')


    @unittest.skip("too slow")
    def test_create_csv_file(self):
        self.keyword_filter.create_csv_file()


    def test_open_csv_file(self):
        testcase = self.keyword_filter.get_all_lines()
        expected = [
            "test1",
            "test2",
            "test3"
        ]
        self.assertEqual(expected, testcase)


    @unittest.skip("too slow")
    def test_write_csv_file(self):
        self.keyword_filter.append_to_csv_file([{'line': 'test_line', 'location': 'test_location', 'language': 'test_language', 'value': 'test_value'}], "poo.csv")


    @unittest.skip("too slow")
    def test_search_file(self):
        testcase = self.keyword_filter.search_file("poo.csv")
        self.assertTrue(['./poo.csv'])


    def test_get_line_word_size(self):
        testcase = self.keyword_filter.get_line_word_size("apple banana carrot")
        self.assertEqual(testcase, 3)

    def test_get_number_of_lines_in_file(self):
        testcase = self.keyword_filter.get_number_of_lines_in_file("./file.csv")
        self.assertEqual(testcase, 4)


    def test_compound_keywords_in_line(self):
        testcase = self.keyword_filter.check_words_in_line(self.keyword_filter.get_antonyms('healthy'), "Ill Will be called right after we have refreshed the ATB retention on search")
        self.assertTrue(len( testcase ) > 0)

    @unittest.skip("too slow")
    def test_get_keys_from_json(self):
        expected_result = ['choosing own goals', 'freedom', 'creativity', 'independent', 'privacy', 'choice', 'curious', 'self respect', 'excitment', 'varied', 'daring', 'pleasure', 'self indulgent', 'enjoying', 'ambitious', 'influential', 'capable', 'successful', 'intelligent', 'wealth', 'authority', 'reputation', 'recognition', 'security', 'family', 'belonging', 'social order', 'healthy', 'clean', 'obedient', 'self discipline', 'politeness', 'tradition', 'devout', 'detachment', 'humble', 'moderate', 'helpful', 'responsible', 'forgiving', 'honest', 'loyal', 'spiritual', 'friendship', 'equality', 'wisdom', 'harmony', 'beauty', 'justice', 'broad minded', 'peace', 'sustainable']
        testcase = self.keyword_filter.get_keys_from_json()
        self.assertEqual(testcase, expected_result)


    def test_get_synonym(self):
        testcase = self.keyword_filter.get_synonyms("choosing own goals")
        self.assertAlmostEqual(testcase, ["keep", "for how", "skip", "uncomment", "comment", "you may", "instead", "could be replaced", "avoid problems", "make sure", "run this", "see", "todo", "value", "wait until", "if so", "backup", "asap", "as soon as possible"])


def main():
    # Create a test suit
    suit = unittest.TestLoader().loadTestsFromTestCase(test_keyword_filter)
    # Run the test suit
    unittest.TextTestRunner(verbosity=2).run(suit)

main()
