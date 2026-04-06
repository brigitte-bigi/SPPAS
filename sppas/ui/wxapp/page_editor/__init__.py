"""

## Events:

## EditorPanel(sppasSplitterWindow)

* is notifying: none
* is listening:
    - EVT_TIMELINE_VIEW: _process_timeline_action() with actions:
        * tier_selected
        * tiers_added
        * save
        * ann_create
        * ann_update

    - EVT_LISTANNS_VIEW: _process_listanns_action() with actions:
        * ann_create
        * ann_delete
        * ann_update

    - EVT_SEARCH_VIEW: _process_search_action() with actions:
        * tier_selected

## sppasTimelinePanel(sppasPanel) [parent=EditorPanel()]

* is emitting TimelineViewEvent with the actions:
    - "close" and filename to ask for closing the panel
    - "save" and filename to ask for saving the file of the panel
    - "collapsed" with the filename and value=the object
    - "expanded" with the filename and value=the object
    - "tier_selected" with the filename
    - "tiers_added" with the filename and the list of tier names
    - "ann_create", "ann_delete", "ann_update"

* is listening:
    - wx.EVT_BUTTON and wx.EVT_TOGGLEBUTTON: _process_tool_event()
    - EVT_MEDIA_LOADED: __on_media_loaded()
    - EVT_MEDIA_NOT_LOADED: __on_media_not_loaded()
    - EVT_MEDIA_ACTION: __on_media_action()
        * "visible" to set a new visible range
        * "tiers_annotations" for infos/draw view mode
        * "audio_waveform" for infos/draw view mode
        * "video_film" for infos/draw view mode
        * "sort_files"
        * "play" and "stop" to invalidate the frames in video films

    - EVT_TIMELINE_VIEW: _process_time_event()
        * tier_selected
        * "ann_create", "ann_delete", "ann_update"

"""

from .editor import sppasEditorPanel

__all__ = (
    "sppasEditorPanel"
)
