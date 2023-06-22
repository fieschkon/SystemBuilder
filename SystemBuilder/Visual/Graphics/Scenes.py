from collections import defaultdict
import typing
from abc import abstractmethod
from typing import Optional

from PySide6 import QtCore, QtGui
from PySide6.QtCore import (QEasingCurve, QLineF, QPointF, QRect, 
                            QRectF, Qt, QVariantAnimation, Signal)
from PySide6.QtGui import (QPixmap, QWheelEvent, QPainter)
from PySide6.QtWidgets import (QGraphicsScene,
                               QGraphicsView, QWidget, QSizePolicy)
from PySide6.QtCore import QPointF, QParallelAnimationGroup, QVariantAnimation, QAbstractAnimation

from SystemBuilder.Core.Settings import SettingsLoader
from SystemBuilder.Core.Callback import Delegate

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QPointF



GRIDSIZE = (25, 25)
ENDOFFSET = -QPointF(25, 25)


class DiagramViewer(QGraphicsView):

    newVisibleArea = Signal(QRectF)

    def __init__(self, scene: QGraphicsScene, parent = None):
        super(DiagramViewer, self).__init__(scene, parent)
        self._scene = scene
        self.startPos = None
        self.zoomlevel = 0
        self.setAcceptDrops(True)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.OrganizeRequested = Delegate(self.__class__)
        self.CopyRequested     = Delegate(self.__class__, QRectF)
        self.SaveRequested     = Delegate(self.__class__)
        self.DeleteRequested   = Delegate(self.__class__)

    ''' Item Focusing '''

    def moveTo(self, pos: QPointF):
        self.anim = QVariantAnimation()
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        self.anim.setStartValue(self.mapToScene(self.rect().center()))
        self.anim.setEndValue(QPointF(pos.x(), pos.y()))
        self.anim.valueChanged.connect(self._moveTick)
        self.anim.finished.connect(self.repaintTraces)
        self.anim.start()

    def _moveTick(self, pos):
        self.centerOn(pos)

    def repaintTraces(self):
        self._scene.update()
        self.update()

    ''' Drag and Drop behavior '''

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        return super().dropEvent(event)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.accept()
        event.acceptProposedAction()
        return super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        event.accept()
        return super().dragMoveEvent(event)

    def contextMenuEvent(self, event) -> None:
        pass

    ''' Scroll behavior
    Responsible for scaling when scrolling
    '''

    def wheelEvent(self, event: QWheelEvent, norep=False):

        if Qt.KeyboardModifier.ControlModifier == event.modifiers():

            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            if event.angleDelta().y() > 0:
                self.scale(1.1, 1.1)
                self.zoomlevel += 1
            else:
                self.scale(0.9, 0.9)
                self.zoomlevel -= 1
        else:
            super(DiagramViewer, self).wheelEvent(event)
        self.newVisibleArea.emit(self.mapToScene(
            self.viewport().geometry()).boundingRect())
        self._scene.update()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        return super().keyPressEvent(event)

class DiagramScene(QGraphicsScene):

    formatFinished = Signal()

    def __init__(self):
        super().__init__()

        self._dragged = False
        self.moveditems = 0
        # self.setBackgroundBrush(configuration.GridColor)
        self.buffer = 10

    def animate_items(self, item_positions, animation_duration=400):
        parallel_animations = QParallelAnimationGroup(self)

        for item, target_position in item_positions.items():
            animation = QVariantAnimation(self)
            animation.setStartValue(item.pos())
            animation.setEndValue(target_position)
            animation.setDuration(animation_duration)
            animation.setEasingCurve(QEasingCurve.Type.InCurve)

            def update_item_position(value, item=item):
                item.setPos(value)

            animation.valueChanged.connect(update_item_position)
            parallel_animations.addAnimation(animation)

        parallel_animations.finished.connect(parallel_animations.deleteLater)
        parallel_animations.start(QAbstractAnimation.DeleteWhenStopped)
        

    def item_moved(self, item):
        scene_rect = self.sceneRect()
        item_rect = item.sceneBoundingRect()

        # Check if the item is near any edge of the scene
        if item_rect.left() < scene_rect.left() + self.buffer:
            scene_rect.setLeft(scene_rect.left() - self.buffer)
        if item_rect.right() > scene_rect.right() - self.buffer:
            scene_rect.setRight(scene_rect.right() + self.buffer)
        if item_rect.top() < scene_rect.top() + self.buffer:
            scene_rect.setTop(scene_rect.top() - self.buffer)
        if item_rect.bottom() > scene_rect.bottom() - self.buffer:
            scene_rect.setBottom(scene_rect.bottom() + self.buffer)

        self.setSceneRect(scene_rect)

    def drawBackground(self, painter: QtGui.QPainter, rect: typing.Union[QtCore.QRectF, QtCore.QRect]) -> None:
        left = int(rect.left()) - (int(rect.left()) % GRIDSIZE[0])
        top = int(rect.top()) - (int(rect.top()) % GRIDSIZE[1])
        pen = painter.pen()
        pen.setColor(SettingsLoader.GridColor.color())
        painter.setPen(pen)

        lines = []
        for x in range(left, int(rect.right()), GRIDSIZE[0]):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), GRIDSIZE[1]):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        painter.drawLines(lines)

        return super().drawBackground(painter, rect)

    ''' Mouse Interactions '''

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        for item in self.selectedItems():
            self.item_moved(item)

    def dragEnterEvent(self, QGraphicsSceneDragDropEvent):
        QGraphicsSceneDragDropEvent.accept()

    def dragMoveEvent(self, QGraphicsSceneDragDropEvent):
        QGraphicsSceneDragDropEvent.accept()

    def buildBoundingRectFromSelectedItems(self):
        sourcerect = QRect(0,0,0,0)
        for item in self.selectedItems():
            sourcerect = sourcerect.united(item.sceneBoundingRect().toRect())
        return sourcerect
    

    @abstractmethod
    def saveItemsForCopy(self):
        pass

    def saveImageToClipboard(self, bounds : QRectF):
        
        pxmap = QPixmap(self.views()[0].grab(self.views()[0].mapFromScene(bounds).boundingRect()))
        
        #Objects.qapp.clipboard().setPixmap(pxmap)
        '''fname = os.path.join(objects.tmpdir, 'boink.png')
        pxmap.save(fname)'''


class DiagramPane(DiagramViewer):
    def __init__(self, parent=None):
        scene = DiagramScene()
        super().__init__(scene, parent)
        #self.OrganizeRequested.connect(lambda x: scene.arrange_tree())
        