After our last week discussion, I remembered that the [Turtle POC corpus](http://88.99.210.144/data/poc-turtle/poc-turtle.txt) 
is not 
grammatical, so it would need to be changed to
make sense for BERT: it has sentences like `parrot isa bird`, `fin has scale`.

Instead, I decided to use one of the [best grammars](http://88.99.210.144/data/clustering_2019/POC-English-2018-12-31/POC-English-Amb_R=6-Weight=6:R-mst-weight=+1:R_cDRKd_gen-rules/dict_26C_2018-12-31_0006.4.0.dict)
 obtained by the 
the ULL pipeline to the [EnglishPOC corpus](http://88.99.210.144/data/poc-english/poc_english.txt).
The grammar has 3 errors in the word categories (cf. "to", "with" and "was"), 
which translate into wrong generated sentences, hence some bad grammar 
rules by the Grammar Learner.
We get sentences like:
```
hammer are a tool.
dad wants mom his daughter be on the board.
son sees mom has son sawed the wood has a hammer.
daughter writes his dad with chalk on the board of directors.
son sawed the wood has.
dad was not daughter is a child before.
dad food not mom is a child now.
son wants his dad mom wants her be on the board of directors.
a mom liked sausage before.
daughter writes to dad with chalk on the board.
daughter wants daughter to son be on the board of directors.
```

I ran the grammar through the grammar cleaner
to see if it can detect some of those bad rules (without changing
the grammar categories) and clean them.
After cleaning the rules, I notice that among the rejected rules, many involve
the badly formed word categories, which should improve sentence quality.
After generating sentences from this cleaned grammar, they seem a bit better, but
still not great.
```
son wants his be on the board.
dad wants her dad wants to be on the board.
dad with a hammer is a tool.
a dad likes sausage before.
daughter food not a human before.
daughter writes with chalk on the board of directors.
dad food not son is a parent now.
dad wants her daughter wants to be on the board.
son knocked the wood with a binoculars.
son knocked the wood has.
son was not son is a human before.
```
As it has been noted in the past, the EnglishPOC corpus does not seem like
the most natural set of sentences.
 
************
After this experiment I decided to generate sentences from the 
[tiniest grammar](grammars/tiniest.dict),
then run ULL pipeline to learn a grammar, then clean them. 
If sentences generated from this grammar are good, this could possible work better
and complete a whole loop:
- sentence generation from a hand-coded grammar (alternatively use a corpus)
- parsing
- grammar learning
- sentence generation from learned grammar
- grammar cleaning
- sentence generation from cleaned grammar

For this, I modified the [sentence generator](https://github.com/glicerico/rangram)
design to handle dictionaries that are closer to LG-type rules, to avoid editing
dictionaries by hand for tests (ULL learned grammars also come in this format).

Using a reduced version of the [tiny dictionary](https://raw.githubusercontent.com/opencog/link-grammar/master/data/en/tiny.dict),
 namely [tiniest](grammars/tiniest.dict), 
 I tried to generate a test corpora from it.
The algorithm very often falls in infinite/very long recursion, given the many
possibilities for loops in the dictionary rules.
Some mechanisms to select shorter rules, like we discussed before,
 are clearly needed.

However, even when the sentence generator is able to produce sentences, they not
always seem very good for our purposes.
We get, for example:
```
is this fast park this must ultimately come generally was a street goes initially us.
```
which, although it is grammatical according to tiniest.dict, I am not sure if
they are useful for our purposes.
I wonder if generating sentences from grammars this way is a reasonable thing to try.

When the generated sentence is shorter, it can be more easily understood:
```
ugly was a white nose already.
1 ugly 2 was
1 ugly 6 already
2 was 5 nose
3 a 5 nose
4 white 5 nose
```
or

```
angry is the big student sadly.
1 angry 6 sadly
1 angry 2 is
2 is 5 student
3 the 5 student
4 big 5 student
```
so more reason to guide the generator towards shorter sentences.

It is possible that my arbitrary reduction of the tiny to tiniest grammar is
partly responsible for the type of sentences obtained, but it's worth noting
that these were indeed also possible in the original tiny grammar.

*******************
Given the situation, I decided to try running the full loop mentioned above,
but starting from the
very simple [gram1.grammar](grammars/gram1.grammar).

I generated the [full corpus](grammars/gram1_full.corpus) (all possible grammatical
sentences) from the grammar.
Then, the stream-parser produces better parses (76.83%) than sequential (69.7%)
and the ULL parser (63.68%), but still not perfect.
So, using the stream-parser parses, two learned grammars (from two different methods)
were obtained, both achieving F1 scores of 76.83%, so learning perfectly from
the faulty parses.
The so-called "Identical Lexical Entries" grammar is quite trivial:
```
% B
"candy" "kids" "quickly" "small" "the":
(BB+) or (BB-) or (BB- & BB- & BC+) or (BB- & BC+) or (BC+) or (CB-) or (CB- & BB+);

% C
"eat":
(BC-) or (BC- & CB+) or (BC- & CB+ & CB+);
```
On the other hand, the "Agglomerative Lexical Entries" grammar is closer
to the original one:
```
% B
"candy":
(CB-) or (CB- & BE+);

% C
"eat":
(DC-) or (DC- & CB+) or (DC- & CE+) or (DC- & CG+ & CB+);

% D
"kids":
(DC+) or (FD- & GD- & DC+) or (GD- & DC+);

% E
"quickly":
(BE-) or (CE-);

% F
"small":
(FD+) or (GF-);

% G
"the":
(CG-) or (CG- & GF+) or (GD+);
```
It's worth noting that many rules are wrong, but they appear there because
the unsupervised parses were not perfect, and the wrong links there made
their way to the grammar.

Generating the full corpus from this grammar, we get 6 more sentences than
with the original grammar.
Those are sentences involving wrong rules, like:
```
the small kids eat the candy quickly small.
1 the 3 kids
2 small 3 kids
3 kids 4 eat
4 eat 5 the
4 eat 6 candy
5 the 8 small
6 candy 7 quickly
```

So, there is room for these learned grammars to be cleaned of faulty rules.
I implemented sentence probability normalization through sentence length, but
there is some bug that I didn't get to explore which is giving probabilities that
are way off; will investigate shortly.
For the sake of this report, I applied the previous sentence probability that
normalizes using a geometric mean.
Using that, the grammar cleaner discarded two rules from this grammar:
One that is not gramatically incorrect, which allowed to produce sentences like
"kids eat".
The other one is the possibility of a link between "the" and "small".
So, the rejection is not bad, but it did miss some of the other rules which are
not grammatical.

On the other hand, it is impossible to fix the grammar by only "cleaning" 
rules, as the algorithm currently cannot create the correct needed rules
without a mechanism for 
 new rule generation and testing.

