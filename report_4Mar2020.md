# Grammatic Induction journal

## March 4th, 2020

A few days ago, I started implementing Ben's idea for a transformer-guided approach
to grammar induction.
The idea is related to that of the [wordcat_transformer](../wordcat_transformer)
project, as it's also guided by sentence probabilities obtained from transformer
network (BERT in the current case, but this could easily be extended to any other
network that could be used as a language model).

For grammar induction, the core of the idea is that we can evaluate how "good" 
(according
to the transformer) are the sentences produced by using a given rule of a grammar
(in this case, link-grammar style rules), as compared to other rules, or other
reference.

As a first approach, I've been using a variation of a very simple 
[grammar](grammars/gram1.grammar) 
used in the 
[rangram](../rangram/) experiments.
Also, in the same repository, I implemented a 
[sentence generator](../rangram/src/sentence_generator.py) that generates a
sentence from the given grammar, optionally specifying the starting rule.


For this experiments, I take each rule in the given grammar, 
generate sentences that use that rule, and get their average sentence probability.
Then, I mutate the rule and adjust the grammar accordingly, generate sentences
from this modified grammar starting with the mutated rule, and evaluate their
average score.
If the sentences from the modified grammar decrease significantly in quality (the
threshold is a
parameter), then the original rule is taken as valid.

The rationale behind this is that correct grammar rules will produce better
sentences than their "opposite".
In this experiments, the mutation is a simple swapping of each connector in
the rule, which also implies a word-order change.
E.g. if we have a rule like:
```
kids: small- & the-
```
which creates the string `the small kids`, then the mutated rule is
```
kids: small+ & the+
```
which creates the string `kids small the`.
(Notice that the rules for small and kids also have to be modified from 
`kids+` to `kids-`).

This methodology was proposed by Ben as a way to "clean" the rules generated
by the language-learning pipeline, or some other mechanism.
In that sense, a way to test it is to take a good grammar, add spurious rules to
it, and check if the algorithm is able to discriminate them.
****
## Experiment
So, I modified [gram1](grammars/gram1.grammar) into 
[badgram1](grammars/badgram1.grammar)
and ran the algorithm on it.
They are good for a first try: out of 21 rules (15 good ones vs 6 spurious ones),
the algorithm concluded that 12 of them were valid (12 good ones vs 0 bad ones).
********

## Points to consider:
- At least one of the good rules discarded by the algorithm:
```
eat: kids-
```
generates sentences that have no direct object, like:
```
the kids eat.
```
although valid, might not be very common in English (??).
The reverse of the rule, 
```
eat: kids+
```
generating sentences like
```
eat the kids.
```
is also gramatically valid, and maybe as common as the previous case (??).

Perhaps I should do a revision of the grammar.

*****
- [badgrammar1](grammars/badgram1.grammar)'s modified rules generates sentences
that are quite bad, because of the addition of spurious rules.
Sentences like:
```
the small the candy eat kids the kids eat the small candy quickly.
```
are not too rare.
This one is generated starting with a good rule.

It's not clear to me if there are some other effects participating in the
rejection of the rules. It could be that starting with a spurious rule, because
of the way I semi-randomly made them, creates longer sentences, which could be
giving lower scores.
So I think I need to normalize for sentence length better, perhaps by using
an average score for valid sentences (from a valid corpus, perhaps) to have
a reference per sentence length, as Ben has suggested before.

Proposed next steps:
- Try sentence normalization with average score of sentences of that length (in
the same corpus, or in some reference sentences).
- Explore incremental building of grammars? Or other ways to avoid very messy
sentences.
- Try this methodology on the output of a language-learning grammar for a 
simple corpus, like a curated POC English or similar.
