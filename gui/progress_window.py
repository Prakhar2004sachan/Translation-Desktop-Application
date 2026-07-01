from imgui_bundle import imgui

class ProgressWindow:
    def __init__(self):
        self.is_open = False
        self.current_folder = ""
        self.current_file = ""
        self.progress = 0.0
        self.total_items = 0
        self.current_item_idx = 0
        self.cancel_requested = False
        self.paused = False

    def reset(self):
        self.progress = 0.0
        self.current_folder = ""
        self.current_file = ""
        self.current_item_idx = 0
        self.total_items = 0
        self.cancel_requested = False
        self.paused = False

    def update(self, current_idx, total_items, item):
        self.current_item_idx = current_idx
        self.total_items = total_items
        self.progress = current_idx / total_items if total_items > 0 else 0
        if item.item_type.name == "FILE":
            self.current_file = item.original_name
            self.current_folder = item.original_path.parent.name
        else:
            self.current_folder = item.original_name

    def render(self):
        if not self.is_open:
            return

        imgui.set_next_window_size((500, 250), imgui.Cond_.first_use_ever)
        expanded, self.is_open = imgui.begin("Progress", True)
        if not expanded:
            imgui.end()
            return

        imgui.text("Renaming in progress...")
        imgui.progress_bar(self.progress, (-1.0, 0.0))

        imgui.text(f"Item: {self.current_item_idx} / {self.total_items}")
        imgui.text(f"Current Folder: {self.current_folder}")
        imgui.text(f"Current File: {self.current_file}")
        
        imgui.separator()

        if imgui.button("Cancel"):
            self.cancel_requested = True
        
        imgui.same_line()
        if imgui.button("Resume" if self.paused else "Pause"):
            self.paused = not self.paused

        imgui.end()
