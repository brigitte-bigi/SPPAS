from whakerkit.components import Components

from .view import ViewBarNode
from .view import ViewManager
from .view import BaseViewNode
from .progress import ProgressBar
from .annot_param import AnnotParamDialog

# ---------------------------------------------------------------------------

Components.register('Views', BaseViewNode.REQUIRED)
Components.register('ProgressBar', ProgressBar.REQUIRED)
Components.register('AnnotParamDialog', AnnotParamDialog.REQUIRED)

# ---------------------------------------------------------------------------


__all__ = (
    "BaseViewNode",
    "ViewBarNode",
    "ViewManager",
    "AnnotParamDialog",
    "Components"
)
