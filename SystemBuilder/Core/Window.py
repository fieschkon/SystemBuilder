import json
import logging
import os
import platform
import pprint
import subprocess
import typing
from enum import Enum
from types import NoneType
from SystemBuilder.Core.Extensions import PluginLoader
from SystemBuilder.Core.Settings import SettingsLoader
from SystemBuilder.Core import API
from SystemBuilder.Visual.Widgets.DetachableTabWidget import DetachableTabWidget

import qdarktheme
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl, Signal, Slot)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QFontMetrics, QGradient,
                           QIcon, QImage, QKeySequence, QLinearGradient,
                           QMatrix3x3, QPainter, QPainterPath, QPalette, QPen,
                           QPixmap, QRadialGradient, QRegion, QTextCursor,
                           QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox,
                               QComboBox, QDialog, QDialogButtonBox,
                               QDockWidget, QFrame, QGridLayout, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMainWindow, QMenu, QMenuBar,
                               QPushButton, QScrollArea, QSizePolicy,
                               QSpacerItem, QStackedWidget, QStatusBar,
                               QTabWidget, QTextEdit, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

class Ribbon(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        # Create the vertical layout
        layout = QHBoxLayout(self)

        # Create the list widget and add items to it
        self.list_widget = QListWidget(self)
        self.list_widget.setFixedWidth(50)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setIconSize(QSize(SettingsLoader.IconSize[0], SettingsLoader.IconSize[1]))
        
        #self.list_widget.currentItemChanged.connect(self.handle_item_changed)
        self.current = None
        self.list_widget.itemClicked.connect(self.item_clicked)
        
        self.list_widget.setFocusPolicy(Qt.NoFocus)

        # Set the frame of the list widget to invisible
        self.list_widget.setFrameStyle(QListWidget.NoFrame)

        # Create the right widget with a widget switcher and a placeholder widget
        self.right_widget = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_widget)
        self.switcher = QStackedWidget (self.right_widget)
        self.right_layout.addWidget(self.switcher)
        self.right_layout.addWidget(QWidget(self.right_widget))
        self.right_widget.hide()

        # Add the widgets to the layout
        layout.addWidget(self.list_widget)
        layout.addWidget(self.right_widget)

        # Set the layout and properties of the sidebar widget
        self.setLayout(layout)

        self.bindAPI()

    def bindAPI(self):
        API.Ribbon.addPane = self.addPane

    def addPane(self, icon: QIcon, widget: QWidget):
        # Create a label for the icon and center it
        label = QLabel(self.list_widget)
        label.setAlignment(Qt.AlignCenter)
        if isinstance(icon, QPixmap):
            label.setPixmap(icon)
        else:
            label.setPixmap(icon.pixmap(QSize(SettingsLoader.IconSize[0], SettingsLoader.IconSize[1])))

        # Create the list item with the label as its widget
        item = QListWidgetItem("", self.list_widget)
        item.setSizeHint(QSize(SettingsLoader.IconSize[0], SettingsLoader.IconSize[1]))
        item.setBackground(Qt.transparent)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setSizeHint(QSize(SettingsLoader.IconSize[0], SettingsLoader.IconSize[1]))
        item.widget = widget
        item.setWhatsThis(widget.toolTip())
        item.setStatusTip(widget.toolTip())
        item.setToolTip(widget.toolTip())

        self.list_widget.setItemWidget(item, label)
        self.switcher.addWidget(widget)
        widget.hide()

    def item_clicked(self, clickeditem : QListWidgetItem):
        from SystemBuilder.Core import Settings
        from SystemBuilder.Core.Settings import SettingsLoader
        self.previous = self.current
        self.current = clickeditem

        if self.previous is self.current and not self.right_widget.isHidden():
            self.previous.setBackground(Qt.transparent)
            self.right_widget.hide()
            self.previous.setSelected(False)
            self.parent().parent().setMaximumWidth(SettingsLoader.IconSize[0]+20)
            return

        if self.current:
            widget = self.current.widget
            widget.show()
            self.switcher.setCurrentWidget(widget)
            self.current.setSelected(True)
            if self.previous and self.previous is not self.current:
                self.previous.setSelected(False)
                self.previous.setBackground(Qt.transparent)
            self.right_widget.show()
            self.parent().parent().setMaximumWidth(10000)
        elif self.previous:
            self.previous.widget.hide()
            self.right_widget.hide()
            
        if self.current:
            self.current.setBackground(Settings.palette.midlight().color())
        elif self.previous:
            self.previous.setBackground(Qt.transparent)

