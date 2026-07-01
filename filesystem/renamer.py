from typing import List
from models.translation_item import TranslationItem, ItemStatus
from filesystem.validator import PathValidator
from filesystem.undo import UndoManager
import os
import shutil

class Renamer:
    def __init__(self, history_file: str = "logs/undo_history.json"):
        self.validator = PathValidator()
        self.undo_manager = UndoManager(history_file)

    def execute_batch(self, items: List[TranslationItem], progress_callback=None):
        """
        Executes a batch of renames.
        MUST sort deepest paths first to prevent invalidating paths!
        """
        # Sort items by depth descending (deepest first)
        sorted_items = sorted(
            [item for item in items if item.selected_for_rename and item.new_path],
            key=lambda x: len(x.original_path.parts),
            reverse=True
        )

        total = len(sorted_items)
        
        for i, item in enumerate(sorted_items):
            try:
                # Need to recalculate original path just in case a parent directory was already renamed 
                # wait, if we sort deepest first, a child is renamed before its parent.
                # So the child's path is still valid because the parent hasn't been renamed yet!
                if not item.original_path.exists():
                    item.status = ItemStatus.ERROR
                    item.error_message = "File not found"
                    continue

                # Ensure valid filename
                safe_name = self.validator.validate_and_correct(item.translated_name)
                # Rebuild new path with safe name
                temp_new_path = item.original_path.with_name(safe_name)
                
                # Resolve collisions
                final_new_path = self.validator.resolve_collision(temp_new_path)
                
                item.status = ItemStatus.RENAMING
                
                # Perform rename
                item.original_path.rename(final_new_path)
                
                # Record undo
                self.undo_manager.record_rename(
                    str(item.original_path),
                    str(final_new_path)
                )
                
                item.status = ItemStatus.COMPLETED
                item.new_path = final_new_path # Update to final resolved path
                
            except Exception as e:
                item.status = ItemStatus.ERROR
                item.error_message = str(e)
                
            if progress_callback:
                progress_callback(i + 1, total, item)

        return True
