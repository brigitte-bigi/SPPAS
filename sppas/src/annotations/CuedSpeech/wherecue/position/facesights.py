# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.facesights.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Sights on a face of size 1000x1000px.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

    ---------------------------------------------------------------------

"""

from sppas.src.imgdata import sppasSights

# ---------------------------------------------------------------------------


class FaceTwoDim(object):
    """Some (x, y) coordinates among the 68 sights on a 1000x1000px face.

    :Example:

        >>>with FaceTwoDim() as face:
        >>>    print(face.sights.x(0))
        >>>    print(face.dim)

    """

    def __init__(self):
        """Create the dictionary with sights coords.

        """
        s = sppasSights(68)
        s.set_sight(0, 0, 165)
        s.set_sight(1, 2, 300)
        s.set_sight(2, 15, 435)
        s.set_sight(3, 40, 570)
        s.set_sight(4, 90, 695)
        s.set_sight(5, 170, 805)
        s.set_sight(6, 260, 905)
        s.set_sight(7, 375, 980)
        s.set_sight(8, 500, 1000)
        s.set_sight(9, 625, 980)
        s.set_sight(10, 760, 905)
        s.set_sight(11, 830, 805)
        s.set_sight(12, 910, 695)
        s.set_sight(13, 960, 570)
        s.set_sight(14, 985, 435)
        s.set_sight(15, 998, 300)
        s.set_sight(16, 1000, 165)
        s.set_sight(17, 99, 70)
        s.set_sight(18, 170, 15)
        s.set_sight(19, 250, 0)
        s.set_sight(20, 330, 20)
        s.set_sight(21, 410, 55)
        s.set_sight(22, 590, 55)
        s.set_sight(23, 680, 20)
        s.set_sight(24, 750, 0)
        s.set_sight(25, 820, 15)
        s.set_sight(26, 910, 70)
        s.set_sight(27, 500, 150)
        s.set_sight(28, 500, 240)
        s.set_sight(29, 500, 330)
        s.set_sight(30, 500, 420)
        s.set_sight(31, 390, 480)
        s.set_sight(32, 445, 500)
        s.set_sight(33, 500, 510)
        s.set_sight(34, 555, 500)
        s.set_sight(35, 620, 480)
        s.set_sight(36, 200, 160)
        s.set_sight(37, 255, 132)
        s.set_sight(38, 315, 132)
        s.set_sight(39, 370, 170)
        s.set_sight(40, 315, 185)
        s.set_sight(41, 255, 185)
        s.set_sight(42, 630, 170)
        s.set_sight(43, 685, 132)
        s.set_sight(44, 745, 132)
        s.set_sight(45, 800, 160)
        s.set_sight(46, 745, 185)
        s.set_sight(47, 685, 185)
        s.set_sight(48, 302, 633)
        s.set_sight(49, 375, 610)
        s.set_sight(50, 445, 600)
        s.set_sight(51, 500, 605)
        s.set_sight(52, 555, 600)
        s.set_sight(53, 625, 610)
        s.set_sight(54, 698, 633)
        s.set_sight(55, 625, 705)
        s.set_sight(56, 555, 745)
        s.set_sight(57, 500, 750)
        s.set_sight(58, 445, 745)
        s.set_sight(59, 375, 705)
        s.set_sight(60, 328, 635)
        s.set_sight(61, 445, 645)
        s.set_sight(62, 500, 650)
        s.set_sight(63, 555, 645)
        s.set_sight(64, 672, 635)
        s.set_sight(65, 555, 677)
        s.set_sight(66, 500, 682)
        s.set_sight(67, 445, 677)

        self.__dict__ = dict(
            dim=68,
            sights=s,
            size=1000
        )
