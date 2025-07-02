# Photon

Photon is a fast, desktop photo-culling application designed for professional and hobbyist photographers. It provides a streamlined, performance-oriented workflow to quickly sort through large volumes of photos by integrating directly with Adobe Lightroom Classic catalogs.

## Features (v1)

*   **Direct Lightroom Catalog Integration:** Opens `*.lrcat` files to read photo libraries without needing an intermediate import step.
*   **High-Performance UI:** A fluid, responsive interface built with PyQt5, featuring a Lightroom-style Library module for familiar navigation.
*   **Efficient Culling Workflow:** Fast grid and loupe views with essential hotkeys (`1-5` for ratings, `P` for Pick, `X` for Reject) that write directly back to the catalog.
*   **Dockable Workspace:** Customizable panel layout that persists between sessions.

## Getting Started (Windows)

*Prerequisites: Python 3.11+*

1.  **Clone the repository:**
    ```powershell
    git clone <repo-url>
    cd Photon
    ```

2.  **Set up the virtual environment:**
    ```powershell
    py -3.11 -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```powershell
    python -m src.main
    ```
