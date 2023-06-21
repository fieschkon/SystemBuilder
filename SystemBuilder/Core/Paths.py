import os
import sys

from platformdirs import user_cache_dir, user_config_dir, user_data_dir, user_log_dir

from SystemBuilder.Utils.PathUtils import makeDir, respath



AppName = 'SystemBuilder'
Org = 'Bingus'

datadir = user_data_dir(AppName, Org)

tmpdir = user_cache_dir(AppName, Org)

logdir = user_log_dir(AppName, Org)

configdir = user_config_dir(AppName, Org)

configfile = f'{configdir}{os.sep}config.json'

resourcedir = respath("Resources")

plugindir = respath("Plugins")

makeDir(datadir)
makeDir(tmpdir)
makeDir(logdir)
makeDir(configdir)
makeDir(resourcedir)
makeDir(plugindir)