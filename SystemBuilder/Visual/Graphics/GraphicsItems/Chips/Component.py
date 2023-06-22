from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QBrush, QLinearGradient, QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsSceneHoverEvent
from PySide6.QtCore import QPointF, QRectF, QLineF
from PySide6.QtGui import QTransform
from SystemBuilder.Core.Settings import SettingsLoader

from SystemBuilder.Utils.ThemingUtils import ThemedColor

class Component(QGraphicsItem):
    def __init__(self, width, height, image=None, parent=None):
        super(Component, self).__init__(parent)
        self._width = width
        self._height = height
        self._image = image
        self.underlyingsize = QRectF(0, 0, self._width, self._height)
        self.previewpos = None
        self.basecolor = ThemedColor(QColor(128, 128, 128, 128), QColor(25, 21, 22, 128))

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        self.hovered = False

        if image:
            pixmap = QPixmap(image).scaled(self._width, self._height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._pixmapItem = QGraphicsPixmapItem(pixmap, self)
            self._pixmapItem.setPos(0, 0)

    def boundingRect(self):
        return self.underlyingsize.adjusted(-40, -40, 40, 40)
    
    def setRect(self, rect : QRectF):
        self.underlyingsize = rect

    def paint(self, painter, option, widget=None):
        # Draw background highlight
        if self.isSelected():
            pen = painter.pen()
            selectionoutline = QPainterPath()
            pen.setColor(SettingsLoader.SelectColor.color())
            selectionoutline.addRoundedRect(self.underlyingsize, 10, 10)
            pen.setWidth(6)
            painter.setPen(pen)
            painter.drawPath(selectionoutline)
        # Draw the rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self._width, self._height), 10, 10)
        painter.setPen(Qt.NoPen)
        
        # Draw the base color with transparency to give a glassy look
        baseColor = self.basecolor.color()
        painter.setBrush(QBrush(baseColor))
        painter.drawPath(path)
        
        # Add a gradient to give a shiny glassy look
        gradient = QLinearGradient(0, 0, 0, self._height)
        gradient.setColorAt(0, QColor(255, 255, 255, 127))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        if self.hovered and self.previewpos:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(self.previewpos, 10, 10)

    def mousePressEvent(self, event):
        self.setSelected(True)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event) -> None:
        self.hovered = True
        self.update()
        return super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event) -> None:
        self.hovered = False
        self.update()
        return super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        closest_point, transform = self.closest_perimeter_point(event.pos())
        self.previewpos = closest_point
        self.previewtransform = transform
        self.update()
        return super().hoverMoveEvent(event)

    def closest_perimeter_point(self, point: QPointF):
        rect = self.underlyingsize
        # Create a line from the center of the rectangle to the given point
        line = QLineF(rect.center(), point)

        # Create four lines representing the edges of the rectangle
        edges = [
            (QLineF(rect.topLeft(), rect.topRight()), 180),
            (QLineF(rect.topRight(), rect.bottomRight()), -90),
            (QLineF(rect.bottomRight(), rect.bottomLeft()), 0),
            (QLineF(rect.bottomLeft(), rect.topLeft()), 90),
        ]

        for edge, rotation in edges:
            # If the line intersects with an edge, return the intersection point and transformation
            intersection_type, intersection_point = edge.intersects(line)
            if intersection_type == QLineF.IntersectionType.BoundedIntersection:
                transform = QTransform()
                transform.rotate(rotation)
                return intersection_point, transform

        return None, None



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

    app = QApplication([])
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    rectItem = Component(200, 200, "Resources\Boxr.svg")
    scene.addItem(rectItem)
    view.show()
    app.exec_()
