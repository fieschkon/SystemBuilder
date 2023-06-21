import inspect

class PluginBase:

    name: str = ""
    author: str = ""
    description: str = ""
    version: str = ""
    requires: list[str] = []

    def dataInitialize(*args, **kwargs):
        pass

    def windowInitialize(*args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass

    def onexit(self, *args, **kwargs):
        pass


class NotBoundException(Exception):
    def __init__(self, error : str = None) -> None:
        frame = inspect.currentframe().f_back.f_back
        # Get the name of the calling function
        caller_name = frame.f_code.co_name
        # Get the filename where the calling function is defined
        filename = frame.f_code.co_filename
        # Get the line number where the calling function is called
        line_number = frame.f_lineno
        if not error:
            error = f"This method is not yet bound. Perhaps it is being called at the wrong time?"
        error += f' Called from {caller_name}:{line_number} in {filename}'
        super().__init__(error)

class Ribbon:
    def addPane(icon, widget):
        '''
        Adds a pane to the ribbon widget.

        Args:
            icon (QIcon): The icon for the widget
            widget (QWidget): The widget to display
        '''        
        raise NotBoundException()
    
class Window:
    def addDocumentPane(widget, tabname : str):
        '''
        Adds a document pane to the tabbed widget.

        Args:
            widget (QWidget): Widget to add
            tabname (str): Tab name
        '''
        raise NotBoundException()
    
    def getTopLevelMenu(name : str):
        '''
        Gets the menu at the top of the window by name.

        Args:
            name (str): Name of menu. e.g. 'File'

        Returns:
            QMenu: The menu
        '''
        raise NotBoundException()

    def addTopLevelMenu(name : str):
        '''
        Add an empty menu to the menubar.

        Args:
            name (str): Name of the menu

        Returns:
            QMenu: Menu created
        '''
        raise NotBoundException()