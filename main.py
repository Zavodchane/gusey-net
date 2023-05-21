from PyQt6.QtWidgets import QStyleFactory, QApplication

from windows.MainWindow import MainWindow
# from windows.statistic_db import create_table

import sys, os


if "." not in sys.path:
    sys.path.append(".")


def setupFolders():
    '''
    Подготовка папки результатов при ее отсутствии
    '''
    try: 
        os.mkdir("tables")
        os.mkdir("results")
    except FileExistsError: pass

# create_table()
setupFolders()

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("Fusion"))

window = MainWindow()
window.showMaximized()

app.exec()