from app_mainwindow import *
from backend.sf_constructor import *
import logging
import sys


logging.basicConfig(format='%(levelname)s: %(message)s', level="WARNING")


if __name__ == '__main__':
    ctor = SFConstructor()

    app = AppMainWindow(sys.argv)

    app.exec()

    print("exit")
