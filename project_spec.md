# Project: Photon – Fast Photo-Culling Desktop App

### Stack & Constraints

* Language: Python 3.11+
* GUI  : PyQt5 (Qt 5.15 LTS)
* DB    : Read/write Adobe Lightroom Classic catalogs (\*.lrcat SQLite, test catalog provided at TestCatolog\2025.lrcat)
* OS    : Windows 11 first, keep code cross-platform
* License: MIT

### Functional Requirements

1. **Lightroom‑Style Workspace Skeleton**

   * Replicate Lightroom Classic’s *Library* module layout (editing controls are **out‑of‑scope for v1**).
   * Four primary, dockable zones:
     **Left Panel** (Navigator preview, Folder tree, Collections),
     **Central Viewer** (alternating Grid ⬌ Loupe),
     **Right Panel** (Histogram, Quick Info, basic EXIF/metadata),
     **Filmstrip** (horizontal thumbnail ribbon with rating overlays).
   * Panels roll in/out with the *Tab* shortcuts: `Tab` toggles side panels, `Shift+Tab` toggles all UI chrome.
   * Panel positions & visibility persist via `layout.json`.

2. **Catalog Import / Sync**

   * Open existing `*.lrcat` SQLite catalog; parse `Adobe_images`, `AgLibraryFile`, ratings, flags.
   * Detect external changes (timestamp polling); refresh thumbnails/metadata without restart.

3. **Grid & Loupe View**

   * **Grid:** infinite‑scroll thumbnails, adaptive columns, spacebar toggles full‑screen Loupe.
   * **Loupe:** full‑resolution preview with pan/zoom (mouse wheel, drag), overlay ratings/flags.
   * **Filmstrip navigation:** left/right arrows & mouse scroll move selection; updates Loupe.

4. **Rating / Flagging / Reject**

   * Hotkeys identical to Lightroom: `1–5` = stars, `6–9` reserved, `P` (keep/flag), `X` (reject), `U` (clear).
   * Changes debounced and persisted back to catalog ≤200 ms after keypress.

5. **Cull Queue & Filters**

   * Quick‑filter bar: `All / Picks / Rejects / Unrated` counts & buttons.
   * Shortcut `F` jumps to next Unrated; `Shift+F` previous.

6. **Dockable Panel Framework**

   * Blender‑style drag‑to‑dock/undock; QtDockPanels with custom titlebars.
   * Initial panel suite:

     * **Navigator** (preview + zoom scrubber)
     * **Folder Tree** (OS/collections hierarchy)
     * **Collections** (custom sets)
     * **Histogram** (live RGB histogram)
     * **Metadata** (read‑only EXIF)
     * **Cull Stats** (kept/rejected tally)

7. **Session Export**

   * Write updated ratings/flags to catalog **and** generate side‑car JSON (`session‑summary.json`).
   * Optional plain‑text lists: `kept.txt`, `rejected.txt`.

### Non-Functional Requirements

* Startup < 2 s with 20 k photos; scrolling 60 fps on mid-range GPU.
* CPU-only fallback if no OpenGL.
* Memory cap configurable (avoid loading full-res unless loupe).

### Acceptance Tests (high level)

| ID    | Scenario                           | Expected                                       |
| ----- | ---------------------------------- | ---------------------------------------------- |
| AT-01 | Open catalog with 5 k images      | Thumbnails populate within 10 s; UI responsive |
| AT-02 | Press “3” on focused photo         | DB rating for that row == 3 within 200 ms      |
| AT-03 | Drag Histogram panel to right dock | Panel snaps & state saved in layout JSON       |
| AT-04 | Mark 500 photos “X” then export    | Catalog flags updated + JSON summary created   |

### Initial Feature Seed

<!-- These become FEATURES.json entries -->

* Catalog opening & simple read-only grid view   (priority P0) - Implemented with full image display, scrollable grid, dark theme, and .CR3 support.
* Hotkey rating / flagging → write-back            (P0) - Implemented as a CLI command.
* Dockable panel framework scaffold                (P0)
* Histogram side panel (live RGB histogram)        (P1)
* Cull stats panel                                 (P1)
* Catalog change watcher (automatic refresh)       (P2)
* JSON export of rejected + kept lists             (P2)

### Confirmations & Notes

* Provide **PLAN** first; wait for my “OK to code” before touching files.
* Put thumbnails in an async loader thread—no UI freeze.
* Use pip-installable deps only; document any Qt Designer files.
