# 4 Mar, 2020
Wrote and sent a [report](report_4Mar2020.md) about first work with inducer.
**************

# 6 Mar, 2020

I picked a "good enough" EnglishPOC [grammar](http://88.99.210.144/data/clustering_2019/POC-English-2018-12-31/POC-English-Amb_R=6-Weight=6:R-mst-weight=+1:R_cDRKd_gen-rules/dict_26C_2018-12-31_0006.4.0.dict),
obtained from the Grammar Leaner.
To avoid adjusting sentence generator now, I just converted it to the current sentence
generator format by hand (TODO: Modify sentence generator to take grammars in LG
format, instead of my made-up format).
The grammar has 3 errors in the word categories (cf. "to", "with" and "was"), 
which translate into wrong generated sentences, and probably some bad grammar rules
from the Grammar Learner.
Want to see if the grammar inducer can detect some of those bad rules (without 
changing
the grammar categories) and clean them.

After cleaning the rules, I notice that among the rejected rules, many involve
the badly formed word categories, which seems good.
After generating sentences from this cleaned grammar, they seem a bit better.


Some possible error sources:
- Check normalization: some rule sentence probability averages end up really high
(orders 100k)
- The EnglishPOC corpus itself is not the best... would prefer to try with a different
corpus. 
I want to generate sentences from the [tiniest grammar](grammars/tiniest.dict),
then run ULL pipeline to learn a grammar, then clean them. 
If sentences generated from this grammar are good, this could possible work better
and still have a whole loop: 
a) sentence generation
b) parsing
c) grammar learning
d) grammar cleaning
e) sentence generation

## Mar 7, 2020

Another possible path to try:
Starting from the [full corpus](grammars/gram1_full.corpus) generated from my 
[gram1](grammars/gram1.grammar), parse it and generate a grammar, then pass
it through the grammar inducer cleaner, and see if it improves :)

Currently: Trying full loop with gram1. Errors with sed expression in grammar
learner json file... it doesn't run because it doesn't recognize some option.

****************
## Mar 8, 2020

Problem with sed was because sed expression doesn't appropriately handle full 
paths to dictionary. 
It has to use a dictionary in the same folder.
Workaround by copying dictionary of interest to working folder.

Stream-parser produces better parses (76.83%) than sequential (69.7%), 
but still not perfect.
Seems hard to generate the correct rules here without a mechanism for new rule
generation.
However, looking at the generated sentences, there may be one or two rules which
could be rejected, so let's pass it through the grammar cleaner.

Additionally, redesigned sentence generator to handle LG-type rules, and be able
to process files like tiniest.dict, which should prove more interesting for testing.
However, I still need to handle specific connectors to match more general ones;
i.e. "Aa+" should be able to match with "A-".
Attempted expanding each specific connector into rules with more general ones,
but later realized this is faulty.
What we need is to be able to match those different specification levels when
looking for the linked category.

Update, implemented those changes and now generation can use LG-type rules.
********

After many experiments using LG dictionaries for sentence generation, it's clear
we need some extra rules to avoid infinite/very long recursion in the rules, 
since those produce sentences which are quite useful.


**************
## Mar 10, 2020

After experimenting with learned grammars from different corpora, I realize the
grammar learning algorithm doesn't work for our current POC purposes:
One grammar learning option is using ALE, which clusters words and then agglomerates
 all the rules pertaining to those words in the same category, which causes
 havoc in the sentence formation.
Alternatively, the ILE method produces grammars which, although incorrect
syntactically, are quite good at reproducing word order in the sentences, since
 they are built according to links coming from unsupervised parsing.
Because such rules reproduce word order just fine, the current implementation 
of the grammar cleaner seems ineffective in fixing a grammar containing them.

On the other hand, as shown previously, when adding random spurious rules by hand, 
the grammar cleaner seems to reject them more reliably.
In this respect, a good example for a POC is one I showed in a 
[previous report](report_4Mar2020.md):

So, I modified [gram1](grammars/gram1.grammar) into 
[badgram1](grammars/badgram1.grammar)
and ran the algorithm on it.
They are good for a first try: out of 21 rules (15 good ones vs 6 spurious ones),
the algorithm concluded that 12 of them were valid (12 good ones vs 0 bad ones).

