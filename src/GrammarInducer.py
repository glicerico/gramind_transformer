import argparse
import copy
import sys
import random

REPOS = "/home/andres/repositories/"
sys.path.insert(0, REPOS)
from src.sentence_generator import GrammarSampler, Grammar


class GrammarInducer:
    """
    Induces a grammar by leveraging transformers
    """

    def __init__(self, grammar_file):
        self.orig_grammar = Grammar(grammar_file)
        self.orig_sampler = GrammarSampler(self.orig_grammar)
        self.mod_grammar = Grammar(grammar_file)  # Local grammar for testing new rules
        self.mod_sampler = None

    def init_mod_sampler(self):
        """
        Generate instance of GrammarSampler using the modified grammar
        """
        self.mod_sampler = GrammarSampler(self.mod_grammar)

    def reset_grammar(self):
        """
        Reset grammar to the one from GrammarSampler instance
        """
        self.mod_sampler = GrammarSampler(self.orig_grammar)

    def choose_random_rule(self, chosen_class=None):
        if chosen_class is None:
            chosen_class = random.randint(0, len(self.sampler.disj_dict) - 1)
        chosen_rule = random.randint(0, len(self.sampler.disj_dict[chosen_class]) - 1)
        _, rule = self.choose_specific_rule(chosen_class, chosen_rule)
        print(f"Random rule: Class {chosen_class}, Rule {chosen_rule}: {rule}")
        return chosen_class, rule

    def choose_specific_rule(self, this_class, this_rule):
        return this_class, self.orig_sampler.disj_dict[this_class][this_rule]

    @staticmethod
    def generate_sentences(sampler, num_sents=10, node=None, rule=None, verbose=False):
        sents = [sampler.generate_parse(starting_node=node, starting_rule=rule)[0] for _ in range(num_sents)]
        sents = list(set(sents))
        if verbose:
            print(f"Generated {len(sents)} unique sentences.")
        return sents

    @staticmethod
    def swap_rule(original_rule):
        """
        Modifies given grammar rule by swapping side and word order for all connectors.
        :param original_rule:
        :return:
        """
        new_rule = [(y, x) for x, y in original_rule]  # Inverts all connectors in rule (and their word order)
        return new_rule

    def swap_grammar(self, root_category, old_rule, verbose=False):
        connectors = {}
        new_rule = self.swap_rule(old_rule)
        # Replace old rule in current category
        new_disjunct = tuple([new_rule if old_rule == x else x for x in self.orig_sampler.disj_dict[root_category]])
        self.mod_grammar.disj_dict[root_category] = new_disjunct

        # Check which of the involved connectors are included in other rules in root_category
        for conn in old_rule:  # Assumes all connectors in new rule were changed
            checks = [True if conn in rule else False for rule in self.mod_grammar.disj_dict[root_category]]
            connectors[conn] = any(checks)

        # For each connector in old rule, change its linked category rules. Assuming all connectors were swapped
        for conn, duplicate in connectors.items():
            linked_class = list(conn)
            linked_class.remove(root_category)
            linked_disj = []
            for rule in self.orig_sampler.disj_dict[linked_class[0]]:
                this_rule = rule[:]  # Copy values
                if conn in this_rule:
                    if duplicate:  # If connector of interest is still in root_category, keep rules connecting to them
                        linked_disj.append(this_rule[:])
                    conn_pos = this_rule.index(conn)
                    swapped_connector = self.swap_rule([conn])
                    this_rule.pop(conn_pos)
                    this_rule.insert(conn_pos, swapped_connector[0])
                    linked_disj.append(this_rule[:])
                else:
                    linked_disj.append(this_rule)
            self.mod_grammar.disj_dict[linked_class[0]] = tuple(linked_disj)  # Substitutes original rule
        if verbose:
            print(f"Original grammar {self.orig_sampler.disj_dict}")
            print(f"Modified grammar {self.mod_grammar.disj_dict}")

        return new_rule


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grammar Induction using transformers')
    parser.add_argument('--grammar', type=str, required=True, help='Grammar file to use')
    parser.add_argument('--verbose', action='store_true', help='Print processing info?')

    args = parser.parse_args()

    inducer = GrammarInducer(args.grammar)

    # rand_class, rand_rule = inducer.choose_random_rule()
    rand_class, rand_rule = inducer.choose_specific_rule(1, 1)  # For testing purposes
    inducer.generate_sentences(inducer.orig_sampler, node=rand_class, rule=rand_rule, num_sents=2, verbose=args.verbose)

    swapped_rule = inducer.swap_grammar(rand_class, rand_rule, verbose=args.verbose)
    inducer.init_mod_sampler()
    inducer.generate_sentences(inducer.mod_sampler, node=rand_class, rule=swapped_rule, num_sents=2, verbose=args.verbose)

    test_swap_grammar()
