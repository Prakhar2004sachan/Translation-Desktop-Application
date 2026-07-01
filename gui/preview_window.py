from imgui_bundle import imgui, imspinner
from typing import List, Optional
from pathlib import Path
from models.translation_item import TranslationItem, ItemType

class TreeNode:
    def __init__(self, name: str, item: Optional[TranslationItem] = None):
        self.name = name
        self.item = item  # Only nodes corresponding to scanned items have the TranslationItem
        self.children = {} # name -> TreeNode

def build_tree(items: List[TranslationItem]) -> TreeNode:
    root_node = TreeNode("")
    for item in items:
        parts = Path(item.relative_path).parts
        current = root_node
        for i, part in enumerate(parts):
            if part not in current.children:
                if i == len(parts) - 1:
                    current.children[part] = TreeNode(part, item)
                else:
                    current.children[part] = TreeNode(part)
            else:
                # If it already exists but we now have the folder item itself, associate it
                if i == len(parts) - 1 and item.item_type == ItemType.FOLDER:
                    current.children[part].item = item
            current = current.children[part]
    return root_node

def node_matches_query(node: TreeNode, query: str) -> bool:
    if not query:
        return True
    if node.item:
        if query in node.item.relative_path.lower() or query in node.item.translated_name.lower():
            return True
    for child in node.children.values():
        if node_matches_query(child, query):
            return True
    return False

def get_descendant_items(node: TreeNode) -> List[TranslationItem]:
    items = []
    if node.item:
        items.append(node.item)
    for child in node.children.values():
        items.extend(get_descendant_items(child))
    return items

