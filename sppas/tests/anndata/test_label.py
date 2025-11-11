# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.tests.test_label.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test sppasLabel(), sppasLabel(), sppasTag(), sppasTagCompare().

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import unittest

from sppas.core.config import symbols
from sppas.core.coreutils import u
from sppas.core.coreutils import b
from sppas.core.coreutils import text_type
from sppas.src.anndata.ann.annlabel import sppasTag
from sppas.src.anndata.ann.annlabel import sppasFuzzyPoint
from sppas.src.anndata.ann.annlabel import sppasFuzzyRect
from sppas.src.anndata.ann.annlabel import sppasLabel
from sppas.src.anndata.ann.annlabel import sppasTagCompare
from sppas.src.anndata.anndataexc import AnnDataTypeError
from sppas.src.anndata.anndataexc import AnnDataNegValueError

# ---------------------------------------------------------------------------

SIL_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
NOISE_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("noise")]
SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]
PAUSE_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("pause")]
NOISE_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("noise")]

# ---------------------------------------------------------------------------


class TestFuzzyPoint(unittest.TestCase):

    def test_init(self):
        # Create a point from tuples of int
        p = sppasFuzzyPoint((1, 2))
        self.assertEqual(p.get_midpoint(), (1, 2))
        self.assertIsNone(p.get_radius())
        # Create a point from tuples of int with a radius value
        p = sppasFuzzyPoint((1, 2), 0)
        self.assertEqual(p.get_midpoint(), (1, 2))
        self.assertEqual(p.get_radius(), 0)
        # Create a point from tuples of float with a radius value
        p = sppasFuzzyPoint((1.1, 2.2), 0.1)
        self.assertEqual(p.get_midpoint(), (1, 2))
        self.assertEqual(p.get_radius(), 0)
        # Create a point from tuples in a string
        p = sppasFuzzyPoint("(1,2)")
        self.assertEqual(p.get_midpoint(), (1, 2))
        self.assertIsNone(p.get_radius())
        # non-conform
        with self.assertRaises(AnnDataTypeError):
            sppasFuzzyPoint(("a", "b"))
        # it was non-conform but it is regular from sppas 4.6:
        # with self.assertRaises(AnnDataNegValueError):
        #    sppasFuzzyPoint((1, -1))

    def test_set_midpoint(self):
        # from a tuple
        p = sppasFuzzyPoint((1, 2))
        p.set_midpoint((3, 4))
        self.assertEqual(p.get_midpoint(), (3, 4))
        # from a string representing the tuple
        p = sppasFuzzyPoint("(1,2)")
        p.set_midpoint("(3,4)")
        self.assertEqual(p.get_midpoint(), (3, 4))

    def test_set_radius(self):
        p = sppasFuzzyPoint((1, 2))
        p.set_radius(3)
        self.assertEqual(p.get_radius(), 3)
        p.set_radius("1")
        self.assertEqual(p.get_radius(), 1)

    def test_contains(self):
        p = sppasFuzzyPoint((1, 2))
        p.set_radius(3)
        self.assertTrue(p.contains((1, 1)))
        self.assertTrue(p.contains((0, 0)))
        self.assertTrue(p.contains((4, 5)))
        self.assertFalse(p.contains((6, 5)))

    def test_overloads(self):
        # str
        p1 = sppasFuzzyPoint((1, 2))
        self.assertEqual(str(p1), "(1,2)")
        p2 = sppasFuzzyPoint((1, 2), 0)
        self.assertEqual(str(p2), "(1,2,0)")
        # eq
        self.assertTrue(p1 == p2)
        self.assertFalse(p1 == (3, 2))
        self.assertTrue(p1 == (1, 2))
        # neq
        self.assertFalse(p1 != p2)
        self.assertFalse(p1 != (1, 2))
        self.assertTrue(p1 != (3, 2))
        # with radius
        p1 = sppasFuzzyPoint((1, 2), 3)
        self.assertTrue(p1 == (1, 2))
        self.assertTrue(p1 == (3, 4))
        self.assertTrue(p1 == (4, 5))
        self.assertFalse(p1 == (5, 5))
        self.assertTrue(p1 == (5, 5, 1))
        self.assertFalse(p1 == (6, 6, 1))

