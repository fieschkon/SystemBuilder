import builtins
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import SystemBuilder

from SystemBuilder.Core import Paths
from SystemBuilder.Core import Settings
from SystemBuilder.Core.Extensions import PluginLoader
from SystemBuilder.Core.Settings import SettingsLoader
from SystemBuilder.Core import Shared
from SystemBuilder.Core.Window import Window
from SystemBuilder.Visual.Launcher import StartupLauncher

# Initialize Logging

root = logging.getLogger()
root.handlers.clear()

if getattr(sys, "frozen", False):
    root.setLevel(logging.INFO)
else:
    root.setLevel(logging.DEBUG)

stformat = '%(asctime)s %(levelname)s %(module)s.%(funcName)s(%(lineno)d) %(message)s'
logformat = logging.Formatter(stformat)

FileLogHandler = RotatingFileHandler(os.path.join(Paths.logdir, f'{datetime.now().strftime("%H-%M-%S")}.log'), mode='a', maxBytes=5*1024*1024, 
                                backupCount=2, encoding=None, delay=0)

FileLogHandler.setFormatter(logformat)
FileLogHandler.setLevel(logging.INFO)
root.addHandler(FileLogHandler)

ConsoleHandler = logging.StreamHandler(sys.stdout)
ConsoleHandler.setLevel(logging.DEBUG)
ConsoleHandler.setFormatter(logformat)
root.addHandler(ConsoleHandler)
builtins.print = logging.info

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    else:
        msg = f"Uncaught Exception:\n{exc_traceback}"
        logging.getLogger().critical(msg, exc_info=(exc_type, exc_value, exc_traceback))
        exit(2)
    
sys.excepthook = handle_exception


def run(args):
    def openWindow():
        PluginLoader.signalWindowReady()
        w.show()
        if SettingsLoader.maximized:
            w.setWindowState(Qt.WindowState.WindowMaximized)
    """Initialize everything and run the application."""

    logging.debug("Main process PID: {}".format(os.getpid()))
    
    if not os.path.isfile(Paths.configfile):
        logging.info('Creating config file...')
        SettingsLoader.saveToFile()

    Shared.qapp = Application(args)

    Shared.qapp.setOrganizationName(Paths.Org)
    Shared.qapp.setApplicationName(Paths.AppName)
    
    Shared.qapp.setApplicationVersion(SystemBuilder.__version__)

    # Apply Settings
    SettingsLoader.openFromFile()
    
    res = Shared.qapp.primaryScreen().availableSize().toTuple()
    SettingsLoader.winx = min(SettingsLoader.winx, res[0])
    SettingsLoader.winy = min(SettingsLoader.winy, res[1])


    #launcher = StartupLauncher()
    #launcher.show()
    #w = Window()
    #w.show()

    # Verify another instance isn't open
    shared_memory = QSharedMemory("SystemBuilder")

    if shared_memory.create(1) is False:
        # If the shared memory segment already exists, another instance is running
        logging.critical("Another instance already open, abort")
        sys.exit(0)

    launcher = StartupLauncher()
    w = Window()
    launcher.operationsFinished.connect(openWindow)
    launcher.show()

    ret =  Shared.qapp.exec()

    return ret

def shutdown(args):
    logging.info("Saving Settings...")
    SettingsLoader.saveToFile()
    
class Application(QApplication):

    def __init__(self, args):
        self._last_focus_object = None

        super().__init__(args)

        self.launch_time = datetime.now()

        self.setStyleSheet(Settings.stylesheet)
        

    def event(self, e):
        return super().event(e)