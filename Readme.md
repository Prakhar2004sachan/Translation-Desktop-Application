# Translation Desktop Application

A modern, high-performance desktop utility designed to scan directories, selectively translate CJK (Chinese, Japanese, Korean) file and folder names using state-of-the-art LLMs/APIs (Google Gemini, DeepL, Google Translate), and safely batch-rename them with built-in undo recovery.

---

## Key Features

* **Decoupled Scanning & Translation:** Scan a target folder to preview items as `PENDING` with original filenames before triggering any API translation requests.
* **Hierarchical Tree Selection:** Recursively select or deselect child files and subfolders by checking/unchecking parent folders.
* **State-of-the-Art Translators:** Integrated with Google GenAI SDK (`google-genai`), DeepL, and Google Translate, featuring exponential backoff retries on rate limits.
* **Safe Batch Undo:** Every renaming batch is logged in a persistent session file (`~/.rename_tools/undo_history.json`). You can revert any renaming batch instantly.
* **Fully Responsive & Dockable UI:** Drag, resize, split, or dock/undock panels to arrange your layout. Views automatically scale responsively if the main window is resized.
* **Header Menus:** Built-in **Views** menu to toggle sidebars, and a **Help** menu with an interactive tabbed **Tutorial** (with screenshots) and **About Us** page.

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/prakharsachan/Rename-Tools.git
   cd Rename-Tools
   ```

2. **Set up Virtual Environment:**
   * **macOS/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   * **Windows:**
     ```cmd
     python -m venv venv
     call venv\Scripts\activate.bat
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

Ensure your virtual environment is active, then run:

```bash
python main.py
```

---

## Running Automated Tests

Run the full pytest suite (covering unit tests for Scanner, Renamer, Gemini Client, and Integration Flow):

```bash
python -m pytest -v
```

---

## Packaging Standalone Apps

### 🍎 macOS (Produces App Bundle & DMG Disk Image)
Make `build.sh` executable and run it on macOS:
```bash
chmod +x build.sh
./build.sh
```
* **App Bundle:** `dist/Translation Desktop Application.app`
* **DMG Installer:** `dist/Translation-Desktop-Application-Installer.dmg` (supports drag-and-drop to Applications).

###  Windows (Produces .exe)
Run the batch file on a Windows system:
```cmd
build.bat
```
* **Executable:** `dist/Translation Desktop Application/` folder containing the compiled `.exe`.