import sys
from PyQt6.QtWidgets import QApplication
from photon_app import PhotonApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotonApp()
    window.showMaximized()
    sys.exit(app.exec())
