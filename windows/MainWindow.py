from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QHBoxLayout,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QScrollArea,
    QTextBrowser,
    QLabel,
    QSlider
)

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import os

from constants.paths import RESULT_PATH
from widgets.ImageBrowser import ImageBrowser

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationTool
from matplotlib.figure import Figure

def loadPaths(startpath: str, tree) -> None:
    for elem in os.listdir(startpath):
        elemPath = startpath + "/" + elem
        parentalItem = QTreeWidgetItem(tree, [os.path.basename(elem)])

        if os.path.isdir(elemPath):
            loadPaths(elemPath, parentalItem)
            parentalItem.setIcon(0, QIcon("assets\open-folder.png"))
        else:
            parentalItem.setIcon(0, QIcon("assets\processing.png"))


def getItemFullPath(item : QTreeWidgetItem):
    out = item.text(0)

    if item.parent():
        out = getItemFullPath(item.parent()) + "/" + out
    else:
        out =  "results/" + out

    return out


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.initUi()


    def initUi(self):
        self.setWindowTitle("гуся.net")
        self.setWindowIcon(QIcon("assets/swan.png"))

        screen = QApplication.primaryScreen()
        screenSize = screen.size()

        self.windowWidth  = screenSize.width()
        self.windowHeight = screenSize.height()

        print(self.windowHeight, self.windowWidth)

        self.primaryLayout   = QHBoxLayout()
        self.firstColLayout  = QVBoxLayout()
        self.secondColLayout = QVBoxLayout()
        self.thirdColLayout  = QVBoxLayout()

        self.initResultsAndControls()
        self.initImageBrowser()
        self.initGraphsAndInfo()

        self.secondColLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.firstColLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.primaryLayout.addLayout(self.firstColLayout)
        self.primaryLayout.addLayout(self.secondColLayout)
        self.primaryLayout.addLayout(self.thirdColLayout)

        self.container = QWidget()
        self.container.setLayout(self.primaryLayout)

        self.setCentralWidget(self.container)


    def initResultsAndControls(self):
        self.resultFileTree = QTreeWidget()
        self.resultFileTree.setHeaderLabel("Results")
        self.resultFileTree.setMaximumWidth(int(self.windowWidth / 5))
        self.resultFileTree.setMinimumWidth(int(self.windowWidth / 6))
        self.resultFileTree.setMaximumHeight(int(self.windowHeight / 2))
        self.resultFileTree.itemClicked.connect(self.treeItemClicked)

        loadPaths(startpath=RESULT_PATH, tree=self.resultFileTree)

        self.sliderLayout = QHBoxLayout()

        self.detectionSliderLabel = QLabel("Процент уверенности")
        self.detectionSliderLabel.setMaximumHeight(15)
        self.detectionSliderLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.detectionPercentLabel = QLabel("1%")
        self.detectionPercentLabel.setMaximumWidth(30)
        self.detectionPercentLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.detectionPercentSlider = QSlider(Qt.Orientation.Horizontal)
        self.detectionPercentSlider.setMaximumWidth(int(self.windowWidth / 5) - 35)
        self.detectionPercentSlider.setRange(1, 100)
        self.detectionPercentSlider.setSingleStep(1)
        self.detectionPercentSlider.valueChanged.connect(self.onSliderValueChange)

        self.sliderLayout.addWidget(self.detectionPercentLabel)
        self.sliderLayout.addWidget(self.detectionPercentSlider)

        self.firstColLayout.addWidget(self.resultFileTree)
        self.firstColLayout.addWidget(self.detectionSliderLabel)
        self.firstColLayout.addLayout(self.sliderLayout)


    def onSliderValueChange(self):
        self.detectionPercentLabel.setText(str(self.sender().value()) + "%")


    def initImageBrowser(self):
        self.imageBrowser = ImageBrowser()
        self.imageBrowser.updatePixmap(None)
        self.imageBrowser.setMaximumWidth(int(self.windowWidth / 2))

        self.secondColLayout.addWidget(self.imageBrowser, alignment=Qt.AlignmentFlag.AlignTop)


    def initGraphsAndInfo(self):
        self.graphsAndInfoScroll = QScrollArea()
        self.graphsAndInfoScroll.setWidgetResizable(True)
        self.graphsAndInfoScroll.setMaximumWidth(int(self.windowWidth / 3.5))

        self.figure  = Figure(figsize=(4, 6))
        self.canvas  = FigureCanvas(self.figure)

        self.figure.subplots_adjust(top = 0.98, bottom=0.0, right = 0.98, left = 0.11)

        self.plotPlaceholderData()

        self.placeholderInfo = QTextBrowser()
        self.placeholderInfo.setMaximumWidth(int(self.windowWidth / 3.5) - 20)
        self.placeholderInfo.setText("Очень важная информация о лебедях и возможно гусях))")

        self.GIContainer = QWidget()
        self.GIContainerLayout = QVBoxLayout()
        self.GIContainerLayout.addWidget(self.canvas)
        self.GIContainerLayout.addWidget(self.placeholderInfo )

        self.GIContainer.setLayout(self.GIContainerLayout)
        
        self.graphsAndInfoScroll.setWidget(self.GIContainer)

        self.thirdColLayout.addWidget(self.graphsAndInfoScroll)

    
    def plotPlaceholderData(self):
        self.axes = self.figure.add_subplot(211)

        self.axes.grid(alpha = 0.2)
        
        self.axes.set_ylabel("Кол-во лебедей")
        self.axes.set_xlabel("Месяц")

        months = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        swans_1 = [1,  3, 10, 3, 4, 1, 5, 8, 2, 3, 1, 4]
        swans_2 = [4, 12, 14, 7, 4, 1, 6, 5, 6, 8, 4, 6]
        swans_3 = [13, 9, 10, 3, 8, 9, 5, 8, 2, 7, 2, 3]
        labels  = ["Лебеди 1", "Лебеди 2", "Лебеди 3"]
        
        self.axes.plot(months, swans_1, label=labels[0])
        self.axes.plot(months, swans_2, label=labels[1])
        self.axes.plot(months, swans_3, label=labels[2])

        self.axes.legend()


        self.totalAxes = self.figure.add_subplot(212)
        self.totalAxes.pie([sum(swans_1), sum(swans_2), sum(swans_3)], labels=labels, wedgeprops=dict(width = 0.5))

        self.canvas.draw()


    def treeItemClicked(self, it : QTreeWidgetItem, col):
        if not os.path.isdir(getItemFullPath(it)):
            print(getItemFullPath(it))
            self.imageBrowser.updatePixmap(getItemFullPath(it))
        else:
            print("Its a folder!")