# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.aio.teicorpo.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Input/Output of the TEI-Corpo file format (.tei).

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

TEI (Text Encoding Initiative) is an XML vocabulary maintained by the TEI
Consortium. TEI-Corpo is the subset of TEI produced and read by the
TeiCorpo conversion tool for the annotated recordings of spoken corpora.
See <https://github.com/christopheparisse/teicorpo>.

The structures of TEI-Corpo are:
    - a "timeline" of "when" elements giving the time values in seconds,
      an un-aligned time has the interval value "-1";
    - an "annotationBlock" for each annotation of a primary tier, whose
      name is its "who" attribute, with the text in "u/seg";
    - "spanGrp" elements, nested at any depth, for the annotations of the
      child tiers, whose name is their "type" attribute, aligned with
      "from"/"to" or attached to another annotation with "target";
    - the declaration of the tiers, with their parent, in the
      "TEMPLATE_DESC" notes of the header;
    - the media and the speakers in the header.

Nothing is lost when reading then writing a TEI-Corpo file:
    - an annotation with only one aligned time is a point annotation;
    - the annotations without any aligned time are the successive labels
      of the next aligned annotation of their tier, like in ELAN files;
    - the "pause" elements of an utterance are the "+" symbol of the
      SPPAS transcription convention, the other event elements are
      enclosed into braces;
    - the identifiers, the target links, the declaration of the tiers,
      the speakers and the revisions are kept in the metadata.

