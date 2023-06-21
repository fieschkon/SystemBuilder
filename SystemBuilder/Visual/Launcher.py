import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Optional

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                               QProgressBar, QSizePolicy, QVBoxLayout, QWidget)

from SystemBuilder.Core.Callback import Delegate
from SystemBuilder.Core import Paths
from SystemBuilder.Core.Extensions import PluginLoader
from SystemBuilder.Utils import PathUtils
from SystemBuilder.Core.Settings import SettingsLoader
from SystemBuilder.Core import Shared
from SystemBuilder.Visual.Widgets.LogarithmicProgressBar import LogarithmicProgressBar


class StartupLauncher(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute( Qt.WA_DeleteOnClose, True )
        self.operationsFinished = Delegate()
        self.currentstep = 0
        self.setupUi()
        
    def finished(self):
        self.operationsFinished.emit()
        self.close()

    def show(self) -> None:
        super().show()
        self.startupOperations()
        return

    def setupUi(self):
        self.resize(578, 206)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.TitleLabel = QLabel(self.centralwidget)
        self.TitleLabel.setObjectName(u"TitleLabel")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(48)
        font.setBold(True)
        self.TitleLabel.setFont(font)

        self.horizontalLayout.addWidget(self.TitleLabel)

        self.ImageBox = QLabel(self.centralwidget)
        self.ImageBox.setObjectName(u"ImageBox")
        self.ImageBox.setMaximumSize(QSize(150, 150))

        self.horizontalLayout.addWidget(self.ImageBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.ProgressBar = LogarithmicProgressBar(self.centralwidget)
        self.ProgressBar.setObjectName(u"ProgressBar")
        self.ProgressBar.setMaximumSize(QSize(16777215, 10))
        self.ProgressBar.setValue(24)
        self.ProgressBar.setTextVisible(False)
        self.ProgressBar.setOrientation(Qt.Horizontal)
        self.ProgressBar.setInvertedAppearance(False)

        self.verticalLayout.addWidget(self.ProgressBar)

        self.setCentralWidget(self.centralwidget)
        self.TitleLabel.setText("SysBuilder")
        px = QIcon("Resources\Boxr.svg").pixmap(QSize(150, 150))
        px = px.scaled(QSize(150, 150), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.ImageBox.setPixmap(px)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def startupOperations(self):
        def onNewProgress(current, total):
            self.ProgressBar.setMaximum(total)
            self.ProgressBar.setValue(current)
            Shared.qapp.processEvents()
        # Collect Maximum Steps
        PluginLoader.onProgress.connect(onNewProgress)
        PluginLoader.loadPlugins()
        # Done
        self.finished()


    def cleanLogs(self):
        size = 0
        for path, dirs, files in os.walk(Paths.logdir):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        if size > SettingsLoader.MaxLoggingSize:
            logging.info(f'Log directory exceeds {SettingsLoader.MaxLoggingSize}, looking for cleaning opportunities...')
            logfiles = PathUtils.getFilesWithExtension([], extension='.log')
            for logfile in logfiles:
                logtime = datetime.strptime(Path(logfile).stem, "%H-%M-%S")
                delta = datetime.now() - logtime
                if delta.days > 5:
                    logging.info(f'Found old log {logfile} from {delta.days} days ago. Deleting...')
                    os.remove(logfile)