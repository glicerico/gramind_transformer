import argparse
import sys
import random
import numpy as np

REPOS = "/home/andres/repositories/"
sys.path.insert(0, REPOS)
from rangram.src.sentence_generator import GrammarSampler, Grammar
from wordcat_transformer.src.BertModel import BertLM


class GrammarInducer:
    """
    Induces a grammar by leveraging transformers
    """

    def __init__(self, grammar_file, pretrained_model='bert-base-uncased', device_number='cuda:2', use_cuda=False):
        self.grammar_file = grammar_file
        self.orig_grammar = Grammar(self.grammar_file)
        self.orig_sampler = GrammarSampler(self.orig_grammar)
        self.mod_grammar = Grammar(self.grammar_file)  # Local grammar for testing new rules
        self.mod_sampler = None
        self.valid_rules = {}

        self.lm = BertLM(pretrained_model=pretrained_model, device_number=device_number, use_cuda=use_cuda)

    def init_mod_sampler(self):
        """
        Generate instance of GrammarSampler using the modified grammar
        """
        self.mod_sampler = GrammarSampler(self.mod_grammar)

    def reset_grammar(self):
        """
        Reset grammar to the one from GrammarSampler instance
        """
        self.mod_grammar = Grammar(self.grammar_file)
        self.mod_sampler = GrammarSampler(self.mod_grammar)

    def choose_random_rule(self, chosen_class=None):
        if chosen_class is None:
            chosen_class = random.randint(0, len(self.orig_sampler.disj_dict) - 1)
        chosen_rule = random.randint(0, len(self.orig_sampler.disj_dict[chosen_class]) - 1)
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

    def evaluate_sentences(self, sents, verbose=False):
        """
        Evaluate sentence probabilities for given samples, return average score
        :param sents:       Sentences to evaluate
        :param verbose:
        :return:
        """
        mean_score = 0
        for sent in sents:
            tokens = self.lm.tokenize_sent(sent)
            mean_score += self.lm.get_sentence_prob_normalized(tokens, verbose=verbose)
        return mean_score / len(sents)

    def evaluate_rule(self, this_class, this_rule, num_sents=5, threshold=0.8, verbose=False, lf=None):
        self.reset_grammar()
        # Generate and evaluate sentences with rule
        orig_sents = inducer.generate_sentences(inducer.orig_sampler, node=this_class, rule=this_rule,
                                                num_sents=num_sents, verbose=args.verbose)
        orig_score = inducer.evaluate_sentences(orig_sents)

        # Generate and evaluate sentences with modified rule
        swapped_rule = inducer.swap_grammar(this_class, this_rule, verbose=args.verbose)
        inducer.init_mod_sampler()
        mod_sents = inducer.generate_sentences(inducer.mod_sampler, node=this_class, rule=swapped_rule,
                                               num_sents=num_sents, verbose=args.verbose)
        mod_score = inducer.evaluate_sentences(mod_sents)

        if verbose:
            print(f"Original sentences: {orig_sents}")
            print(f"Modified sentences: {mod_sents}")

        print(f"Original score: {orig_score}")
        print(f"Modified score: {mod_score}")

        # Accept rule if modified rule lowers sentences score below threshold
        if mod_score / orig_score < threshold:
            print(f"Rule is accepted!: {this_rule}")
            lf.write("Rule is accepted!: ")
            np.savetxt(lf, this_rule, fmt="(%s, %s)", newline=", ")
            self.valid_rules[this_class].append(this_rule)
        else:
            print(f"Rule is rejected!: {this_rule}")
            lf.write("Rule is rejected!: ")
            np.savetxt(lf, this_rule, fmt="(%s, %s)", newline=", ")

        return orig_score, mod_score


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grammar Induction using transformers')
    parser.add_argument('--grammar', type=str, required=True, help='Grammar file to use')
    parser.add_argument('--verbose', action='store_true', help='Print processing info?')
    parser.add_argument('--sents', default=5, type=int, help='Num of sentences to generate per rule')
    parser.add_argument('--thres', default=0.8, type=float, help='Min ratio of quality drop to accept a rule')
    parser.add_argument('--norm_file', type=str, help='Sentences file to use for normalization')
    parser.add_argument('--norm_pickle', type=str, help='Pickle file to use for normalization')

    args = parser.parse_args()

    inducer = GrammarInducer(args.grammar)

    # Calculate normalization scores if option is present
    if args.norm_file:
        inducer.lm.calculate_norm_dict(args.norm_file)
        print("Normalization scores:")
        print(inducer.lm.norm_dict)

    # rand_class, rand_rule = inducer.choose_random_rule()
    # rand_class, rand_rule = inducer.choose_specific_rule(1, 1)  # For testing purposes
    # orig_sents = inducer.generate_sentences(inducer.orig_sampler, node=rand_class, rule=rand_rule, num_sents=args.sents,
    #                                         verbose=args.verbose)
    # orig_score = inducer.evaluate_sentences(orig_sents)
    logfile = open("logfile.log", 'w')
    scores = {}  # Store scores for each rule
    for curr_class, class_rules in inducer.orig_sampler.disj_dict.items():
        logfile.write("Class: " + str(curr_class) + "\n")
        inducer.valid_rules[curr_class] = []  # Build valid rules dictionary
        scores[curr_class] = []
        for curr_rule in class_rules:
            orig_score, mod_score = inducer.evaluate_rule(curr_class, curr_rule, num_sents=args.sents, threshold=args.thres, verbose=args.verbose, lf=logfile)
            scores[curr_class].append((orig_score, mod_score, mod_score / orig_score))

    logfile.close()
    print(f"Accepted rules:")
    print(inducer.valid_rules)
    print(f"Scores: {scores}")
