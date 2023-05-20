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
    QSlider,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QFileDialog
)

from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtCore import Qt

import os

from constants.paths import RESULT_PATH
from widgets.ImageBrowser import ImageBrowser

from yolov5.detect import detect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationTool
from matplotlib.figure import Figure

from pathlib import WindowsPath

from torch import cuda

from threading import Thread


def loadPaths(startpath: str, tree : QTreeWidget) -> None:
    for elem in os.listdir(startpath):
        elemPath = startpath + "/" + elem
        parentalItem = QTreeWidgetItem(tree, [os.path.basename(elem)])

        if os.path.isdir(elemPath):
            loadPaths(elemPath, parentalItem)
            parentalItem.setIcon(0, QIcon("assets\open-folder.png"))
        else:
            parentalItem.setIcon(0, QIcon("assets\processing.png"))


def getItemFullPath(item : QTreeWidgetItem) -> str:
    out = item.text(0)

    if item.parent():
        out = getItemFullPath(item.parent()) + "/" + out
    else:
        out =  "results/" + out

    return out


class MainWindow(QMainWindow):
    currentlySelectedFolder = ""

    def __init__(self) -> None:
        super().__init__()

        self.initUi()


    def initUi(self):
        '''
        Инициализация UI
        '''
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
        '''
        Инициализация древа файлов и папок в результатах и контроля параметров модели
        '''
        self.resultFileTree = QTreeWidget()
        self.resultFileTree.setHeaderLabel("Results")
        self.resultFileTree.setMaximumWidth(int(self.windowWidth / 5))
        self.resultFileTree.setMinimumWidth(int(self.windowWidth / 6))
        self.resultFileTree.setMaximumHeight(int(self.windowHeight / 2))
        self.resultFileTree.itemClicked.connect(self.treeItemClicked)

        loadPaths(startpath=RESULT_PATH, tree=self.resultFileTree)

        self.detectionPercentSliderLayout = QHBoxLayout()

        self.detectionSliderLabel = QLabel("Минимальный процент уверенности")
        self.detectionSliderLabel.setMaximumHeight(15)
        self.detectionSliderLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.detectionPercentLabel = QLabel("50%")
        self.detectionPercentLabel.setMaximumWidth(30)
        self.detectionPercentLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.detectionPercentSlider = QSlider(Qt.Orientation.Horizontal)
        self.detectionPercentSlider.setMaximumWidth(int(self.windowWidth / 5) - 35)
        self.detectionPercentSlider.setRange(1, 100)
        self.detectionPercentSlider.setValue(50)
        self.detectionPercentSlider.setSingleStep(1)
        self.detectionPercentSlider.valueChanged.connect(self.onPercentSliderValueChange)

        self.detectionPercentSliderLayout.addWidget(self.detectionPercentLabel)
        self.detectionPercentSliderLayout.addWidget(self.detectionPercentSlider)


        self.lineThicknessSliderLayout = QHBoxLayout()

        self.lineThicknessSliderLabel = QLabel("Толщина линий выделения")
        self.lineThicknessSliderLabel.setMaximumHeight(15)
        self.lineThicknessSliderLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.lineThicknessLabel = QLabel("3")
        self.lineThicknessLabel.setMaximumWidth(30)
        self.lineThicknessLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lineThicknessSlider = QSlider(Qt.Orientation.Horizontal)
        self.lineThicknessSlider.setMaximumWidth(int(self.windowWidth / 5) - 35)
        self.lineThicknessSlider.setRange(1, 10)
        self.lineThicknessSlider.setValue(3)
        self.lineThicknessSlider.setSingleStep(1)
        self.lineThicknessSlider.valueChanged.connect(self.onThicknessSliderValueChange)

        self.lineThicknessSliderLayout.addWidget(self.lineThicknessLabel)
        self.lineThicknessSliderLayout.addWidget(self.lineThicknessSlider)


        self.deviceCheckBoxesLabel = QLabel("Девайс")
        self.deviceCheckBoxesLabel.setMaximumHeight(15)
        self.deviceCheckBoxesLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.deviceCheckBoxesLayout = QHBoxLayout()

        self.cpuCheckBox  = QCheckBox("CPU")
        self.cpuCheckBox.setMaximumWidth(50)
        self.cpuCheckBox.setChecked(True)
        self.cpuCheckBox.stateChanged.connect(self.checkBoxCheckMate)

        self.cudaCheckBox = QCheckBox("GPU") 
        self.cudaCheckBox.setEnabled(cuda.is_available())
        self.cudaCheckBox.stateChanged.connect(self.checkBoxCheckMate)
        self.cudaCheckBox.setMaximumWidth(50)

        self.deviceCheckBoxesLayout.addWidget(self.cpuCheckBox)
        self.deviceCheckBoxesLayout.addWidget(self.cudaCheckBox)


        self.pathLayout = QHBoxLayout()

        self.pathLabel = QLabel("Выбранная папка:")
        self.pathLabel.setMaximumHeight(15)
        self.pathLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.pathLabel.setMaximumWidth(100)

        self.pathDisplay = QLineEdit(self.currentlySelectedFolder)
        self.pathDisplay.setMaximumWidth(int(self.windowWidth / 5) - 100)
        self.pathDisplay.setReadOnly(True)

        self.pathLayout.addWidget(self.pathLabel)
        self.pathLayout.addWidget(self.pathDisplay)


        self.chooseFolderButton = QPushButton("Выбрать папку")
        self.chooseFolderButton.clicked.connect(self.chooseFolder)


        self.detectButton = QPushButton("Detect")
        self.detectButton.clicked.connect(self.onDetectButtonClicked)
        self.detectButton.setEnabled(False)


        self.firstColLayout.addWidget(self.resultFileTree)
        self.firstColLayout.addWidget(self.detectionSliderLabel)
        self.firstColLayout.addLayout(self.detectionPercentSliderLayout)
        self.firstColLayout.addWidget(self.lineThicknessSliderLabel)
        self.firstColLayout.addLayout(self.lineThicknessSliderLayout)
        self.firstColLayout.addWidget(self.deviceCheckBoxesLabel)
        self.firstColLayout.addLayout(self.deviceCheckBoxesLayout)
        self.firstColLayout.addLayout(self.pathLayout)
        self.firstColLayout.addWidget(self.chooseFolderButton)
        self.firstColLayout.addWidget(self.detectButton)


    def onPercentSliderValueChange(self):
        '''
        Функция вызываемая при смене значения на слайдере
        '''
        self.detectionPercentLabel.setText(str(self.sender().value()) + "%")

    
    def onThicknessSliderValueChange(self):
        '''
        Функция вызываемая при смене значения на слайдере
        '''
        self.lineThicknessLabel.setText(str(self.sender().value()))


    def checkBoxCheckMate(self):
        if self.sender().checkState() == Qt.CheckState.Checked:
            if   self.sender() == self.cpuCheckBox:
                self.cudaCheckBox.setChecked(False)
            elif self.sender() == self.cudaCheckBox:
                self.cpuCheckBox.setChecked(False)


    def chooseFolder(self):
        currentUser = os.environ.get('USER', os.environ.get('USERNAME'))
        self.currentlySelectedFolder = QFileDialog(directory=f"C:/Users/{currentUser}/Pictures").getExistingDirectory()

        self.updatePathDisplay()


    def updatePathDisplay(self):
        self.pathDisplay.setText(self.currentlySelectedFolder)
        if self.currentlySelectedFolder != "":
            self.detectButton.setEnabled(True)
        else:
            self.detectButton.setEnabled(False)


    def initImageBrowser(self):
        '''
        Инициализация браузера изображений
        '''
        self.imageBrowser = ImageBrowser()
        self.imageBrowser.updatePixmap(None)
        self.imageBrowser.setMaximumWidth(int(self.windowWidth / 2))

        self.secondColLayout.addWidget(self.imageBrowser, alignment=Qt.AlignmentFlag.AlignTop)


    def initGraphsAndInfo(self):
        '''
        Инициализация графиков и информации о полученных фото
        '''
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
        '''
        Затычка для данных графиков
        '''
        self.axes = self.figure.add_subplot(211)

        self.axes.grid(alpha = 0.2)
        
        self.axes.set_ylabel("Кол-во лебедей")
        self.axes.set_xlabel("Месяц")

        months = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        swans_1 = [1,  3, 10, 3, 4, 1, 5, 8, 2, 3, 1, 4]
        swans_2 = [4, 12, 14, 7, 4, 1, 6, 5, 6, 8, 4, 6]
        swans_3 = [13, 9, 10, 3, 8, 9, 5, 8, 2, 7, 2, 3]
        labels  = ["Шипуны", "Кликуны", "Малые лебеди"]
        
        self.axes.plot(months, swans_1, label=labels[0])
        self.axes.plot(months, swans_2, label=labels[1])
        self.axes.plot(months, swans_3, label=labels[2])

        self.axes.legend()


        self.totalAxes = self.figure.add_subplot(212)
        self.totalAxes.pie([sum(swans_1), sum(swans_2), sum(swans_3)], labels=labels, wedgeprops=dict(width = 0.5))

        self.canvas.draw()

    
    def onDetectButtonClicked(self):
        detection_thread = Thread(target=self.detect)
        detection_thread.start()

    
    def detect(self):
        self.detectButton.setEnabled(False)

        if self.cudaCheckBox.isChecked():
            device = "cuda:0"
        else: 
            device = "cpu"

        options = {
            'weights': ['yolov5\\runs\\train\\exp14\\weights\\best.pt'], 
            'source': self.currentlySelectedFolder, 
            'data': WindowsPath('data/coco128.yaml'), 
            'imgsz': [640, 640], 
            'conf_thres': self.detectionPercentSlider.value()/100, 
            'iou_thres': 0.45, 
            'max_det': 1000, 
            'device': device, 
            'view_img': False, 
            'save_txt': False, 
            'save_conf': False, 
            'save_crop': False, 
            'nosave': False, 
            'classes': None, 
            'agnostic_nms': False, 
            'augment': False, 
            'visualize': False, 
            'update': False, 
            'project': WindowsPath('results'), 
            'name': 'run', 
            'exist_ok': False, 
            'line_thickness': self.lineThicknessSlider.value(), 
            'hide_labels': False, 
            'hide_conf': False, 
            'half': False, 
            'dnn': False, 
            'vid_stride': 1
        }
        
        detect(options)

        self.resultFileTree.clear()
        loadPaths(RESULT_PATH, self.resultFileTree)

        self.currentlySelectedFolder = ""
        self.updatePathDisplay()


    def treeItemClicked(self, it : QTreeWidgetItem, col):
        '''
        Функция вызываемая при нажатии на элемент в дереве файлов папки результатов
        '''
        if not os.path.isdir(getItemFullPath(it)):
            self.imageBrowser.updatePixmap(getItemFullPath(it))