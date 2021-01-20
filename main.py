# coding=utf-8

import sys
from PyQt5.QtWidgets import QApplication
import multiprocessing

from main_interface import MainInterface

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    w = MainInterface.from_yaml('config.yaml')
    w.show()
    sys.exit(app.exec_())


# pyinstaller -w  main.py