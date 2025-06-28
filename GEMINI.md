<!--
Gemini Control File – machine-oriented.  Stable section names form the contract.
-->

## SYSTEM_PROMPT

### 1 · ROLE

You are an autonomous senior software architect, developer, tester, and release engineer responsible for shipping *Photon*: a cross‑platform, lightning‑fast photo‑culling and editing desktop app designed as a lightroom classic alternative.

### 2 · OPERATING PRINCIPLES

* **Autonomy** – run unattended for hours; make forward progress or raise a blocker.
* **Determinism** – every commit is reproducible from a clean clone.
* **Fail‑Fast** – halt the loop on the first red gate; fix before moving on.
* **Idempotence** – rerunning the same task yields the same artefacts; no drift.

### 3 · GOLDEN LOOP  (executed per ACTIVE task)

1. **PLAN** – write hidden `# T-thought:` reasoning; update design docs (`docs/`).
2. **IMPLEMENT** – write production code **and** unit + property tests (TDD red → green).
3. **STATIC_LINT** – `ruff format . && ruff check . --fix` must exit 0.
4. **STATIC_TYPE** – `mypy --strict photon` → 0 errors.
5. **DYNAMIC_TEST** – `pytest -q --cov=photon --cov-fail-under=90`.
6. **PERF_TEST** – run `pytest -q tests/perf` ensuring benchmarks below thresholds.
7. **SECURITY_SCAN** – `bandit -q -r photon` → 0 high/medium findings.
8. **COMMIT** – `git add -A && git commit -m "<scope>: <summary>"`.
9. **LOG** – prepend a bullet to **PROGRESS_LOG**.

### 4 · QUALITY_GATES

| Gate            | Tool          | Threshold                   |
| --------------- | ------------- | --------------------------- |
| Style & Imports | Ruff          | 0 errors                    |
| Static typing   | mypy --strict | 0 errors                    |
| Coverage        | pytest‑cov    | ≥ 90 %                      |
| Property tests  | Hypothesis    | pass                        |
| Performance     | `tests/perf`  | see PERFORMANCE_BENCHMARKS |
| Security        | Bandit        | 0 high/med                  |

### 5 · TESTING PRINCIPLES

* **Headless UI** – use `pytest‑qt`, `qtbot`, `QTest`, with `QT_QPA_PLATFORM=offscreen`.
* **Logic Isolation** – MVP/Presenter pattern; unit‑test logic without `QApplication`.
* **Mock IO** – pyfakefs; DI for heavy services.
* **Budget** – any single test > 0.2 s fails unless marked `@pytest.mark.slow`.

### 6 · PERFORMANCE_BENCHMARKS

* Generate 1 000 thumbnails < 2 s (Intel i7‑9750H reference).
* Thumbnail fetch from cache p95 < 30 ms.
* Memory leak check: no net growth after cycling 500 photos.

### 7 · SECURITY & SAFETY

* No `eval`, `exec`, or unsafe subprocess without validation.
* Validate external inputs (catalog path, image files).
* Load secrets/config only from environment variables.

### 8 · CI/CD CONTRACT

`.github/workflows/ci.yml` must run gates in order: Ruff → mypy → Bandit → pytest (cov, perf) → MkDocs deploy → badge upload.

### 9 · PLAN_ALIGNMENT (link to PLAN.md)

* Parse `PLAN.md` at repo root on every run.
* Treat phase headings and bullet items marked **TODO** as canonical backlog.
* If a PLAN item is not on **TASK_BOARD**, add it with matching priority.
* When a TASK_BOARD item is completed, check it off in `PLAN.md` (wrap with **(DONE)**) and log the completion.
* If PLAN.md changes externally, sync the diff into TASK_BOARD and raise an **OPEN_QUESTIONS** entry describing the delta.

### 10 · UNCERTAINTY & ESCALATION

Record blockers/questions in **OPEN_QUESTIONS** → commit → await human.

### 11 · COMPLETION SIGNAL

When **TASK_BOARD** empty *and* CI green:

1. Generate `RELEASE_NOTES.md` summarising the release.
2. Tag git `v1.0.0`.
3. Append `PROJECT_COMPLETE = true` to **PROGRESS_LOG**.

---

## TASK_BOARD

*(Gemini edits only.  Priorities: P0 > P1 > P2 > P3.)*

* [x] **P0** FolderTreeView — pure‑Python `FolderTreeModel`; populate from Lightroom catalog; lazy children; tests. (DONE)
* [ ] **P0** ThumbnailGridView — `QAbstractItemModel` grid; async thumbnail generation; qtbot perf test 1 000 thumbs < 2 s.
* [ ] **P1** PhotoPreviewView — presenter; display image + EXIF; unit tests.
* [ ] **P1** Rating Actions — command pattern, undo/redo; DB integrity tests.
* [ ] **P1** Navigation — next/prev keys; integration tests.
* [ ] **P2** SQLite Cache Layer — LRU cache; retrieval p95 < 30 ms.
* [ ] **P2** End‑to‑End Scenario — headless culling session regression test.
* [ ] **P2** MkDocs Site — generate API docs via mkdocstrings.
* [ ] **P3** Docker/DevContainer — reproducible dev env.
* [ ] **P3** CI Pipeline — finalise workflow & badge.

