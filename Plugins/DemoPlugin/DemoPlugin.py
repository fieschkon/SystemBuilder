from SystemBuilder.Core.API import PluginBase


class ExamplePlugin(PluginBase):
    name : str = 'Example Plugin'
    author : str = ''
    description : str = ''
    version : str = '1'

    def dataInitialize(*args, **kwargs):
        print("Demo Plugin Initialized!") 

    def windowInitialize(*args, **kwargs):
        print("Demo Plugin ready to interact with window!") 

    def run(*args, **kwargs):
        print(args, kwargs)

    def onexit(self, *args, **kwargs):
        print("Demo Plugin shutting down!") 