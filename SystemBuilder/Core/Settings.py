from enum import Enum
import inspect
import json
import logging
import os
from SystemBuilder.Utils.JsonUtils import json_decode, json_encode
from SystemBuilder.Utils.ThemingUtils import ThemedColor, getTheme
from SystemBuilder.Core.Paths import configfile, configdir
import qdarktheme
from PySide6.QtGui import QColor


stylesheet = None
palette = None


class SettingsLoader:
    # Logging
    MaxLoggingSize = 10485760

    # Runtime Editable
    winx = 200
    winy = 150
    maximized = False

    globalSettingsSizeX = 300
    globalSettingsSizeY = 200

    IconSize = (50, 50)

    # Theming
    themename = getTheme()

    # Icon Colors
    IconColor = ThemedColor(QColor(105,105,105), QColor(192,192,192)) #QColor(105,105,105)

    # Halo Color
    HaloColor = ThemedColor(QColor(9, 12, 9, 255), QColor(255, 255, 255, 255))

    CanvasColor = QColor(33, 33, 33, 255)
    GridColor = ThemedColor(QColor(211, 211, 211, 255) , QColor(47, 47, 47, 255))

    SelectColor = QColor(255, 223, 100, 255)

    def serializeSettings():
        attributes = inspect.getmembers(SettingsLoader, lambda a:not(inspect.isroutine(a)))
        serializedDict = {a[0] : a[1] for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))}
        return json_encode(serializedDict)

    def loadSettings(indict : dict):
        for key, value in indict.items():
            try:
                setattr(SettingsLoader, key, json_decode(value))
            except:
                if isinstance(value, dict):
                    if value['type'] == ThemedColor.__name__:
                        value = ThemedColor.fromDict(value)
                    elif value['type'] == QColor.__name__:
                        value = QColor(value['color'][0], value['color'][1], value['color'][2])

                setattr(SettingsLoader, key, value)

    def saveToFile(path=configfile):
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        with open(path, 'w') as f:
            f.write(SettingsLoader.serializeSettings())
            logging.info("Settings Saved.")

    def openFromFile(path=configfile):
        global stylesheet, palette
        SettingsLoader.loadSettings(dict(json.loads(open(path, 'r').read())))
        stylesheet = qdarktheme.load_stylesheet(SettingsLoader.themename)
        palette = qdarktheme.load_palette()

stylesheet = qdarktheme.load_stylesheet(SettingsLoader.themename)
palette = qdarktheme.load_palette()
