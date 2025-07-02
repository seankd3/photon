import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QLabel
)
from src.catalog import get_images


class Worker(QObject):
    image_found = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, catalog_path):
        super().__init__()
        self.catalog_path = catalog_path

    def run(self):
        images = get_images(self.catalog_path)
        # Only load a small number of images for demonstration purposes
        for i, image in enumerate(images):
            if i >= 20:  # Limit to 20 images for responsiveness
                break
            self.image_found.emit(image)
        self.finished.emit()


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

        self.load_catalog()

    def load_catalog(self):
        catalog_path = "C:/Users/smast/OneDrive/Desktop/CodeProjects/Photon/TestCatolog/2025.lrcat"

        self.thread = QThread()
        self.worker = Worker(catalog_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.image_found.connect(self.grid_view.add_image)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.close_application_timer)

        self.thread.start()

    def close_application_timer(self):
        QTimer.singleShot(5000, QApplication.instance().quit)  # Close after 5 seconds


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()