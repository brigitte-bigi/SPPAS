The accessible font, used in contrast mode, was downloaded from:
<https://github.com/Orange-OpenSource/font-accessible-dfa>
It is under the terms of the SIL Open Font License, Version 1.1.

Commissioner and Fira Code are licensed under the SIL Open Font License. 
Downloaded from:
<https://fonts.google.com/>.

SourceSerifPro: <https://fonts.adobe.com/fonts/source-serif#licensing-section>

Each family is split into unicode-range subsets, one woff2 file per script
block, by scripts/build_fonts_subsets.py. The pages refer to the subsets only:
the full files listed above are the sources of the split and are kept as such.

A subset holds the characters its font really draws. AccessibleDfA maps a
number of Greek, Cyrillic and Vietnamese codepoints to empty glyphs: they are
left out, so that the browser falls back to the sans family instead of
displaying nothing.