class Window(QMainWindow):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        # Menu Items
        self.TopLevelMenuItems : dict[str : QMenu] = {}
        self.MenuItems : dict[str : QAction] = {}

        self.setupUi()
        self.setupTopLevelMenuItems()
        logging.info('Main Window Loaded.')
        self.bindAPI()
        logging.info('Window API Bound.')
        

    def closeEvent(self, event) -> None:

        SettingsLoader.maximized = self.isMaximized()
        if not SettingsLoader.maximized:
            window_size = self.size()
            SettingsLoader.winx = window_size.width()
            SettingsLoader.winy = window_size.height()

        return super().closeEvent(event)


    def setupUi(self):
        

        self.resize(SettingsLoader.winx, SettingsLoader.winy)
        self.CentralWidget = QWidget(self)
        self.CentralWidgetLayout = QVBoxLayout(self.CentralWidget)
        self.CentralWidgetLayout.setSpacing(0)
        self.CentralWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.CentralWidgetStack = QStackedWidget(self.CentralWidget)
        self.EmptyDisplayWidget = QLabel('No object selected')
        self.CentralWidgetStack.addWidget(self.EmptyDisplayWidget)

        self.DocumentTabsWidget = DetachableTabWidget(self.CentralWidget)

        self.CentralWidgetStack.addWidget(self.DocumentTabsWidget)

        self.CentralWidgetLayout.addWidget(self.CentralWidgetStack)

        self.setCentralWidget(self.CentralWidget)
        self.MenuBar = QMenuBar(self)
        self.MenuBar.setGeometry(QRect(0, 0, 800, 21))

        self.setMenuBar(self.MenuBar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.ExplorerDockWidget = QDockWidget(self)
        self.ExplorerDockWidget.setAutoFillBackground(False)
        self.ExplorerDockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.ExplorerDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.ExplorerDockWidget.setWindowTitle(u"Explorer")
        self.ExplorerDockWidgetContents = QWidget()
        self.ExplorerDockWidgetContentsLayout = QVBoxLayout(self.ExplorerDockWidgetContents)
        self.ExplorerDockWidgetContentsLayout.setSpacing(0)
        self.ExplorerDockWidgetContentsLayout.setContentsMargins(0, 0, 0, 0)
        self.REPLACEME_ExplorerPanel = Ribbon(self.ExplorerDockWidgetContents)

        self.ExplorerDockWidgetContentsLayout.addWidget(self.REPLACEME_ExplorerPanel)

        self.ExplorerDockWidget.setWidget(self.ExplorerDockWidgetContents)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.ExplorerDockWidget)
        self.ParameterDockWidget = QDockWidget(self)
        self.ParameterDockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.ParameterDockWidget.setWindowTitle(u"Details")
        self.ParameterDockWidgetContents = QWidget()
        self.ParameterDockWidgetContentsLayout = QVBoxLayout(self.ParameterDockWidgetContents)
        self.ParameterDockWidgetContentsLayout.setSpacing(0)
        self.ParameterDockWidgetContentsLayout.setContentsMargins(0, 0, 0, 0)

        self.ParameterDockWidget.setWidget(self.ParameterDockWidgetContents)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ParameterDockWidget)

        self.CentralWidgetStack.setCurrentIndex(0)

    def bindAPI(self):
        API.Window.addDocumentPane = self.addDocumentPane
        API.Window.addTopLevelMenu = self.addTopLevelMenu
        API.Window.getTopLevelMenu = self.getTopLevelMenu
        

    def addDocumentPane(self, widget : QWidget, tabname):
        '''
        Adds a document pane to the tabbed widget.

        Args:
            widget (QWidget): Widget to add
        '''
        self.DocumentTabsWidget.addTab(widget, tabname)
        if self.DocumentTabsWidget.count() == 0:
            self.CentralWidgetStack.setCurrentIndex(0)
        else:
            self.CentralWidgetStack.setCurrentIndex(1)


    '''
    Menu Item Generation
    '''

    def getTopLevelMenu(self, name : str) -> QMenu:
        '''
        Gets the menu at the top of the window by name.

        Args:
            name (str): Name of menu. e.g. 'File'

        Returns:
            QMenu: The menu
        '''
        return self.TopLevelMenuItems.get(name, None)

    def addTopLevelMenu(self, name : str) -> QMenu:
        '''
        Add an empty menu to the menubar.

        Args:
            name (str): Name of the menu

        Returns:
            QMenu: Menu created
        '''
        menu = self.MenuBar.addMenu(name)
        self.TopLevelMenuItems[name] = menu
        return menu

    def setupTopLevelMenuItems(self):
        # Define default menu items
        self.addTopLevelMenu(u"File")
        self.addTopLevelMenu(u"Edit")
        self.addTopLevelMenu(u"View")

