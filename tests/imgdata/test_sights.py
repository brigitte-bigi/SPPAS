"""
:filename: sppas.src.imgdata.tests.test_sights.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Tests of the sights class.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import NegativeValueError
from sppas.core.coreutils import IndexRangeException

from sppas.src.imgdata.sights import sppasSights

# ---------------------------------------------------------------------------


class TestSights(unittest.TestCase):

    def setUp(self):
        self.sights = sppasSights(5)

    # ---------------------------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------------------------

    def test_init_wrong_type(self):
        # wrong parameter type cases
        with self.assertRaises(sppasTypeError):
            sppasSights("blabla")

        # negative number cases
        with self.assertRaises(sppasTypeError):
            sppasSights(-6)

    # ---------------------------------------------------------------------------

    def test_init(self):
        sights = sppasSights(5)
        self.assertEqual(5, len(sights))

        for i in range(5):
            self.assertEqual((0, 0, None, None), sights.get_sight(0))

    # ---------------------------------------------------------------------------
    # Getters & Setters
    # ---------------------------------------------------------------------------

    def test_x_list_getter(self):
        self.sights.set_sight(0, 10, 10)
        self.sights.set_sight(1, 10, 10)
        self.sights.set_sight(2, 30, 10)
        self.sights.set_sight(4, 10, 10)

        # test equal
        copy_list = self.sights.get_x()
        self.assertEqual([10, 10, 30, 0, 10], copy_list)

        # test mutability
        copy_list[1] = 150
        self.assertNotEqual(150, self.sights.get_x()[1])

    # ---------------------------------------------------------------------------

    def test_y_list_getter(self):
        self.sights.set_sight(0, 10, 20)
        self.sights.set_sight(1, 10, 20)
        self.sights.set_sight(2, 10, 50)
        self.sights.set_sight(4, 10, 10)

        # test equal
        copy_list = self.sights.get_y()
        self.assertEqual([20, 20, 50, 0, 10], copy_list)

        # test mutability
        copy_list[3] = -20
        self.assertNotEqual(-20, self.sights.get_y()[3])

    # ---------------------------------------------------------------------------

    def test_z_list_getter(self):
        self.sights.set_sight(0, 10, 20)
        self.sights.set_sight(1, 10, 20)
        self.sights.set_sight(2, 10, 50)
        self.sights.set_sight(3, 10, 10)
        self.sights.set_sight(4, 10, 10)

        # z axis not yet set
        self.assertIsNone(self.sights.get_z())

        # set z axis
        self.sights.set_sight_z(0, 44)
        self.sights.set_sight_z(3, 44)

        # test equal
        copy_list = self.sights.get_z()
        self.assertEqual([44, None, None, 44, None], copy_list)

        # test mutability
        copy_list[0] = 66
        self.assertNotEqual(66, self.sights.get_z()[0])

    # ---------------------------------------------------------------------------

    def test_score_list_getter(self):
        self.sights.set_sight(0, 10, 20)
        self.sights.set_sight(1, 10, 20)
        self.sights.set_sight(2, 10, 50)
        self.sights.set_sight(3, 10, 30)
        self.sights.set_sight(4, 10, 30)

        # score not yet set
        self.assertIsNone(self.sights.get_score())

        # set score
        self.sights.set_sight_score(0, 62.1)
        self.sights.set_sight_score(4, 48.9)

        # test equal
        copy_list = self.sights.get_score()
        self.assertEqual([62.1, None, None, None, 48.9], copy_list)

        # test mutability
        copy_list[3] = 0.2
        self.assertNotEqual(0.2, self.sights.get_score()[3])

    # ---------------------------------------------------------------------------

    def test_x_getter(self):
        # 0 by default for x-axis not yet set
        self.assertEqual(0, self.sights.x(2))

        self.sights.set_sight(2, 80, 10)
        self.assertEqual(80, self.sights.x(2))

    # ---------------------------------------------------------------------------

    def test_y_getter(self):
        # 0 by default for y-axis not yet set
        self.assertEqual(0, self.sights.y(3))

        self.sights.set_sight(3, 10, 40)
        self.assertEqual(40, self.sights.y(3))

    # ---------------------------------------------------------------------------

    def test_z_getter(self):
        # None by default for z-axis not yet set
        self.assertIsNone(self.sights.z(1))

        self.sights.set_sight_z(1, 33)

        # test correct cases
        self.assertIsNone(self.sights.z(4))  # None value for z index not set
        self.assertEqual(33, self.sights.z(1))

    # ---------------------------------------------------------------------------

    def test_score_getter(self):
        # None by default for score not yet set
        self.assertIsNone(self.sights.score(1))

        self.sights.set_sight_score(1, 33)

        # test correct cases
        self.assertIsNone(self.sights.score(4))  # None value for score index not set
        self.assertEqual(33, self.sights.score(1))

    # ---------------------------------------------------------------------------

    def test_sight_getter(self):
        # sight not yet set case
        self.assertEqual((0, 0, None, None), self.sights.get_sight(2))

        # test with sight set
        self.sights.set_sight(2, 50, 50, 3, 1.8)
        self.assertEqual((50, 50, 3, 1.8), self.sights.get_sight(2))

    # ---------------------------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------------------------

    def test_reset_method(self):
        # set all sights
        for i in range(len(self.sights)):
            self.sights.set_sight(i, 10, 10, z=10, score=0.44)

        # reset sights
        self.sights.reset()

        # test if value are reset
        self.assertEqual([0, 0, 0, 0, 0], self.sights.get_x())
        self.assertEqual([0, 0, 0, 0, 0], self.sights.get_y())
        self.assertIsNone(self.sights.get_z())
        self.assertIsNone(self.sights.get_score())

    # ---------------------------------------------------------------------------

    def test_copy_method(self):
        sights_copy = self.sights.copy()
        sights_copy.set_sight(0, 10, 10)

        self.assertNotEqual(10, self.sights.x(0))
        self.assertNotEqual(10, self.sights.y(0))

    # ---------------------------------------------------------------------------

    def test_check_index_method(self):
        # test wrong index cases
        with self.assertRaises(sppasTypeError):
            self.sights.get_sight("blabla")

        with self.assertRaises(NegativeValueError):
            self.sights.get_sight(-7)

        with self.assertRaises(IndexRangeException):
            self.sights.get_sight(666)

        # test correct case
        self.assertEqual(2, self.sights.check_index(2))

    # ---------------------------------------------------------------------------

    def test_mean_method(self):
        for i in range(len(self.sights)):
            self.sights.set_sight_score(i, 2)

        computed_mean = 2 * len(self.sights) / len(self.sights)
        self.assertEqual(computed_mean, self.sights.get_mean_score())

    # ---------------------------------------------------------------------------

    def test_intermediate_method(self):
        other_sights = sppasSights(5)

        for i in range(len(self.sights)):
            self.sights.set_sight(i, 10, 10, 10, 0.5)
            other_sights.set_sight(i, 20, 20, 20, 1)

        intermediate_sights = self.sights.intermediate(other_sights)

        self.assertEqual([15, 15, 15, 15, 15], intermediate_sights.get_x())
        self.assertEqual([15, 15, 15, 15, 15], intermediate_sights.get_y())
        self.assertEqual([15, 15, 15, 15, 15], intermediate_sights.get_z())
        self.assertEqual([0.75, 0.75, 0.75, 0.75, 0.75], intermediate_sights.get_score())
