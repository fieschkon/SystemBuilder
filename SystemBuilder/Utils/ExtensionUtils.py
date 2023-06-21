from itertools import chain
import os
from pkgutil import iter_modules


def iter_modules_recursive(paths: list[str], relativeto=None):
    def listdirs(rootdir):
        paths = []
        for it in os.scandir(rootdir):
            if it.is_dir():
                paths.append(it.path)
                paths += listdirs(it)
        return paths

    directoriesToScan = [
        item for sublist in [listdirs(path) for path in paths] for item in sublist
    ]
    directoriesToScan += paths

    moduleinfo = iter(())
    for directory in directoriesToScan:
        if relativeto != None:
            directory = os.path.relpath(directory, relativeto)
        moduleinfo = chain(
            moduleinfo,
            iter_modules([directory], str(directory.replace(os.sep, ".") + ".")),
        )

    return moduleinfo