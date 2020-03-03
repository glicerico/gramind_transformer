import unittest
import sys

REPOS = "/home/andres/repositories/"
sys.path.insert(0, REPOS)
from gramind_transformer.src.GrammarInducer import GrammarInducer


class MyTestCase(unittest.TestCase):
    def test_swap_grammar(self):
        """
        Tests if the method swapping the grammar works properly, for one example.
        """
        test_inducer = GrammarInducer('../grammars/gram1.grammar')

        test_class, test_rule = test_inducer.choose_specific_rule(1, 1)
        test_inducer.swap_grammar(test_class, test_rule, verbose=False)

        expected_disj_dict = {
            0: ([(0, 1)], [(1, 0)], [(5, 0), (0, 1)], [(5, 0), (1, 0)], [(3, 0), (5, 0), (0, 1)], [(3, 0), (5, 0),
                                                                                                   (1, 0)]),
            1: ([(0, 1)], [(1, 0), (2, 1)], [(0, 1), (1, 4)], [(0, 1), (1, 2), (1, 4)]),
            2: ([(1, 2)], [(2, 1)], [(5, 2), (1, 2)], [(5, 2), (2, 1)], [(3, 2), (5, 2), (1, 2)], [(3, 2), (5, 2),
                                                                                                   (2, 1)]),
            3: ([(3, 2)], [(3, 0)]),
            4: ([(1, 4)],),
            5: ([(5, 0)], [(5, 2)])}
        self.assertEqual(test_inducer.mod_grammar.disj_dict, expected_disj_dict)
        print("Swapped grammar test passed!")


if __name__ == '__main__':
    unittest.main()