"""

import copy
import logging
import xml.etree.cElementTree as ET

from sppas.core.config import sg
from sppas.core.coreutils import sppasReadError
from sppas.core.coreutils import sppasUnicode

from ..media import sppasMedia
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from .basetrsio import sppasBaseIO

# ---------------------------------------------------------------------------

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

# The "when" identifier shared by all the un-aligned times at writing time.
UNALIGNED_ID = "TU"

# ---------------------------------------------------------------------------


class sppasTEICORPO(sppasBaseIO):
    """SPPAS reader and writer of the TEI-Corpo files.

    The reading fills one tier for each "who" of the annotation blocks
    and one tier for each "type" of the span groups. The writing gives
    back the structures of the reading: the annotation blocks of the
    primary tiers, the span groups of their child tiers nested in the
    blocks, and the "target" links.

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of TEI format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r', encoding="utf-8") as fp:
                for i in range(10):
                    line = fp.readline()
                    if "<TEI" in line and TEI_NS in line:
                        return True
        except (IOError, UnicodeDecodeError):
            return False

        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def _tei(tag):
        """Return the fully qualified name of a TEI element.

        :param tag: (str) Local name of the element.
        :return: (str)

        """
        return "{" + TEI_NS + "}" + tag

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasTEICORPO instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasTEICORPO, self).__init__(name)

        self.default_extension = "tei"
        self.software = "TeiCorpo"

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_empty_tier = True
        self._accept_metadata = True
        self._accept_comments = False
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_tag_types = False
        self._accept_tag_geometry = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------------
    # Reader
    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a TEI-Corpo file and fill the Transcription.

        :param filename: (str)

        """
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except ET.ParseError as e:
            raise sppasReadError(filename, msg=str(e))

        self._parse_header(root)
        times = sppasTEICORPO._parse_timeline(root)

        spans_by_id = dict()
        pending_targets = list()
        pending_labels = dict()
        body = root.find(sppasTEICORPO._tei("text") + "/" + sppasTEICORPO._tei("body"))
        if body is not None:
            for block in body.iter(sppasTEICORPO._tei("annotationBlock")):
                self._parse_annotation_block(
                    block, times, spans_by_id, pending_targets, pending_labels)

        # The annotations un-aligned at the end of their tier were not
        # attached to an aligned one.
        for tier_name in pending_labels:
            for texts, xml_id in pending_labels[tier_name]:
                logging.error("The annotation {:s} of the tier {:s} has no "
                              "aligned time at all: it is lost."
                              "".format(xml_id, tier_name))

        # The annotations attached to another one with a "target"
        for tier_name, target_id, text, xml_id in pending_targets:
            location = spans_by_id.get(target_id, None)
            if location is None:
                logging.error("Unknown target {:s} in tier {:s}."
                              "".format(target_id, tier_name))
                continue
            tier = self.find(tier_name)
            ann = tier.create_annotation(location.copy(),
                                         sppasLabel(sppasTag(text)))
            if len(xml_id) > 0:
                ann.set_meta("id", xml_id)
            ann.set_meta("tei_target", target_id)

        self._create_hierarchy()

    # -----------------------------------------------------------------------

    def _parse_header(self, root):
        """Parse the header: metadata, media, speakers and tiers.

        The declaration of the tiers fills the "tei_parent", "tei_type"
        and "tei_timealign" metadata of the created tiers. The speakers
        fill their "speaker_..." metadata. The revisions fill the
        "tei_revision_..." metadata of the transcription.

        :param root: (ET) XML element tree root.

        """
        header = root.find(sppasTEICORPO._tei("teiHeader"))
        if header is None:
            return

        # Title of the document
        desc = header.find(".//" + sppasTEICORPO._tei("titleStmt") +
                           "/" + sppasTEICORPO._tei("title") +
                           "/" + sppasTEICORPO._tei("desc"))
        if desc is not None and desc.text is not None:
            self.set_meta("tei_title_desc", desc.text)

        # Media of the recording
        for media_root in header.iter(sppasTEICORPO._tei("media")):
            media_url = media_root.attrib.get("url", "")
            if len(media_url) > 0:
                media = sppasMedia(media_url,
                                   mime_type=media_root.attrib.get("mimeType", None))
                self.add_media(media)

        # Declaration of the tiers: code, parent, type, timealign
        for note in header.iter(sppasTEICORPO._tei("note")):
            if note.attrib.get("type", "") != "TEMPLATE_DESC":
                continue
            for tier_note in note.findall(sppasTEICORPO._tei("note")):
                declared = dict()
                for sub_note in tier_note.findall(sppasTEICORPO._tei("note")):
                    declared[sub_note.attrib.get("type", "")] = sub_note.text
                code = declared.get("code", None)
                if code is None:
                    continue
                tier = self.create_tier(code)
                for key, value in declared.items():
                    if key != "code" and value is not None:
                        tier.set_meta("tei_" + key, value)

        # Speakers: attached to their tier with the "alt" elements
        for person in header.iter(sppasTEICORPO._tei("person")):
            name_node = person.find(sppasTEICORPO._tei("persName"))
            for alt in person.iter(sppasTEICORPO._tei("alt")):
                tier = self.find(alt.attrib.get("type", ""))
                if tier is None:
                    continue
                if name_node is not None and name_node.text is not None:
                    tier.set_meta("speaker_name", name_node.text)
                for key, value in person.attrib.items():
                    tier.set_meta("speaker_" + key, value)
                for person_note in person.findall(sppasTEICORPO._tei("note")):
                    note_type = person_note.attrib.get("type", "")
                    if len(note_type) > 0 and person_note.text is not None:
                        tier.set_meta("speaker_note_" + note_type, person_note.text)

        # Revisions of the document
        revision_desc = header.find(sppasTEICORPO._tei("revisionDesc"))
        if revision_desc is not None:
            for item in revision_desc.iter(sppasTEICORPO._tei("item")):
                item_desc = item.find(sppasTEICORPO._tei("desc"))
                if item_desc is not None and item_desc.text is not None \
                        and item.text is not None:
                    self.set_meta("tei_revision_" + item_desc.text, item.text)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_timeline(root):
        """Parse the timeline and return the time values in seconds.

        An un-aligned time -- TeiCorpo writes it with the interval value
        "-1" -- is stored with the value None.

        :param root: (ET) XML element tree root.
        :return: (dict) "when" identifier -> float or None.

        """
        times = dict()
        timeline = root.find(sppasTEICORPO._tei("text") + "/" +
                             sppasTEICORPO._tei("timeline"))
        if timeline is None:
            return times

        for when in timeline.findall(sppasTEICORPO._tei("when")):
            when_id = when.attrib.get(XML_ID, "")
            if "absolute" in when.attrib:
                times[when_id] = float(when.attrib["absolute"])

        for when in timeline.findall(sppasTEICORPO._tei("when")):
            when_id = when.attrib.get(XML_ID, "")
            if "interval" in when.attrib:
                interval = float(when.attrib["interval"])
                if interval < 0.:
                    times[when_id] = None
                    continue
                since = when.attrib.get("since", "").lstrip("#")
                origin = times.get(since, 0.)
                if origin is None:
                    origin = 0.
                times[when_id] = interval + origin

        return times

    # -----------------------------------------------------------------------

    def _parse_annotation_block(self, block, times, spans_by_id,
                                pending_targets, pending_labels):
        """Parse an annotationBlock and its nested span groups.

        :param block: (ET) The annotationBlock element.
        :param times: (dict) "when" identifier -> float or None.
        :param spans_by_id: (dict) Identifier -> sppasLocation, completed here.
        :param pending_targets: (list) Annotations attached to another one,
        completed here with (tier name, target identifier, text, id) entries.
        :param pending_labels: (dict) Tier name -> list of (text, id) of the
        annotations without any aligned time, waiting for an aligned one.

        """
        tier_name = block.attrib.get("who", "")
        if len(tier_name) == 0:
            tier_name = "no_speaker"
            if self.find(tier_name) is None:
                self.create_tier(tier_name).set_meta("tei_who", "")
        u_node = block.find(sppasTEICORPO._tei("u"))
        texts = sppasTEICORPO._parse_utterance(u_node)
        ann = self._add_annotation(
            tier_name, block.attrib.get("start", ""), block.attrib.get("end", ""),
            texts, block.attrib.get(XML_ID, ""), times, spans_by_id, pending_labels)
        if ann is not None and sppasTEICORPO._is_rich_utterance(u_node) is True:
            raw = "".join(
                ET.tostring(sppasTEICORPO._strip_namespace(child), encoding="unicode")
                for child in u_node)
            ann.set_meta("tei_u", raw)
            # The snapshot of the text is made from the created labels,
            # after the normalizations of sppasTag, so it matches the
            # comparison made at writing time.
            ann.set_meta("tei_u_text",
                         " ".join(label.get_best().get_content()
                                  for label in ann.get_labels()))

        # The span groups: annotations of the child tiers. They can be
        # nested at any depth -- a span can hold the group of the
        # annotations attached to it.
        for span_grp in block.iter(sppasTEICORPO._tei("spanGrp")):
            span_tier_name = span_grp.attrib.get("type", "")
            tier = self.find(span_tier_name)
            if tier is None:
                tier = self.create_tier(span_tier_name)
            # The tier can be already created by the declaration of the
            # header: it is a span-tier anyway.
            tier.set_meta("tei_hierarchy", "span")
            if "tei_parent" not in tier.get_meta_keys():
                tier.set_meta("tei_parent", tier_name)
            for span in span_grp.findall(sppasTEICORPO._tei("span")):
                span_text = span.text if span.text is not None else ""
                span_id = span.attrib.get(XML_ID, "")
                if "target" in span.attrib:
                    pending_targets.append(
                        (span_tier_name, span.attrib["target"].lstrip("#"),
                         span_text, span_id))
                    continue
                self._add_annotation(
                    span_tier_name, span.attrib.get("from", ""),
                    span.attrib.get("to", ""), [span_text], span_id,
                    times, spans_by_id, pending_labels)

    # -----------------------------------------------------------------------

    @staticmethod
    def _strip_namespace(node):
        """Return a copy of a node without the TEI namespace in the tags.

        :param node: (ET) XML element.
        :return: (ET)

        """
        node = copy.deepcopy(node)
        for element in node.iter():
            if element.tag.startswith("{"):
                element.tag = element.tag.split("}")[1]
        return node

    # -----------------------------------------------------------------------

    @staticmethod
    def _is_rich_utterance(u_node):
        """Return True if the utterance holds more than plain segments.

        :param u_node: (ET or None) The "u" element.
        :return: (bool)

        """
        if u_node is None:
            return False
        for child in u_node:
            if child.tag != sppasTEICORPO._tei("seg"):
                return True
            if len(child) > 0:
                return True
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_utterance(u_node):
        """Return the texts of an utterance element, one per segment.

        The "pause" elements are the "+" symbol of the SPPAS
        transcription convention, and the other event elements are
        enclosed into braces. Both are appended to the current segment.

        :param u_node: (ET or None) The "u" element.
        :return: (list of str)

        """
        if u_node is None:
            return list()

        parts = list()
        for child in u_node:
            local_name = child.tag.split("}")[-1]
            if local_name == "seg":
                text = ""
                if child.text is not None:
                    text = child.text.strip()
                for event in child:
                    event_text = sppasTEICORPO._event_text(event)
                    text = (text + " " + event_text).strip()
                parts.append(text)
                continue

            event = sppasTEICORPO._event_text(child)
            if len(parts) == 0:
                parts.append(event)
            else:
                parts[-1] = (parts[-1] + " " + event).strip()

        return parts

    # -----------------------------------------------------------------------

    @staticmethod
    def _event_text(node):
        """Return the readable text of an event element of an utterance.

        A pause is the "+" symbol of the SPPAS transcription convention,
        any other event is a comment, enclosed into braces.

        :param node: (ET) The event element.
        :return: (str)

        """
        local_name = node.tag.split("}")[-1]
        if local_name == "pause":
            return "+"

        node_desc = node.find(sppasTEICORPO._tei("desc"))
        if node_desc is not None and node_desc.text is not None:
            return "{" + node_desc.text + "}"
        return "{" + local_name + "}"

    # -----------------------------------------------------------------------

    def _add_annotation(self, tier_name, begin_ref, end_ref, texts, xml_id,
                        times, spans_by_id, pending_labels):
        """Create the annotation matching the given references.

        An annotation with only one aligned time is a point. An
        annotation without any aligned time is delayed: its text and its
        identifier become the next labels of the next aligned annotation
        of the tier, like in the ELAN files.

        """
        tier = self.find(tier_name)
        if tier is None:
            tier = self.create_tier(tier_name)

        begin = times.get(begin_ref.lstrip("#"), None)
        end = times.get(end_ref.lstrip("#"), None)

        if begin is None and end is None:
            pending_labels.setdefault(tier_name, list()).append((texts, xml_id))
            return None

        if begin is not None and end is not None and begin != end:
            location = sppasLocation(
                sppasInterval(sppasPoint(begin), sppasPoint(end)))
        elif begin is not None:
            location = sppasLocation(sppasPoint(begin))
        else:
            location = sppasLocation(sppasPoint(end))

        labels = [sppasLabel(sppasTag(text)) for text in texts]
        if len(labels) == 0:
            labels = [sppasLabel(sppasTag(""))]
        absorbed = pending_labels.pop(tier_name, list())
        for absorbed_texts, absorbed_id in absorbed:
            for text in absorbed_texts:
                labels.append(sppasLabel(sppasTag(text)))

        ann = tier.create_annotation(location, labels)
        if len(xml_id) > 0:
            ann.set_meta("id", xml_id)
            spans_by_id[xml_id] = location
        if len(absorbed) > 0:
            ann.set_meta("tei_absorbed",
                         " ".join(a_id for a_text, a_id in absorbed))
        return ann

    # -----------------------------------------------------------------------

    def _create_hierarchy(self):
        """Create the hierarchy links declared in the header.

        A link that the hierarchy of SPPAS can't validate is ignored,
        with a message in the log.

        """
        for child_tier in self:
            parent_name = child_tier.get_meta("tei_parent", None)
            if parent_name is None or parent_name == "-":
                continue
            parent_tier = self.find(parent_name)
            if parent_tier is None:
                continue
            try:
                self.add_hierarchy_link("TimeAlignment", child_tier, parent_tier)
            except Exception as e:
                logging.info("The hierarchy link between {:s} and {:s} was "
                             "ignored: {:s}".format(child_tier.get_name(),
                                                    parent_name, str(e)))

    # -----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a TEI-Corpo file with the content of the Transcription.

        :param filename: (str)

        """
        root = ET.Element("TEI")
        root.set("xmlns", TEI_NS)
        root.set("version", "0.9")

        self._format_header(root)

        text_root = ET.SubElement(root, "text")
        times = self._format_timeline(text_root)
        self._format_body(text_root, times)

        sppasTEICORPO.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding=sg.__encoding__,
                   xml_declaration=True, method="xml")

    # -----------------------------------------------------------------------

    def _block_tiers(self):
        """Return the tiers to write as annotation blocks."""
        return [tier for tier in self
                if tier.get_meta("tei_hierarchy", "") != "span"]

    # -----------------------------------------------------------------------

    def _span_tiers(self):
        """Return the tiers to write as span groups."""
        return [tier for tier in self
                if tier.get_meta("tei_hierarchy", "") == "span"]

    # -----------------------------------------------------------------------

    def _format_header(self, root):
        """Add the teiHeader element into the given root.

        :param root: (ET) XML element.

        """
        header = ET.SubElement(root, "teiHeader")

        file_desc = ET.SubElement(header, "fileDesc")
        title_stmt = ET.SubElement(file_desc, "titleStmt")
        title = ET.SubElement(title_stmt, "title")
        desc = ET.SubElement(title, "desc")
        desc.text = self.get_meta("tei_title_desc", self.get_name())
        publication_stmt = ET.SubElement(file_desc, "publicationStmt")
        distributor = ET.SubElement(publication_stmt, "distributor")
        distributor.text = "tei_corpo"

        # Declaration of the tiers, with their parent
        notes_stmt = ET.SubElement(file_desc, "notesStmt")
        template = ET.SubElement(notes_stmt, "note")
        template.set("type", "TEMPLATE_DESC")
        for tier in self:
            if tier.get_meta("tei_who", None) == "":
                continue
            tier_note = ET.SubElement(template, "note")
            code = ET.SubElement(tier_note, "note")
            code.set("type", "code")
            code.text = tier.get_name()
            parent = ET.SubElement(tier_note, "note")
            parent.set("type", "parent")
            parent.text = tier.get_meta("tei_parent", None)
            if parent.text is None:
                parent_tier = self.get_hierarchy().get_parent(tier)
                parent.text = "-" if parent_tier is None else parent_tier.get_name()
            for key in ("type", "subtype", "lang", "timealign", "graphicref"):
                value = tier.get_meta("tei_" + key, None)
                if value is not None:
                    note = ET.SubElement(tier_note, "note")
                    note.set("type", key)
                    note.text = value

        # Media of the recording
        if len(self.get_media_list()) > 0:
            source_desc = ET.SubElement(file_desc, "sourceDesc")
            recording_stmt = ET.SubElement(source_desc, "recordingStmt")
            recording = ET.SubElement(recording_stmt, "recording")
            for media in self.get_media_list():
                media_node = ET.SubElement(recording, "media")
                media_node.set("mimeType", media.get_mime_type())
                media_node.set("url", media.get_filename())

        # Speakers of the tiers
        speakers = [tier for tier in self
                    if any(key.startswith("speaker_")
                           for key in tier.get_meta_keys())]
        if len(speakers) > 0:
            profile_desc = ET.SubElement(header, "profileDesc")
            partic_desc = ET.SubElement(profile_desc, "particDesc")
            list_person = ET.SubElement(partic_desc, "listPerson")
            for tier in speakers:
                person = ET.SubElement(list_person, "person")
                for key in tier.get_meta_keys():
                    if key.startswith("speaker_note_"):
                        note = ET.SubElement(person, "note")
                        note.set("type", key[len("speaker_note_"):])
                        note.text = tier.get_meta(key)
                    elif key.startswith("speaker_") and key != "speaker_name":
                        person.set(key[len("speaker_"):], tier.get_meta(key))
                alt_grp = ET.SubElement(person, "altGrp")
                alt = ET.SubElement(alt_grp, "alt")
                alt.set("type", tier.get_name())
                name = tier.get_meta("speaker_name", None)
                if name is not None:
                    pers_name = ET.SubElement(person, "persName")
                    pers_name.text = name

        encoding_desc = ET.SubElement(header, "encodingDesc")
        app_info = ET.SubElement(encoding_desc, "appInfo")
        application = ET.SubElement(app_info, "application")
        application.set("ident", sg.__name__)
        application.set("version", sg.__version__)
        app_desc = ET.SubElement(application, "desc")
        app_desc.text = "Transcription converted to TEI_CORPO"

        # Revisions of the document
        revisions = [key for key in self.get_meta_keys()
                     if key.startswith("tei_revision_")]
        if len(revisions) > 0:
            revision_desc = ET.SubElement(header, "revisionDesc")
            item_list = ET.SubElement(revision_desc, "list")
            for key in revisions:
                item = ET.SubElement(item_list, "item")
                item.text = self.get_meta(key)
                item_desc = ET.SubElement(item, "desc")
                item_desc.text = key[len("tei_revision_"):]

    # -----------------------------------------------------------------------

    def _format_timeline(self, text_root):
        """Add the timeline element and return the time values.

        The points share a single un-aligned "when", written with the
        interval value "-1" like TeiCorpo does.

        :param text_root: (ET) The text element.
        :return: (dict) float -> "when" identifier.

        """
        values = set()
        has_unaligned = False
        for tier in self:
            for ann in tier:
                if ann.location_is_point() is True:
                    values.add(ann.get_lowest_localization().get_midpoint())
                    has_unaligned = True
                else:
                    values.add(ann.get_lowest_localization().get_midpoint())
                    values.add(ann.get_highest_localization().get_midpoint())

        timeline = ET.SubElement(text_root, "timeline")
        timeline.set("unit", "s")
        origin = ET.SubElement(timeline, "when")
        origin.set("absolute", "0")
        origin.set("xml:id", "T0")

        if has_unaligned is True:
            when = ET.SubElement(timeline, "when")
            when.set("interval", "-1")
            when.set("since", "#T0")
            when.set("xml:id", UNALIGNED_ID)

        times = dict()
        for i, value in enumerate(sorted(values)):
            when = ET.SubElement(timeline, "when")
            when.set("interval", str(value))
            when.set("since", "#T0")
            when.set("xml:id", "T{:d}".format(i + 1))
            times[value] = "T{:d}".format(i + 1)

        return times

    # -----------------------------------------------------------------------

    @staticmethod
    def _time_refs(ann, times):
        """Return the "when" references of an annotation.

        :param ann: (sppasAnnotation)
        :param times: (dict) float -> "when" identifier.
        :return: (tuple) Begin and end references.

        """
        begin = times[ann.get_lowest_localization().get_midpoint()]
        if ann.location_is_point() is True:
            return "#" + begin, "#" + UNALIGNED_ID
        end = times[ann.get_highest_localization().get_midpoint()]
        return "#" + begin, "#" + end

    # -----------------------------------------------------------------------

    def _format_body(self, text_root, times):
        """Add the body element with the blocks and their span groups.

        :param text_root: (ET) The text element.
        :param times: (dict) float -> "when" identifier.

        """
        body = ET.SubElement(text_root, "body")
        div = ET.SubElement(body, "div")
        div.set("type", "Situation")

        # The span-tiers annotations, grouped by their parent block-tier
        span_children = dict()
        targets = dict()
        for tier in self._span_tiers():
            parent_name = tier.get_meta("tei_parent", "")
            for ann in tier:
                if ann.is_meta_key("tei_target") is True:
                    target_id = ann.get_meta("tei_target")
                    targets.setdefault(target_id, list()).append(
                        (tier.get_name(), ann))
                else:
                    span_children.setdefault(parent_name, list()).append(
                        (tier.get_name(), ann))

        for tier in self._block_tiers():
            who = tier.get_meta("tei_who", tier.get_name())
            for ann in tier:
                begin_ref, end_ref = sppasTEICORPO._time_refs(ann, times)
                block = ET.SubElement(div, "annotationBlock")
                block.set("start", begin_ref)
                block.set("end", end_ref)
                block.set("who", who)
                block.set("xml:id", ann.get_meta("id"))
                u_node = ET.SubElement(block, "u")
                raw = ann.get_meta("tei_u", None)
                current_text = " ".join(label.get_best().get_content()
                                        for label in ann.get_labels())
                # The metadata values are normalized by set_meta(): the
                # comparison is made with the same normalization.
                current_text = sppasUnicode(current_text).to_strip()
                if raw is not None and current_text == ann.get_meta("tei_u_text", None):
                    # The utterance was not modified: its original
                    # content is given back, exactly.
                    fragment = ET.fromstring("<u>" + raw + "</u>")
                    for child in fragment:
                        u_node.append(child)
                else:
                    for label in ann.get_labels():
                        seg = ET.SubElement(u_node, "seg")
                        seg.text = label.get_best().get_content()

                sppasTEICORPO._append_targets(u_node_parent=block,
                                              ann_id=ann.get_meta("id"),
                                              targets=targets)
                self._format_spans(
                    block, ann, tier.get_name(), span_children, targets, times)

    # -----------------------------------------------------------------------

    def _format_spans(self, block, block_ann, block_tier_name,
                      span_children, targets, times):
        """Add the span groups of a block, nested like at reading time.

        :param block: (ET) The annotationBlock element.
        :param block_ann: (sppasAnnotation) The annotation of the block.
        :param block_tier_name: (str) Name of the tier of the block.
        :param span_children: (dict) Parent tier name -> (tier name, ann).
        :param targets: (dict) Target identifier -> (tier name, ann).
        :param times: (dict) float -> "when" identifier.

        """
        children = span_children.get(block_tier_name, list())
        if len(children) == 0:
            return

        block_begin = block_ann.get_lowest_localization().get_midpoint()
        block_end = block_ann.get_highest_localization().get_midpoint()

        groups = dict()
        for tier_name, ann in children:
            midpoint = ann.get_lowest_localization().get_midpoint()
            if midpoint < block_begin or midpoint >= block_end:
                continue
            groups.setdefault(tier_name, list()).append(ann)

        for tier_name in groups:
            span_grp = ET.SubElement(block, "spanGrp")
            span_grp.set("type", tier_name)
            for ann in groups[tier_name]:
                span = ET.SubElement(span_grp, "span")
                begin_ref, end_ref = sppasTEICORPO._time_refs(ann, times)
                span.set("from", begin_ref)
                span.set("to", end_ref)
                ann_id = ann.get_meta("id")
                span.set("xml:id", ann_id)
                span.text = ann.serialize_labels(separator=" ", empty="", alt=True)

                sppasTEICORPO._append_targets(u_node_parent=span,
                                              ann_id=ann_id,
                                              targets=targets)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_targets(u_node_parent, ann_id, targets):
        """Add the span groups of the annotations attached to a given one.

        :param u_node_parent: (ET) The element of the targeted annotation.
        :param ann_id: (str) Identifier of the targeted annotation.
        :param targets: (dict) Target identifier -> (tier name, ann).

        """
        for target_tier_name, target_ann in targets.get(ann_id, list()):
            target_grp = ET.SubElement(u_node_parent, "spanGrp")
            target_grp.set("type", target_tier_name)
            target_span = ET.SubElement(target_grp, "span")
            target_span.set("target", "#" + ann_id)
            target_span.set("xml:id", target_ann.get_meta("id"))
            target_span.text = target_ann.serialize_labels(
                separator=" ", empty="", alt=True)

    # -----------------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """Pretty indent of an ElementTree.

        :param elem: (ET) XML element.
        :param level: (int) Level of indentation.

        """
        i = "\n" + level * "\t"
        if len(elem) > 0:
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                sppasTEICORPO.indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