# ---------------------------------------------------------------------------


class TestFuzzyRect(unittest.TestCase):

    def test_init(self):
        # Create from a tuple of int
        p = sppasFuzzyRect((1, 2, 4, 10))
        self.assertEqual(p.get_midpoint(), (1, 2, 4, 10))
        self.assertIsNone(p.get_radius())
        p = sppasFuzzyRect((1, 2, 4, 10), 0)
        self.assertEqual(p.get_midpoint(), (1, 2, 4, 10))
        self.assertEqual(p.get_radius(), 0)

        # Create from a string
        p = sppasFuzzyRect("(1,2,10,12)")
        self.assertEqual(p.get_midpoint(), (1, 2, 10, 12))
        self.assertIsNone(p.get_radius())

        p = sppasFuzzyRect("(1, 2, 10, 12)")
        self.assertEqual(p.get_midpoint(), (1, 2, 10, 12))
        self.assertIsNone(p.get_radius())

        # Non-conform init
        with self.assertRaises(AnnDataTypeError):
            sppasFuzzyRect(("a", "b", "10", "24"))
        with self.assertRaises(AnnDataNegValueError):
            sppasFuzzyRect((1, -1, 0, 0))

        p = sppasFuzzyRect((1., 2., 4.2, 10.1), 0)
        self.assertEqual(p.get_midpoint(), (1, 2, 4, 10))
        self.assertEqual(p.get_radius(), 0)

    def test_set_midpoint(self):
        # from a tuple
        p = sppasFuzzyRect((1, 2, 10, 10))
        p.set_midpoint((3, 4, 12, 12))
        self.assertEqual(p.get_midpoint(), (3, 4, 12, 12))
        # from a string representing the tuple
        p = sppasFuzzyRect("(1, 2, 10, 10)")
        p.set_midpoint("(3, 4, 12, 12)")
        self.assertEqual(p.get_midpoint(), (3, 4, 12, 12))

    def test_set_radius(self):
        p = sppasFuzzyRect((1, 2, 10, 12))
        p.set_radius(3)
        self.assertEqual(p.get_radius(), 3)
        p.set_radius("1")
        self.assertEqual(p.get_radius(), 1)

    def test_contains(self):
        p = sppasFuzzyRect((1, 2, 10, 10))
        p.set_radius(3)
        self.assertTrue(p.contains((1, 1)))
        self.assertTrue(p.contains((0, 0)))
        self.assertTrue(p.contains((14, 12)))
        self.assertFalse(p.contains((16, 5)))
        self.assertTrue(p.contains((10, 15)))
        self.assertFalse(p.contains((10, 16)))

# ---------------------------------------------------------------------------


