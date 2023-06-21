from typing import cast
from PySide6.QtGui import QUndoStack

qapp = cast('app.Application', None)
undoStack = QUndoStack()