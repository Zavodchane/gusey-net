from PyQt6.QtWidgets import (
    QLabel
)

from PyQt6.QtGui import (
    QPixmap
)


class ImageBrowser(QLabel):
    '''
    Класс браузера изображений (слегка переделаный QLabel)
    '''

    def __init__(self):
        super().__init__()

    
    def updatePixmap(self, path: str):
        '''
        Функция обновления QPixmap для браузера
        '''
        self.setPixmap(QPixmap(path).scaledToWidth(self.maximumWidth() - 40))
