from imgui_bundle import imgui
import asyncio
from pathlib import Path
import threading
from typing import List

from models.config import AppConfig
from models.translation_item import TranslationItem, ItemStatus, ItemType

from gui.main_window import MainWindow
from gui.preview_window import PreviewWindow
from gui.progress_window import ProgressWindow
from gui.settings_window import SettingsWindow

from filesystem.scanner import DirectoryScanner
from filesystem.renamer import Renamer
from utils.background_worker import BackgroundWorker

def resolve_asset_path(relative_path: str) -> str:
    import sys
    import os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

class App:
    def __init__(self):
        from models.config import get_user_data_dir
        self.config = AppConfig.load()
        self.main_window = MainWindow(self.config)
        self.preview_window = PreviewWindow()
        self.progress_window = ProgressWindow()
        self.settings_window = SettingsWindow(self.config)
        
        self.scanner = DirectoryScanner(self.config.filter_settings)
        self.renamer = Renamer(history_file=str(get_user_data_dir() / "undo_history.json"))
        
        self.worker = BackgroundWorker(max_workers=2)
        
        self.is_scanning = False
        self.is_translating = False
        self.is_renaming = False
        
        self.items: List[TranslationItem] = []

    def render(self):
        # Lazy load textures on the first frame where OpenGL context is active
        if not hasattr(self, "textures_loaded"):
            from utils.texture_loader import load_texture
            self.icon_tex, self.icon_w, self.icon_h = load_texture(resolve_asset_path("assets/icon.png"))
            self.screenshot_main_tex, self.ss_main_w, self.ss_main_h = load_texture(resolve_asset_path("assets/screenshot_main.png"))
            self.screenshot_preview_tex, self.ss_prev_w, self.ss_prev_h = load_texture(resolve_asset_path("assets/screenshot_preview.png"))
            self.textures_loaded = True
            
            # Window toggle states
            self.show_controls_window = True
            self.show_preview_window = True
            self.show_tutorial_window = False
            self.show_about_window = False

        # Create Dockspace over the viewport so users can dock/undock and arrange layouts
        imgui.dock_space_over_viewport(viewport=imgui.get_main_viewport())

        # Top Menu Bar
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                clicked, _ = imgui.menu_item("Settings", "", False)
                if clicked:
                    self.settings_window.is_open = not self.settings_window.is_open
                
                clicked, _ = imgui.menu_item("Undo Last Batch", "", False)
                if clicked:
                    self.undo_last()
                    
                clicked, _ = imgui.menu_item("Exit", "", False)
                if clicked:
                    import sys
                    sys.exit(0)
                imgui.end_menu()

            if imgui.begin_menu("Views"):
                _, self.show_controls_window = imgui.menu_item("Controls Sidebar", "", self.show_controls_window)
                _, self.show_preview_window = imgui.menu_item("Preview Panel", "", self.show_preview_window)
                imgui.end_menu()

            if imgui.begin_menu("Help"):
                clicked, _ = imgui.menu_item("Tutorial", "", False)
                if clicked:
                    self.show_tutorial_window = True
                clicked, _ = imgui.menu_item("About Us", "", False)
                if clicked:
                    self.show_about_window = True
                imgui.end_menu()

            imgui.end_main_menu_bar()

        # Get OS Window Size dynamically
        io = imgui.get_io()
        window_w = io.display_size.x
        window_h = io.display_size.y
        menu_h = 22.0
        content_h = window_h - menu_h
        
        controls_w = max(340.0, min(500.0, window_w * 0.32))
        preview_w = window_w - controls_w
        selected_count = sum(1 for item in self.items if item.selected_for_rename)
        
        # Rescale sidebars responsively if the main OS window size changes!
        if not hasattr(self, "last_window_w"):
            self.last_window_w = window_w
            self.last_window_h = window_h
        elif self.last_window_w != window_w or self.last_window_h != window_h:
            imgui.set_window_size("Controls", (controls_w, content_h))
            imgui.set_window_pos("Controls", (0.0, menu_h))
            imgui.set_window_size("Preview", (preview_w, content_h))
            imgui.set_window_pos("Preview", (controls_w, menu_h))
            self.last_window_w = window_w
            self.last_window_h = window_h

        # Layout Controls UI (Sidebar) - Closeable and Dockable
        if self.show_controls_window:
            imgui.set_next_window_size((controls_w, content_h), imgui.Cond_.first_use_ever)
            imgui.set_next_window_pos((0, menu_h), imgui.Cond_.first_use_ever)
            expanded, self.show_controls_window = imgui.begin("Controls", True)
            if expanded:
                # App Header Logo & Title (shown when app is open)
                if self.icon_tex:
                    imgui.image(imgui.ImTextureRef(self.icon_tex), (28.0, 28.0))
                    imgui.same_line()
                    imgui.align_text_to_frame_padding()
                    imgui.text_colored(imgui.ImColor(0.2, 0.6, 1.0, 1.0).value, "Rename Tools Dashboard")
                    imgui.spacing()
                    imgui.separator()
                    imgui.spacing()

                scan_requested, translate_requested, settings_requested = self.main_window.render(selected_count)
                if scan_requested and not self.is_scanning and not self.is_renaming:
                    self.start_scan()
                    
                if translate_requested and not self.is_translating and not self.is_renaming:
                    self.start_translation()
                    
                if settings_requested:
                    self.settings_window.is_open = not self.settings_window.is_open
                    
                imgui.separator()
                imgui.spacing()
                
                # Start Renaming button (displays selected count)
                rename_label = f"Start Renaming ({selected_count} items)"
                if imgui.button(rename_label, (-1, 40)):
                    if not self.is_renaming and self.items:
                        self.start_renaming()
            imgui.end()
 
        # Layout Preview UI - Closeable and Dockable
        if self.show_preview_window:
            imgui.set_next_window_size((preview_w, content_h), imgui.Cond_.first_use_ever)
            imgui.set_next_window_pos((controls_w, menu_h), imgui.Cond_.first_use_ever)
            expanded, self.show_preview_window = imgui.begin("Preview", True)
            if expanded:
                self.preview_window.render(self.is_translating, self.is_scanning)
            imgui.end()

        # Layout About Us dialog
        if self.show_about_window:
            imgui.set_next_window_size((400, 310), imgui.Cond_.first_use_ever)
            expanded, self.show_about_window = imgui.begin("About Us", True)
            if expanded:
                if self.icon_tex:
                    # Centered logo
                    avail_x = imgui.get_content_region_avail().x
                    imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + (avail_x - 64.0) / 2.0)
                    imgui.image(imgui.ImTextureRef(self.icon_tex), (64.0, 64.0))
                    imgui.spacing()
                    
                imgui.separator()
                imgui.text_colored(imgui.ImColor(0.2, 0.6, 1.0, 1.0).value, "Translation Desktop Application")
                imgui.text("Version 1.0.0")
                imgui.spacing()
                imgui.text_wrapped("A modern, premium utility designed to scan directories, auto-translate CJK files/folders via advanced LLMs, and safely batch-rename them.")
                imgui.spacing()
                imgui.text_disabled("Pair Programmed with prakharsachan")
            imgui.end()

        # Layout Tutorial Dialog with screenshots
        if self.show_tutorial_window:
            imgui.set_next_window_size((600, 520), imgui.Cond_.first_use_ever)
            expanded, self.show_tutorial_window = imgui.begin("Tutorial", True)
            if expanded:
                imgui.text_colored(imgui.ImColor(0.2, 0.6, 1.0, 1.0).value, "User Guide:")
                imgui.spacing()
                
                if imgui.begin_tab_bar("tutorial_tabs"):
                    is_sel_1, _ = imgui.begin_tab_item("1. Scan & Select")
                    if is_sel_1:
                        imgui.text_wrapped("Choose your target folder and languages in the left sidebar, and click 'Scan Directory'.")
                        imgui.spacing()
                        if self.screenshot_main_tex:
                            # Scale dynamically based on available window width
                            img_w = max(100.0, imgui.get_content_region_avail().x - 20.0)
                            img_h = img_w * (360.0 / 540.0)
                            imgui.image(imgui.ImTextureRef(self.screenshot_main_tex), (img_w, img_h))
                        imgui.end_tab_item()
                        
                    is_sel_2, _ = imgui.begin_tab_item("2. Translate & Rename")
                    if is_sel_2:
                        imgui.text_wrapped("Check or uncheck the items you want to translate, then click 'Translate Selected'. Verify the new names, and click 'Start Renaming'.")
                        imgui.spacing()
                        if self.screenshot_preview_tex:
                            # Scale dynamically based on available window width
                            img_w = max(100.0, imgui.get_content_region_avail().x - 20.0)
                            img_h = img_w * (360.0 / 540.0)
                            imgui.image(imgui.ImTextureRef(self.screenshot_preview_tex), (img_w, img_h))
                        imgui.end_tab_item()
                    imgui.end_tab_bar()
            imgui.end()
 
        self.settings_window.render()
        self.progress_window.render()

    def undo_last(self):
        undone = self.renamer.undo_manager.undo_last_batch(100)
        print(f"Undid {undone} items.")

    def start_scan(self):
        directory = Path(self.config.last_directory)
        if not directory.exists() or not directory.is_dir():
            print(f"Invalid directory: {directory}")
            return
            
        self.is_scanning = True
        self.items.clear()
        
        def scan_task():
            try:
                for item in self.scanner.scan(directory):
                    # Filter by settings
                    if item.item_type == ItemType.FILE and not self.config.translation_settings.translate_files:
                        continue
                    if item.item_type == ItemType.FOLDER and not self.config.translation_settings.translate_folders:
                        continue
                    self.items.append(item)
                
                # Decouple scan from translation: render original items immediately
                self.preview_window.items = self.items
                self.is_scanning = False
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.is_scanning = False

        self.worker.submit(scan_task)

    def _get_translator(self):
        provider = self.config.provider
        if provider == "Gemini":
            from translator.gemini import GeminiTranslatorProvider
            api_key = self.config.api_keys.get("Gemini", "")
            return GeminiTranslatorProvider(api_key)
        else:
            from translator.google import GoogleTranslatorProvider
            return GoogleTranslatorProvider()

    def start_translation(self):
        if not self.items:
            return
            
        self.is_translating = True
        
        # Only translate selected items
        selected_items = [item for item in self.items if item.selected_for_rename]
        if not selected_items:
            self.is_translating = False
            return
            
        for item in selected_items:
            item.status = ItemStatus.TRANSLATING
            
        translator = self._get_translator()
        
        def translate_task():
            try:
                # Setup an event loop for async translation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Batch selected texts
                texts = [item.base_name for item in selected_items]
                
                translated_texts = loop.run_until_complete(
                    translator.translate_batch(
                        texts, 
                        self.config.source_language, 
                        self.config.target_language, 
                        self.config.translation_settings
                    )
                )
                
                for i, item in enumerate(selected_items):
                    item.update_translated_name(translated_texts[i], self.config.translation_settings.preserve_file_extension)
                    item.status = ItemStatus.READY
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Translation failed: {e}")
                for item in selected_items:
                    item.status = ItemStatus.ERROR
                    item.error_message = str(e)
                
            self.preview_window.rebuild_tree()
            self.is_translating = False

        self.worker.submit(translate_task)

    def start_renaming(self):
        self.is_renaming = True
        self.progress_window.is_open = True
        self.progress_window.reset()
        
        def progress_cb(current, total, item):
            self.progress_window.update(current, total, item)
            
        def rename_task():
            self.renamer.execute_batch(self.items, progress_cb)
            self.is_renaming = False
            self.progress_window.is_open = False
            print("Renaming complete")

        self.worker.submit(rename_task)

    def shutdown(self):
        self.worker.shutdown()
