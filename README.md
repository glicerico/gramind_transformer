# gramind-transformers
## Unsupervised grammar induction with transformers

The gramind-transformer repository is part of a larger project that aims to 
construct an unsupervised grammar induction pipeline.
Currently, This repository takes a grammar and filters out rules that don't
make sense according to a language model.
The module takes a grammar with spurious rules, in 
[LinkGrammar format](https://www.link.cs.cmu.edu/link/dict/introduction.html#1),
and selects those rules that are in agreement with the grammar implicit in
the language model in use, thus explicitly obtaining a grammar that describes
 the language in question.
In order to do that, it leverages the implicit grammar knowledge contained
in the language model learned by transformers (e.g. 
[BERT](https://en.wikipedia.org/wiki/BERT_(language_model)), 
[GPT-3](https://en.wikipedia.org/wiki/GPT-3), etc.).

The high-level description of the project, and some proof-of-concept
 results have been [published here](https://arxiv.org/abs/2005.12533). 
This repository implements those ideas in a preliminary manner and is
intended for experimentation purposes, not as a finished pipeline.
 
The pipeline currently has been implemented using the 
[rangram](https://github.com/glicerico/rangram) repository to generate
sentences from grammars, and the 
[wordcat_transformer](https://github.com/glicerico/wordcat_transformer)
repository to evaluate the "quality" of a sentence, which is done using
a pre-trained BERT language model.
These tasks, however, could be performed with different methods, and
those could be plugged to this grammar inducer.
In fact, other methods are being currently explored, e.g. 
[this repository](https://github.com/glicerico/Tree-Transformer-gen) tries
to generate sentences from the grammar learned by a 
[Tree Transfomer](https://arxiv.org/abs/1909.06639).