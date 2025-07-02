import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QLabel
)


class GridView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.image_widgets = []

    def add_image(self, image):
        i = len(self.image_widgets)
        label = QLabel(image[1])  # image[1] is the fileName
        self.layout.addWidget(label, i // 4, i % 4)
        self.image_widgets.append(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photon")
        self.setGeometry(100, 100, 1200, 800)

        self.grid_view = GridView(self)
        self.setCentralWidget(self.grid_view)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
