import argparse
import sys
import random

REPOS = "/home/andres/repositories/"
sys.path.insert(0, REPOS)
from src.sentence_generator import GrammarSampler


class GrammarInducer:
    """
    Induces a grammar by leveraging transformers
    """
    def __init__(self, grammar_file):

        self.sampler = GrammarSampler(grammar_file)

    def choose_random_rule(self, chosen_class=None):
        if chosen_class is None:
            chosen_class = random.randint(0, len(self.sampler.disj_dict) - 1)
        chosen_rule = random.randint(0, len(self.sampler.disj_dict[chosen_class]) - 1)
        rule = self.choose_specific_rule(chosen_class, chosen_rule)
        print(f"Random rule: Class {chosen_class}, Rule {chosen_rule}: {rule}")
        return chosen_class, rule

    def choose_specific_rule(self, this_class, this_rule):
        return self.sampler.disj_dict[this_class][this_rule]

    def generate_sentences(self, num_sents=10, node=None, rule=None):
        sents = [self.sampler.generate_parse(starting_node=node, starting_rule=rule)[0] for i in range(num_sents)]
        sents = list(set(sents))
        print(f"Generated {len(sents)} unique sentences.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grammar Induction using transformers')
    parser.add_argument('--grammar', type=str, required=True, help='Grammar file to use')

    args = parser.parse_args()

    inducer = GrammarInducer(args.grammar)

    print(inducer.sampler.disj_dict)
    rand_class, rand_rule = inducer.choose_random_rule()

    inducer.generate_sentences(node=rand_class, rule=rand_rule, num_sents=5)


