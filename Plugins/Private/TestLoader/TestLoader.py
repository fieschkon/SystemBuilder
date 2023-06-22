from SystemBuilder.Core.API import *

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QBrush, QLinearGradient, QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsSceneHoverEvent, QLabel, QGraphicsScene, QGraphicsView
from PySide6.QtCore import QPointF, QRectF, QLineF
from PySide6.QtGui import QTransform

from SystemBuilder.Visual.Graphics.GraphicsItems.Chips.Component import Component
from SystemBuilder.Visual.Graphics.Scenes import DiagramPane

class DemonstrationSetupPlugin(PluginBase):
    name : str = 'Test Loader'
    author : str = ''
    description : str = 'Plugin for loading a test setup'
    version : str = '1'

    def dataInitialize(*args, **kwargs):
        print("Data initialized")

    def windowInitialize(*args, **kwargs):
        print("Creating test window")
        onWindowReady()

    def run(*args, **kwargs):
        print("Running")

    def onexit(self, *args, **kwargs):
        print("Exiting") 


def onWindowReady():
    sc = DiagramPane()
    rectItem = Component(200, 200, "Resources\Boxr.svg")
    sc.scene().addItem(rectItem)

    rectItem2 = Component(200, 200, "Resources\Boxr.svg")
    sc.scene().addItem(rectItem)
    rectItem2.setParentItem(rectItem)

    Window.addDocumentPane(sc, "Test Window")