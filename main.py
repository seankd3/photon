import sys
from PyQt6.QtWidgets import QApplication
from photon_app import PhotonApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotonApp()
    window.showMaximized()

    # Example: Load a catalog. Replace with a real path or user selection.
    # For testing, you can uncomment and provide a valid .lrcat path.
    # window.load_catalog(r"C:\Path\To\Your\Catalog.lrcat")

    sys.exit(app.exec())