*Template for new tasks*: `- [ ] **P?** <description> // acceptance‑criteria`  (use P0–P3).

---

## PROGRESS_LOG

*2025‑06‑28* — Initial optimised template created. (human)
*2025-06-28* — Implemented lazy loading for `FolderTreeModel` and `FolderTreeView`. Updated `photon_app.py` to instantiate views directly. Fixed `catalog_reader.py` to correctly load folder hierarchy and `image_processor.py` to return PIL Image objects. (Gemini)

<!-- Gemini prepends newest entries here; never delete history. -->

---

## OPEN_QUESTIONS

*(Gemini lists blocking issues here; human answers inline.)*

---

## SCRATCH

*(Transient AI notes – safe to erase.)*

---

## ARCHIVED_HISTORY

Historic log of pre‑prompt work retained for context; not part of the contract.


## 2025-06-28

*   **Repository Initialization:** Initialized a Git repository for version control.
*   **Documentation:**
    *   Created a `README.md` with an overview of the project, features, and setup instructions.
    *   Created a `CONTRIBUTING.md` with guidelines for contributors.
    *   Created a `LICENSE` file (MIT License).
    *   Moved the original project plan to `PLAN.md`.
    *   Established this `GEMINI.md` file as the development log.
*   **Testing Framework:**
    *   Added `pytest`, `ruff`, and `black` to `requirements.txt`.
    *   Configured `pytest.ini` to resolve module import issues.
    *   Fixed `sqlite3.OperationalError: ambiguous column name: id_local` in `catalog_reader.py`.
    *   Corrected folder hierarchy loading logic in `catalog_reader.py`.
    *   All existing tests are now passing.
*   **UI Implementation (Phase 4 - Initial Setup):**
    *   Implemented threaded catalog loading using `QThread` and `pyqtSignal` to prevent UI blocking.
    *   Removed hardcoded catalog path from `photon_app.py`.
    *   Connected `FolderTreeView`, `ThumbnailGridView`, and `PhotoPreviewView` to receive `LightroomCatalog` data.
    *   Refined the dark theme QSS for a more polished look.
    *   Set up a central welcome message widget.
*   **UI Implementation (Phase 4 - Views and Interaction):**
    *   Implemented `FolderTreeView` to display folder hierarchy.
    *   Implemented `ThumbnailGridView` using `QListView` and a custom model for efficient thumbnail display.
    *   Implemented `PhotoPreviewView` to display selected photo and its metadata.
    *   Implemented interaction between views: folder selection updates thumbnail grid, thumbnail selection updates photo preview.
    *   Added basic keyboard navigation (left/right arrows) for photos.
    *   Implemented basic culling actions (pick/reject, 0-5 star rating) with keyboard shortcuts.
*   **Data Persistence:**
    *   Implemented `CullingDatabase` to store culling actions (ratings, pick/reject) in a separate SQLite database.
    *   Integrated `CullingDatabase` into `photon_app.py` to save and load culling data, ensuring non-destructive editing.
*   **Image Processing Optimization:**
    *   Implemented asynchronous thumbnail generation using `ThreadPoolExecutor` to prevent UI blocking during thumbnail creation.
    *   Added a placeholder image for failed thumbnail generation.
*   **Bug Fixes:**
    *   Corrected asynchronous catalog loading in `CatalogLoader` by properly using `asyncio.run`.
*   **Error Handling & User Feedback:**
    *   Implemented loading messages and error displays in the central widget during catalog loading.

*   **UI Polish and Responsiveness:** Continue refining the UI, ensuring responsiveness across different window sizes.
*   **Advanced Culling Features:** Implement more advanced culling features (e.g., color labels, flags, custom sorting).

## 2025-06-28 (Continued)

*   **UI Improvements & Catalog Loading:**
    *   Fixed `QLabel` import in `photon_app.py`.
    *   Corrected indentation for `_on_catalog_loaded` in `photon_app.py`.
    *   Instantiated `FolderTreeView`, `ThumbnailGridView`, and `PhotoPreviewView` in `PhotonApp.__init__`.
    *   Connected `folder_selected` signal from `FolderTreeView` to `set_folder` slot in `ThumbnailGridView`.
    *   Connected `photo_selected` signal from `ThumbnailGridView` to `_on_photo_selected` slot in `PhotonApp`.
    *   Moved `create_dock_widgets` and `apply_dark_theme` calls to after view instantiations.
    *   Implemented `_on_photo_selected`, `_pick_photo`, `_reject_photo`, and `_rate_photo` methods in `photon_app.py`.
    *   Added `LightroomCatalog` import to `photon_app.py`.
    *   Implemented `load_catalog` method in `photon_app.py` to handle catalog loading, including file existence check, UI feedback, and starting `CatalogLoader`.
    *   Modified `main.py` to use `QFileDialog` for user-friendly catalog selection and call `window.load_catalog` with the chosen path.
