from PyQt6.QtWidgets import (
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

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

import os

from constants.paths import RESULT_PATH
from widgets.ImageBrowser import ImageBrowser

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
        self.resultFileTree.setMaximumWidth(300)
        self.resultFileTree.setMinimumWidth(150)
        self.resultFileTree.setMaximumHeight(500)
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
        self.detectionPercentSlider.setMaximumWidth(265)
        self.detectionPercentSlider.setRange(1, 100)
        self.detectionPercentSlider.setSingleStep(1)
        self.detectionPercentSlider.valueChanged.connect(self.onSliderValueChange)

        self.sliderLayout.addWidget(self.detectionPercentLabel)
        self.sliderLayout.addWidget(self.detectionPercentSlider)

        self.firstColLayout.addWidget(self.resultFileTree)
        self.firstColLayout.addWidget(self.detectionSliderLabel)
        self.firstColLayout.addLayout(self.sliderLayout)
        # self.firstColLayout.addWidget(self.detectionPercentLabel)
        # self.firstColLayout.addWidget(self.detectionPercentSlider)


    def onSliderValueChange(self):
        self.detectionPercentLabel.setText(str(self.sender().value()) + "%")


    def initImageBrowser(self):
        self.imageBrowser = ImageBrowser()
        self.imageBrowser.updatePixmap(None)
        self.imageBrowser.setMaximumWidth(1000)
        self.imageBrowser.setMinimumWidth(600)

        self.secondColLayout.addWidget(self.imageBrowser, alignment=Qt.AlignmentFlag.AlignTop)


    def initGraphsAndInfo(self):
        self.graphsAndInfoScroll = QScrollArea()
        self.graphsAndInfoScroll.setWidgetResizable(True)
        self.graphsAndInfoScroll.setFixedWidth(600)
        self.graphsAndInfoScroll

        self.placeholderGraph = QLabel()
        self.placeholderGraph.setPixmap(QPixmap("assets/placeholder_graph.png").scaledToWidth(560))
        self.placeholderGraph.setFixedWidth(560)

        self.placeholderInfo = QTextBrowser()
        self.placeholderInfo.setText("Очень важная информация о лебедях и возможно гусях))")
        self.placeholderInfo.setFixedWidth(560)

        self.GIContainer = QWidget()
        self.GIContainerLayout = QVBoxLayout()
        self.GIContainerLayout.addWidget(self.placeholderGraph)
        self.GIContainerLayout.addWidget(self.placeholderInfo )

        self.GIContainer.setLayout(self.GIContainerLayout)
        
        self.graphsAndInfoScroll.setWidget(self.GIContainer)

        self.thirdColLayout.addWidget(self.graphsAndInfoScroll)


    def treeItemClicked(self, it : QTreeWidgetItem, col):
        if not os.path.isdir(getItemFullPath(it)):
            print(getItemFullPath(it))
            self.imageBrowser.updatePixmap(getItemFullPath(it))
        else:
            print("Its a folder!")