class PreviewWindow:
    def __init__(self):
        self._items: List[TranslationItem] = []
        self.tree_root: Optional[TreeNode] = None
        self.search_query = ""

    @property
    def items(self) -> List[TranslationItem]:
        return self._items

    @items.setter
    def items(self, value: List[TranslationItem]):
        self._items = value
        self.rebuild_tree()

    def rebuild_tree(self):
        self.tree_root = build_tree(self._items)

    def render(self, is_translating: bool = False, is_scanning: bool = False):
        if is_scanning:
            self._draw_centered_loading("##", "Scanning directory...")
            return
            
        if is_translating:
            self._draw_centered_loading("##", "Translating names using Gemini...")
            return

        if not self._items:
            imgui.text("No items scanned yet.")
            return

        # Search Bar and Select All / Deselect All
        avail_w = imgui.get_content_region_avail().x
        btn_width = 100.0
        spacing = imgui.get_style().item_spacing.x
        search_w = max(100.0, avail_w - (btn_width * 2) - (spacing * 2))
        
        imgui.set_next_item_width(search_w)
        changed, self.search_query = imgui.input_text("##SearchBox", self.search_query)
        
        imgui.same_line()
        if imgui.button("Select All", (btn_width, 0)):
            for item in self._items:
                item.selected_for_rename = True
                
        imgui.same_line()
        if imgui.button("Deselect All", (btn_width, 0)):
            for item in self._items:
                item.selected_for_rename = False

        total_count = len(self._items)
        selected_count = sum(1 for item in self._items if item.selected_for_rename)
        imgui.text_disabled(f"Selected: {selected_count} of {total_count} items")
        imgui.spacing()
        
        # Draw table
        flags = imgui.TableFlags_.borders | imgui.TableFlags_.row_bg | imgui.TableFlags_.resizable | imgui.TableFlags_.scroll_y
        if imgui.begin_table("preview_table", 5, flags):
            imgui.table_setup_column("Select", imgui.TableColumnFlags_.width_fixed, 50.0)
            imgui.table_setup_column("Type", imgui.TableColumnFlags_.width_fixed, 60.0)
            imgui.table_setup_column("Structure (Original Path)")
            imgui.table_setup_column("Translated Name")
            imgui.table_setup_column("Status", imgui.TableColumnFlags_.width_fixed, 90.0)
            imgui.table_headers_row()

            if self.tree_root:
                for child_name in sorted(self.tree_root.children.keys()):
                    self._render_tree_node(self.tree_root.children[child_name], self.search_query.lower())

            imgui.end_table()

    def _render_tree_node(self, node: TreeNode, query: str):
        if not node_matches_query(node, query):
            return

        imgui.table_next_row()
        
        # Column 0: Select Checkbox (Recursive for folder nodes!)
        imgui.table_set_column_index(0)
        descendants = get_descendant_items(node)
        if descendants:
            is_selected = all(item.selected_for_rename for item in descendants)
            changed, selected = imgui.checkbox(f"##sel_{id(node)}", is_selected)
            if changed:
                for item in descendants:
                    item.selected_for_rename = selected
        else:
            imgui.text("")

        # Column 1: Type (FILE or FOLDER)
        imgui.table_set_column_index(1)
        if node.item:
            imgui.text(node.item.item_type.name)
        else:
            imgui.text("FOLDER")

        # Column 2: Expandable Tree Node (Original name / relative path)
        imgui.table_set_column_index(2)
        is_leaf = len(node.children) == 0
        flags = imgui.TreeNodeFlags_.open_on_arrow | imgui.TreeNodeFlags_.open_on_double_click
        if is_leaf:
            flags |= imgui.TreeNodeFlags_.leaf
        if query:
            flags |= imgui.TreeNodeFlags_.default_open

        opened = imgui.tree_node_ex(node.name, flags)
        if node.item and imgui.is_item_hovered():
            imgui.set_tooltip(str(node.item.original_path))

        # Column 3: Editable Translated Name
        imgui.table_set_column_index(3)
        if node.item:
            imgui.set_next_item_width(-1)
            changed, new_val = imgui.input_text(f"##trans_{id(node.item)}", node.item.translated_name)
            if changed:
                node.item.translated_name = new_val
        else:
            imgui.text("")

        # Column 4: Status
        imgui.table_set_column_index(4)
        if node.item:
            # We show a nice status color
            from models.translation_item import ItemStatus
            if node.item.status == ItemStatus.READY:
                imgui.text_colored((0.2, 0.8, 0.2, 1.0), "Ready")
            elif node.item.status == ItemStatus.PENDING:
                imgui.text_colored((0.8, 0.8, 0.2, 1.0), "Pending")
            elif node.item.status == ItemStatus.ERROR:
                imgui.text_colored((0.8, 0.2, 0.2, 1.0), "Error")
                if imgui.is_item_hovered():
                    imgui.set_tooltip(node.item.error_message)
            else:
                imgui.text(node.item.status.value)
        else:
            imgui.text("")

        # If tree node is expanded, recursively render children
        if opened:
            for child_name in sorted(node.children.keys()):
                self._render_tree_node(node.children[child_name], query)
            imgui.tree_pop()

    def _draw_centered_loading(self, label: str, text: str):
        avail = imgui.get_content_region_avail()
        spinner_radius = 25.0
        spinner_thickness = 4.0
        
        pos_x = (avail.x - spinner_radius * 2) / 2.0
        pos_y = (avail.y - spinner_radius * 2) / 2.0 - 40.0
        
        # Center the cursor
        imgui.set_cursor_pos((imgui.get_cursor_pos().x + pos_x, imgui.get_cursor_pos().y + pos_y))
        
        color = imgui.ImColor(0.2, 0.6, 1.0, 1.0) # Premium blue color
        imspinner.spinner_twin_pulsar(label, spinner_radius, spinner_thickness, color)
        
        # Draw label underneath
        text_size = imgui.calc_text_size(text).x
        text_pos_x = (avail.x - text_size) / 2.0
        imgui.set_cursor_pos((imgui.get_cursor_pos().x + text_pos_x - pos_x, imgui.get_cursor_pos().y + spinner_radius * 2 + 15.0))
        imgui.text(text)
