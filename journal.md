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
After generating sentences from this cleaned grammar, they seem better.


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

Another possible path to try:
Starting from the [full corpus](grammars/gram1_full.corpus) generated from my 
[gram1](grammars/gram1.grammar), parse it and generate a grammar, then pass
it through the grammar inducer cleaner, and see if it improves :)

