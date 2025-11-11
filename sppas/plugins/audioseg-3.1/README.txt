------------------------------------------------------------------------------

program:    audioseg
author:     Brigitte Bigi
contact:    contact@sppas.org
date:       2023-05-30
version:    3.2
copyright:  Copyright (C) 2017-2023 Brigitte Bigi
license:    GNU Public License version 3 or any later version
brief:      SPPAS plugin for AudioSegmenter.

AudioSegmenter is a tool to segment audio files into several tracks. Bounds
of the tracks are indicated in an annotated file of any format supported by 
SPPAS (xra, TextGrid, eaf, ...).

New in version 3.x: a video can also be segmented. It must have the same name
than the audio file except for the extension, and the video feature of SPPAS
must be enabled.

Be careful: when defining the optional pattern, it must *not* start by its
'-' which will automatically be added by the plugin.

------------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
------------------------------------------------------------------------------
