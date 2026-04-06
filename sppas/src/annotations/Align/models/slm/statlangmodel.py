"""
:filename: sppas.src.annotations.Align.models.slm.statlangmodel.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Statistical language model representation and use.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

from ..modelsexc import ModelsDataTypeError
from .arpaio import sppasArpaIO

# ---------------------------------------------------------------------------


class sppasSLM(object):
    """Statistical language model representation.

    """

    def __init__(self):
        """Create a sppasSLM instance without model."""
        self.model = None

    # -----------------------------------------------------------------------

    def set(self, model):
        """Set the language model.

        :param model: (list) List of lists of tuples for 1-gram, 2-grams, ...

        """
        if not (isinstance(model, list) and
                all([isinstance(m, list) for m in model])):
            raise ModelsDataTypeError("slm",
                                      "list of lists of tuples",
                                      type(model))

        self.model = model

    # -----------------------------------------------------------------------

    def load_from_arpa(self, filename):
        """Load the model from an ARPA-ASCII file.

        :param filename: (str) Filename from which to read the model.

        """
        arpa_io = sppasArpaIO()
        self.model = arpa_io.load(filename)

    # -----------------------------------------------------------------------

    def save_as_arpa(self, filename):
        """Save the model into an ARPA-ASCII file.

        :param filename: (str) Filename in which to write the model.

        """
        arpa_io = sppasArpaIO()
        arpa_io.set(self.model)
        arpa_io.save(filename)

    # -----------------------------------------------------------------------

    def evaluate(self, filename):
        """Evaluate a model on a file (perplexity)."""
        raise NotImplementedError("The method 'evaluate' of sppasSLM is "
                                  "not implemented yet. Any help is welcome!")

    # -----------------------------------------------------------------------

    def interpolate(self, other):
        """Interpolate the model with another one.

        An N-Gram language model can be constructed from a linear interpolation
        of several models. In this case, the overall likelihood P(w|h) of a
        word w occurring after the history h is computed as the arithmetic
        average of P(w|h) for each of the models.

        The default interpolation method is linear interpolation. In addition,
        log-linear interpolation of models is possible.

        :param other: (sppasSLM)
        """
        raise NotImplementedError("The method 'interpolate' of sppasSLM is "
                                  "not implemented yet. Any help is welcome!")
