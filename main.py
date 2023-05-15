from PyQt6.QtWidgets import QStyleFactory, QApplication

from windows.MainWindow import MainWindow

import sys, os

sys.path.append(".")


def setupFolders():
    try: os.mkdir("results")
    except FileExistsError: pass

setupFolders()

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("Fusion"))

window = MainWindow()
window.showMaximized()

app.exec()