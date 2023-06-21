import platform
import subprocess
from PySide6.QtGui import QColor

def getTheme():
    match platform.system():
        case "Darwin":
            cmd = "defaults read -g AppleInterfaceStyle"
            p = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )
            return "dark" if bool(p.communicate()[0]) else "light"
        case "Windows":
            try:
                import winreg
            except ImportError:
                return "light"
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            reg_keypath = (
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            try:
                reg_key = winreg.OpenKey(registry, reg_keypath)
            except FileNotFoundError:
                return "light"

            for i in range(1024):
                try:
                    value_name, value, _ = winreg.EnumValue(reg_key, i)
                    if value_name == "AppsUseLightTheme":
                        return "dark" if value == 0 else "light"
                except OSError:
                    break
            return "light"

class ThemedColor():

    DEFAULTCOLOR = QColor(255, 0, 0, 255)

    def __init__(self, lightColor : QColor = None, darkColor: QColor = None) -> None:
        self.lightColor = lightColor
        self.darkColor = darkColor

    def color(self, themename=getTheme()):
        match themename:
            case 'dark':
                return self.darkColor
            case 'light':
                return self.lightColor
            case 'auto':
                return self.color(getTheme())
            
    def toDict(self):
        return {
            'type' : self.__class__.__name__,
            'light' : (self.lightColor.red(), self.lightColor.green(), self.lightColor.blue()),
            'dark' : (self.darkColor.red(), self.darkColor.green(), self.darkColor.blue())
        }
    
    def fromDict(indict):
        return ThemedColor(QColor(indict['light'][0], indict['light'][1], indict['light'][2]), QColor(indict['dark'][0], indict['dark'][1], indict['dark'][2]))