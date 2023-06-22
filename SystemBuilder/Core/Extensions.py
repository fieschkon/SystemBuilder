from importlib import import_module, reload
from inspect import isclass
import logging
import os
import subprocess
import sys
from time import sleep
from SystemBuilder.Core.API import PluginBase
from SystemBuilder.Core.Callback import Delegate
from SystemBuilder.Utils import ExtensionUtils
from SystemBuilder.Core import Paths

class PluginWrapper():
    def __init__(self, pluginbase : PluginBase, module) -> None:
        self.module = module
        self.plugin : PluginBase = pluginbase
    
    def run(self, *args, **kwargs):
        return self.plugin.run(*args, **kwargs)

    def reload(self):
        reload(self.module)
        for attribute_name in dir(self.module):
            attribute = getattr(self.module, attribute_name)

            if isclass(attribute) and issubclass(attribute, PluginBase):
                self.plugin = attribute
                break

    def dataInitialize(self, *args, **kwargs):
        return self.plugin.dataInitialize(*args, **kwargs)

    def windowInitialize(self, *args, **kwargs):
        return self.plugin.windowInitialize(*args, **kwargs)

    def onexit(self, *args, **kwargs):
        return self.plugin.onexit(*args, **kwargs)

class PluginLoader:

    onProgress = Delegate(int, int)
    plugins = []

    def loadPlugins():
        PluginLoader.plugins.clear()
        # Find requirements.txt
        requirements = PluginLoader.discoverDependencies(Paths.plugindir)
        # Find modules
        modules = PluginLoader.getModules()

        totalsteps = len(modules) + len(requirements)
        # Install dependencies
        step = 0
        
        for requirement in requirements:
            PluginLoader.onProgress.emit(step, totalsteps)
            PluginLoader.installDependency(requirement)
            step += 1

        # Extract modules
        for module_name in modules:
            PluginLoader.onProgress.emit(step, totalsteps)
            p = PluginLoader.extractPluginFromModule(module_name)
            step += 1
            if p:
                PluginLoader.plugins.append(p)
                p.dataInitialize()

    def discoverDependencies(directory):
        requirements = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == 'requirements.txt':
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        readrequirements = f.read().splitlines()
                        requirements.extend(readrequirements)
        return requirements

    def extractPluginFromModule(moduleName):
        logging.info(f'Attempting import of {moduleName} into context...')
        # import the module and iterate through its attributes
        try:
            module = import_module(f"{moduleName}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                if isclass(attribute) and issubclass(attribute, PluginBase):
                    #globals()[attribute_name] = attribute
                    logging.info(f'Plugin found in {moduleName}')
                    return PluginWrapper(attribute, module)
        except Exception as e:
            logging.error(f'Error loading {moduleName}:\n{e}')
   
    def getModules():
        return [module_name for (_, module_name, _) in ExtensionUtils.iter_modules_recursive([Paths.plugindir], relativeto=os.getcwd())]

    
    def installDependency(pipname):
        logging.info(f'Installing {pipname}...')
        pipcode = subprocess.check_call([sys.executable, '-m', 'pip', 'install', pipname])
        match pipcode:
            case 0: #success
                logging.info(f'{pipname} installed successfully.')
            case 1: #error
                logging.critical(f'{pipname} errored on install.')
            case 2: #unknown error
                logging.critical(f'{pipname} errored on install.')
            case 23: #no matches found
                logging.critical(f'{pipname} could not be resolved.')
            case _:
                logging.critical(f'{pipname} could not be installed due to unknown pip error.')

    def signalWindowReady():
        for plugin in PluginLoader.plugins:
            logging.info(f"Signaling window ready to {plugin.plugin.name}")
            plugin.plugin.windowInitialize()