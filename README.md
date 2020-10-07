# gramind-transformers
## Unsupervised grammar induction with transformers

The gramind-transformer project aims to construct an unsupervised grammar
induction 
pipeline that consumes text in one language, and is able to produce a 
grammar that describes that language. 
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