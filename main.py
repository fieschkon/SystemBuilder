import sys

import SystemBuilder.SystemBuilder
from SystemBuilder import App

if __name__ == '__main__':
    ecode = SystemBuilder.SystemBuilder.main()
    App.shutdown(ecode)
    sys.exit(ecode)