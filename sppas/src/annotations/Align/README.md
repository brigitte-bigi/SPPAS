
Alignment is the process of aligning speech with its corresponding
transcription at the phone level.
This phonetic segmentation problem consists in a time-matching between a
given speech unit along with a phonetic representation of the unit.
The goal is to generate an alignment between the speech signal and its
phonetic representation.

By default, alignment is based on the Julius Speech Recognition Engine (SRE)
for 3 reasons:

1. it is  easy to install which is important for users;
2. it is also easy to use then was easy to integrate in SPPAS;
3. its performances correspond to the state-of-the-art of HMM-based
systems and are quite good.

The HTK command "HVite" can also be used to perform Alignment.

A finite state grammar that describes sentence patterns to be recognized and
an acoustic model are needed. A grammar essentially defines constraints on
what the SRE can expect as input. It is a list of words that the SRE listens
to. Each word has a set of associated list of phonemes, extracted from the
dictionary. When given a speech input, Julius searches for the most likely
word sequence under constraint of the given grammar.

Speech Alignment also requires an Acoustic Model in order to align
speech. An acoustic model is a file that contains statistical
representations of each of the distinct sounds of one language.
Each phoneme is represented by one of these statistical representations.
SPPAS is based on the use of HTK-ASCII acoustic models.
