from imgui_bundle import imgui
from models.config import AppConfig
import subprocess
import sys

class MainWindow:
    def __init__(self, config: AppConfig):
        self.config = config
        self.directory_input = self.config.last_directory
        self.languages = [
            "Auto Detect", "English", "Hindi", "Japanese", "Chinese", 
            "Korean", "Russian", "Spanish", "German", "French", "Italian", "Portuguese"
        ]

    def render(self, selected_count: int = 0) -> tuple[bool, bool, bool]:
        """Returns (scan_requested, translate_requested, settings_requested)"""
        scan_requested = False
        translate_requested = False
        settings_requested = False
        
        imgui.text("Translation Settings")
        imgui.spacing()
        
        # Label above input for cleaner design
        imgui.text_disabled("Target Directory:")
        
        # Calculate dynamic width for input box to fill space next to Browse button
        avail_width = imgui.get_content_region_avail().x
        browse_btn_width = 80.0
        spacing = imgui.get_style().item_spacing.x
        
        imgui.set_next_item_width(avail_width - browse_btn_width - spacing)
        changed, self.directory_input = imgui.input_text("##DirectoryInput", self.directory_input)
        if changed:
            self.config.last_directory = self.directory_input
            
        imgui.same_line()
        if imgui.button("Browse...", (browse_btn_width, 0)):
            try:
                import platform
                if platform.system() == "Darwin":
                    cmd = ["osascript", "-e", 'POSIX path of (choose folder with prompt "Select Directory")']
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        folder_path = result.stdout.strip()
                        if folder_path:
                            self.directory_input = folder_path
                            self.config.last_directory = folder_path
                elif platform.system() == "Windows":
                    ps_cmd = (
                        "Add-Type -AssemblyName System.Windows.Forms; "
                        "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                        "if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"
                    )
                    cmd = ["powershell", "-Command", ps_cmd]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        folder_path = result.stdout.strip()
                        if folder_path:
                            self.directory_input = folder_path
                            self.config.last_directory = folder_path
            except Exception as e:
                print(f"Error opening dialog: {e}")

        imgui.spacing()

        # Languages
        imgui.text_disabled("Source Language:")
        imgui.set_next_item_width(-1)
        src_idx = self.languages.index(self.config.source_language) if self.config.source_language in self.languages else 0
        changed, new_src = imgui.combo("##Source", src_idx, self.languages)
        if changed: self.config.source_language = self.languages[new_src]
        
        # Swap Button spanning full width
        if imgui.button("Swap Languages", (-1, 0)):
            if self.config.source_language != "Auto Detect":
                self.config.source_language, self.config.target_language = self.config.target_language, self.config.source_language
        
        imgui.text_disabled("Target Language:")
        imgui.set_next_item_width(-1)
        tgt_idx = self.languages.index(self.config.target_language) if self.config.target_language in self.languages else 1
        changed, new_tgt = imgui.combo("##Target", tgt_idx, self.languages)
        if changed: self.config.target_language = self.languages[new_tgt]

        imgui.separator()
        imgui.spacing()
        
        # Translation Options
        ts = self.config.translation_settings
        changed, val = imgui.checkbox("Translate Folders", ts.translate_folders); ts.translate_folders = val
        imgui.same_line()
        changed, val = imgui.checkbox("Translate Files", ts.translate_files); ts.translate_files = val
        
        changed, val = imgui.checkbox("Preserve File Extension", ts.preserve_file_extension); ts.preserve_file_extension = val
        
        imgui.separator()
        imgui.spacing()
        
        # Control Action Buttons
        if imgui.button("Scan Directory", (-1, 40)):
            scan_requested = True
            
        imgui.spacing()
        translate_label = f"Translate Selected ({selected_count})"
        if imgui.button(translate_label, (-1, 40)):
            translate_requested = True
            
        imgui.spacing()
        if imgui.button("Settings", (-1, 40)):
            settings_requested = True
            
        return scan_requested, translate_requested, settings_requested
