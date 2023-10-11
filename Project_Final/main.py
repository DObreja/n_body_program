#############################################################
#               N_BODY PROBLEM PROGRAM                      #
# Author: David Obreja                                      #
# NOTE: Make sure you install the stuff in requirements.txt #
# This uses PySide2 in order to make Qt run for the program.#
# Make sure that is installed before running the program!   #
#############################################################


from main_window import MainWindow
from PySide2.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)  # Makes the application
    win = MainWindow()  # Sets to window
    win.resize(1280, 720)
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
