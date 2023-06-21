import logging
import os
import sys


def respath(relative_path):
    """
    Get the absolute path to a resource file.

    This function works both during development and when the code is bundled using PyInstaller.

    Args:
        relative_path (str): The relative path to the resource file.

    Returns:
        str: The absolute path to the resource file.

    Raises:
        None.

    """
    try:
        # Check if running in a PyInstaller environment
        base_path = sys._MEIPASS
    except Exception:
        # If not running in a PyInstaller environment, use the current working directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def makeDir(path):
    """
    Create a new directory at the provided path.
    
    Args:
        path (str): The absolute or relative path to create a new directory.

    Raises:
        FileExistsError: If the directory already exists.
    """
    try:
        os.makedirs(path)
        logging.debug(f"{path} created.")  # Log the creation of the directory
    except FileExistsError:
        logging.debug(f"{path} pre-exists.")  # Log if the directory already exists


def getFilesWithExtension(paths: list, extension: str = ".json", recursive=False):
    """
    Get all the files with a specific extension from the provided paths.

    Args:
        paths (list): A list of absolute or relative paths to search for files.
        extension (str, optional): The extension of the files to search. Defaults to ".json".
        recursive (bool, optional): If True, perform a recursive search. Defaults to False.

    Returns:
        list: A list of absolute paths to the files found.
    """
    def listdirs(rootdir):
        """List all directories in a given directory."""
        paths = []
        for it in os.scandir(rootdir):
            if it.is_dir():
                paths.append(it.path)
                paths += listdirs(it)
        return paths

    files = []
    if recursive:
        [paths.__iadd__(listdirs(root)) for root in paths]  # Add all sub-directories to the list of paths
    for path in paths:
        for file in os.listdir(path):
            if file.endswith(extension):  # Check if the file has the correct extension
                files.append(os.path.join(path, file))  # Add the file to the list of files
    return files


def getFiles(paths: list, recursive=False):
    """
    Get all the files from the provided paths.

    Args:
        paths (list): A list of absolute or relative paths to search for files.
        recursive (bool, optional): If True, perform a recursive search. Defaults to False.

    Returns:
        list: A list of absolute paths to the files found.
    """
    def listdirs(rootdir):
        """List all directories in a given directory."""
        paths = []
        for it in os.scandir(rootdir):
            if it.is_dir():
                paths.append(it.path)
                paths += listdirs(it)
        return paths

    files = []
    if recursive:
        [paths.__iadd__(listdirs(root)) for root in paths]  # Add all sub-directories to the list of paths
    for path in paths:
        for file in os.listdir(path):  # Check every file in the directory
            files.append(os.path.join(path, file))  # Add the file to the list of files
    return files