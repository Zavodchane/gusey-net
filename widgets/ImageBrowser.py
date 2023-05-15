from PyQt6.QtWidgets import (
    QLabel
)

from PyQt6.QtGui import (
    QPixmap
)


class ImageBrowser(QLabel):
    def __init__(self):
        super().__init__()

    
    def updatePixmap(self, path: str):
        self.setPixmap(QPixmap(path).scaledToWidth(self.maximumWidth() - 40))