class TestTag(unittest.TestCase):
    """Represents a typed content of a label.

    A sppasTag() content can be one of the following types:

        1. string/unicode - (str)
        2. integer - (int)
        3. float - (float)
        4. boolean - (bool)
        5. point - (sppasFuzzyPoint)
        6. rect - (sppasFuzzyRect)

    """

    def test_unicode(self):
        text = sppasTag("\têtre   \r   être être  \n  ")
        self.assertIsInstance(str(text), str)

    # -----------------------------------------------------------------------

    def test_string_content(self):
        """Test the tag if the content is a unicode/string."""

        text = sppasTag(" test ")
        self.assertEqual(text.get_content(), u("test"))

        text = sppasTag(2)
        self.assertEqual(text.get_typed_content(), "2")
        self.assertEqual(text.get_type(), "str")

        text = sppasTag(2.1)
        self.assertEqual(text.get_typed_content(), "2.1")
        self.assertEqual(text.get_type(), "str")

    # -----------------------------------------------------------------------

    def test_int_content(self):
        """Test the tag if the content is an integer."""

        # int value
        text = sppasTag(2, tag_type="int")
        self.assertEqual(text.get_typed_content(), 2)  # typed content is "int"
        self.assertEqual(text.get_content(), u("2"))   # but content is always a string
        self.assertEqual(text.get_type(), "int")

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="int")

        text_str = sppasTag("2")
        self.assertEqual(text.get_content(), text_str.get_content())
        self.assertNotEqual(text.get_typed_content(), text_str.get_typed_content())

        # with no type specified, the default is "str"
        text = sppasTag(2)
        self.assertEqual(text.get_content(), u("2"))
        self.assertEqual(text.get_typed_content(), u("2"))
        self.assertEqual(text.get_type(), "str")

    # -----------------------------------------------------------------------

    def test_float_content(self):
        """Test the tag if the content is a floating point."""

        text = sppasTag(2.10, tag_type="float")
        textstr = sppasTag("2.1")
        self.assertEqual(text.get_typed_content(), 2.1)
        self.assertEqual(text.get_content(), u("2.1"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="float")

    # -----------------------------------------------------------------------

    def test_bool_content(self):
        """Test the tag if the content is a boolean."""

        text = sppasTag("1", tag_type="bool")
        textstr = sppasTag("True")
        self.assertEqual(text.get_typed_content(), True)
        self.assertEqual(text.get_content(), u("True"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

    # -----------------------------------------------------------------------

    def test_point_content(self):
        """Test the tag if the content is a sppasFuzzyPoint."""

        p = sppasFuzzyPoint((1, 2))
        tag = sppasTag(p, tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p.get_midpoint(), p2.get_midpoint())
        self.assertEqual(p.get_radius(), p2.get_radius())

        p = sppasFuzzyPoint((1, 2), 1)
        tag = sppasTag(p, tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p.get_midpoint(), p2.get_midpoint())
        self.assertEqual(p.get_radius(), p2.get_radius())

        tag = sppasTag((1, 2), tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2))
        self.assertIsNone(p2.get_radius())

        tag = sppasTag((30, 20, 2), tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (30, 20))
        self.assertEqual(p2.get_radius(), 2)

        tag = sppasTag("(1,2)", tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2))
        self.assertIsNone(p2.get_radius())

        tag = sppasTag("(1,2,0)", tag_type="point")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2))
        self.assertEqual(p2.get_radius(), 0)

    # -----------------------------------------------------------------------

    def test_rect_content(self):
        """Test the tag if the content is a sppasFuzzyRect."""

        p = sppasFuzzyRect((1, 2, 10, 10))
        tag = sppasTag(p, tag_type="rect")
        p2 = tag.get_typed_content()
        self.assertEqual(p.get_midpoint(), p2.get_midpoint())
        self.assertEqual(p.get_radius(), p2.get_radius())

        p = sppasFuzzyRect((1, 2, 10, 10), 1)
        tag = sppasTag(p, tag_type="rect")
        p2 = tag.get_typed_content()
        self.assertEqual(p.get_midpoint(), p2.get_midpoint())
        self.assertEqual(p.get_radius(), p2.get_radius())

        tag = sppasTag((1, 2, 10, 10), tag_type="rect")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2, 10, 10))
        self.assertIsNone(p2.get_radius())

        tag = sppasTag("(1,2,10,10)", tag_type="rect")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2, 10, 10))
        self.assertIsNone(p2.get_radius())

        tag = sppasTag("(1,2,10,10,1)", tag_type="rect")
        p2 = tag.get_typed_content()
        self.assertEqual(p2.get_midpoint(), (1, 2, 10, 10))
        self.assertEqual(p2.get_radius(), 1)

    # -----------------------------------------------------------------------

    def test_set(self):
        text = sppasTag("test")
        text.set_content("toto")
        text.set_content((1, 2, 1))
        self.assertEqual(text.get_type(), "str")
        text.set_content((1, 2, 1), tag_type="point")
        self.assertEqual(text.get_type(), "point")

    # -----------------------------------------------------------------------

    def test__eq__(self):
        text1 = sppasTag(" test    ")
        text2 = sppasTag("test\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

        text1 = sppasTag("")
        text2 = sppasTag("\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """Events are labels with a specific text.

    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_is_silence(self):
        label = sppasLabel(sppasTag(SIL_PHON))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertTrue(text.is_silence())

    def test_IsPause(self):
        label = sppasLabel(sppasTag(PAUSE_ORTHO))
        self.assertTrue(label.get_best().is_pause())

    def test_IsNoise(self):
        label = sppasLabel(sppasTag(NOISE_ORTHO))
        self.assertTrue(label.get_best().is_noise())
        label = sppasLabel(sppasTag(NOISE_PHON))
        self.assertTrue(label.get_best().is_noise())

    def test_IsSpeech(self):
        label = sppasLabel(sppasTag("l"))
        self.assertTrue(label.get_best().is_speech())
        label = sppasLabel(sppasTag(NOISE_PHON))
        self.assertFalse(label.get_best().is_speech())

# ---------------------------------------------------------------------------


class TestTagCompare(unittest.TestCase):
    """Test methods to compare tags."""

    def setUp(self):
        self.tc = sppasTagCompare()

    # -----------------------------------------------------------------------

    def test_members(self):
        """Test methods getter."""

        self.assertEqual(self.tc.methods['exact'], self.tc.exact)
        self.assertEqual(self.tc.get('exact'), self.tc.exact)

        self.assertEqual(self.tc.methods['iexact'], self.tc.iexact)
        self.assertEqual(self.tc.get('iexact'), self.tc.iexact)

        self.assertEqual(self.tc.methods['startswith'], self.tc.startswith)
        self.assertEqual(self.tc.get('startswith'), self.tc.startswith)

        self.assertEqual(self.tc.methods['istartswith'], self.tc.istartswith)
        self.assertEqual(self.tc.get('istartswith'), self.tc.istartswith)

        self.assertEqual(self.tc.methods['endswith'], self.tc.endswith)
        self.assertEqual(self.tc.get('endswith'), self.tc.endswith)

        self.assertEqual(self.tc.methods['iendswith'], self.tc.iendswith)
        self.assertEqual(self.tc.get('iendswith'), self.tc.iendswith)

        self.assertEqual(self.tc.methods['contains'], self.tc.contains)
        self.assertEqual(self.tc.get('contains'), self.tc.contains)

        self.assertEqual(self.tc.methods['icontains'], self.tc.icontains)
        self.assertEqual(self.tc.get('icontains'), self.tc.icontains)

        self.assertEqual(self.tc.methods['regexp'], self.tc.regexp)
        self.assertEqual(self.tc.get('regexp'), self.tc.regexp)

    # -----------------------------------------------------------------------

    def test_exact(self):
        """tag == text (case sensitive)."""

        self.assertTrue(self.tc.exact(sppasTag("abc"), u("abc")))
        self.assertFalse(self.tc.exact(sppasTag("abc"), u("ABC")))

        with self.assertRaises(TypeError):
            self.tc.exact("abc", u("ABC"))
        with self.assertRaises(TypeError):
            self.tc.exact(sppasTag("abc"), b("ABC"))

    # -----------------------------------------------------------------------

    def test_iexact(self):
        """tag == text (case in-sensitive)."""

        self.assertTrue(self.tc.iexact(sppasTag("abc"), u("ABC")))
        self.assertFalse(self.tc.iexact(sppasTag("abc"), u("AAA")))

        with self.assertRaises(TypeError):
            self.tc.iexact("abc", u("ABC"))
        with self.assertRaises(TypeError):
            self.tc.iexact(sppasTag("abc"), b("ABC"))

    # -----------------------------------------------------------------------

    def test_startswith(self):
        """tag startswith text (case sensitive)."""

        self.assertTrue(self.tc.startswith(sppasTag("abc"), u("a")))
        self.assertFalse(self.tc.startswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.startswith("abc", u("a"))
        with self.assertRaises(TypeError):
            self.tc.startswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_istartswith(self):
        """tag startswith text (case in-sensitive)."""

        self.assertTrue(self.tc.istartswith(sppasTag("abc"), u("A")))
        self.assertFalse(self.tc.istartswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.istartswith("abc", u("A"))
        with self.assertRaises(TypeError):
            self.tc.istartswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_endswith(self):
        """tag endswith text (case sensitive)."""

        self.assertTrue(self.tc.endswith(sppasTag("abc"), u("c")))
        self.assertFalse(self.tc.endswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.endswith("abc", u("c"))
        with self.assertRaises(TypeError):
            self.tc.endswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_iendswith(self):
        """tag endswith text (case in-sensitive)."""

        self.assertTrue(self.tc.iendswith(sppasTag("abc"), u("C")))
        self.assertFalse(self.tc.iendswith(sppasTag("abc"), u("b")))

        with self.assertRaises(TypeError):
            self.tc.iendswith("abc", u("C"))
        with self.assertRaises(TypeError):
            self.tc.iendswith(sppasTag("abc"), b("b"))

    # -----------------------------------------------------------------------

    def test_contains(self):
        """tag contains text (case sensitive)."""

        self.assertTrue(self.tc.contains(sppasTag("abc"), u("b")))
        self.assertFalse(self.tc.contains(sppasTag("abc"), u("B")))

        with self.assertRaises(TypeError):
            self.tc.contains("abc", u("b"))
        with self.assertRaises(TypeError):
            self.tc.contains(sppasTag("abc"), b("B"))

    # -----------------------------------------------------------------------

    def test_icontains(self):
        """tag contains text (case in-sensitive)."""

        self.assertTrue(self.tc.icontains(sppasTag("abc"), u("B")))
        self.assertFalse(self.tc.icontains(sppasTag("abc"), u("d")))

        with self.assertRaises(TypeError):
            self.tc.icontains("abc", u("B"))
        with self.assertRaises(TypeError):
            self.tc.icontains(sppasTag("abc"), b("d"))

    # -----------------------------------------------------------------------

    def test_regexp(self):
        """tag matches the regexp."""

        self.assertTrue(self.tc.regexp(sppasTag("abc"), "^a[a-z]"))
        self.assertFalse(self.tc.regexp(sppasTag("abc"), "d"))

        with self.assertRaises(TypeError):
            self.tc.regexp("abc", b("B"))

    # -----------------------------------------------------------------------

    def test_combine_methods(self):
        self.assertTrue(
            self.tc.startswith(sppasTag("abc"),
                               u("a")) and self.tc.endswith(sppasTag("abc"),
                                                            u("c")))
        self.assertTrue(
            self.tc.get("startswith")(sppasTag("abc"),
                                      u("a")) and self.tc.get("endswith")(sppasTag("abc"),
                                                                          u("c")))

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):
    """Test sppasLabel()."""

    def test_init(self):
        label = sppasLabel(None)
        self.assertIsNone(label.get_best())

        t = sppasTag("score0.5")
        label = sppasLabel(t)
        self.assertEqual(1, len(label))
        self.assertEqual([t, None], label[0])

        label = sppasLabel(t, 0.5)
        self.assertEqual(1, len(label))
        self.assertEqual([t, 0.5], label[0])

        # inconsistency between given tags and scores
        label = sppasLabel(t, [0.5, 0.5])
        self.assertIsNone(label.get_score(t))

        label = sppasLabel([t, t], 0.5)
        self.assertEqual(1, len(label))
        self.assertIsNone(label.get_score(t))

    # -----------------------------------------------------------------------

    def test_key(self):
        label = sppasLabel(tag=None)
        self.assertIsNone(label.get_key())
        label.set_key("id001")
        self.assertEqual(label.key, "id001")
        label.set_key()
        self.assertIsNone(label.get_key())

    # -----------------------------------------------------------------------

    def test_unicode(self):
        sppasLabel(sppasTag("être"))

    # -----------------------------------------------------------------------

    def test_label_type(self):
        label = sppasLabel(sppasTag(2, "int"))
        self.assertIsInstance(str(label.get_best()), str)
        self.assertIsInstance(label.get_best().get_content(), text_type)
        self.assertIsInstance(label.get_best().get_typed_content(), int)

    # -----------------------------------------------------------------------

    def test_is_label(self):
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertFalse(text.is_speech())

    # -----------------------------------------------------------------------

    def test_append(self):
        # do not add an already existing tag (test without scores)
        t = sppasTag("score0.5")
        label = sppasLabel(t)
        label.append(t)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))
        self.assertIsNone(label.get_score(t))

        # do not add an already existing tag (test with scores)
        t = sppasTag("score0.5")
        label = sppasLabel(t, score=0.5)
        label.append(t)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))
        self.assertEqual(label.get_score(t), 0.5)
        label.append(t, score=0.5)
        self.assertEqual(label.get_score(t), 1.)

    # -----------------------------------------------------------------------

    def test_add_tag(self):
        label = sppasLabel(sppasTag("score0.5"), score=0.5)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))

        label.append(sppasTag("score0.8"), score=0.8)
        self.assertEqual(label.get_best().get_content(), u("score0.8"))

        label.append(sppasTag("score1.0"), score=1.0)
        self.assertEqual(label.get_best().get_content(), u("score1.0"))

        # expect error (types inconsistency):
        text1 = sppasTag(2.1)
        self.assertEqual(text1.get_type(), "str")
        text2 = sppasTag(2.10, tag_type="float")
        self.assertEqual(text2.get_type(), "float")
        label.append(text1, score=0.8)
        with self.assertRaises(TypeError):
            label.append(text2, score=0.2)

    # -----------------------------------------------------------------------

    def test_is_empty(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label.get_best().is_empty())

        label.append(sppasTag("text"), score=0.8)
        self.assertFalse(label.get_best().is_empty())

    # -----------------------------------------------------------------------

    def test_equal(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label == label)
        self.assertEqual(label, label)
        self.assertTrue(label == sppasLabel(sppasTag(""), score=0.5))
        self.assertFalse(label == sppasLabel(sppasTag(""), score=0.7))
        self.assertFalse(label == sppasLabel(sppasTag("a"), score=0.5))

    # -----------------------------------------------------------------------

    def test_set_score(self):
        tag = sppasTag("toto")
        label = sppasLabel(tag, score=0.5)
        self.assertEqual(label.get_score(tag), 0.5)
        label.set_score(tag, 0.8)
        self.assertEqual(label.get_score(tag), 0.8)

    # -----------------------------------------------------------------------

    def test_match(self):
        """Test if a tag matches some functions."""

        t = sppasTagCompare()
        l = sppasLabel(sppasTag("para"))

        self.assertFalse(l.match([(t.exact, u("par"), False)]))
        self.assertTrue(l.match([(t.exact, u("par"), True)]))

        f1 = (t.startswith, u("p"), False)
        f2 = (t.iendswith, u("O"), False)
        self.assertTrue(l.match([f1, f2], logic_bool="or"))
        self.assertFalse(l.match([f1, f2], logic_bool="and"))

        l.append(sppasTag("pata"))
        self.assertTrue(l.match([(t.endswith, u("ta"), False)]))

    # -----------------------------------------------------------------------

    def test_copy(self):
        label = sppasLabel(sppasTag("tag"), score=0.5)
        copied = label.copy()
        self.assertTrue(copied == label)
        self.assertFalse(copied is label)
