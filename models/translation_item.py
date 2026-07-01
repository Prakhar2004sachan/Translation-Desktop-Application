from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from enum import Enum

class ItemType(Enum):
    FILE = "File"
    FOLDER = "Folder"

class ItemStatus(Enum):
    PENDING = "Pending"
    TRANSLATING = "Translating"
    READY = "Ready"
    RENAMING = "Renaming"
    COMPLETED = "Completed"
    ERROR = "Error"
    SKIPPED = "Skipped"

@dataclass
class TranslationItem:
    original_path: Path
    original_name: str
    item_type: ItemType
    relative_path: str = ""
    
    translated_name: str = ""
    new_path: Optional[Path] = None
    
    status: ItemStatus = ItemStatus.PENDING
    error_message: str = ""
    
    confidence: float = 0.0
    selected_for_rename: bool = True
    
    # Store split components if needed
    base_name: str = ""
    extension: str = ""
    
    def __post_init__(self):
        if self.item_type == ItemType.FILE:
            self.extension = self.original_path.suffix
            self.base_name = self.original_path.stem
        else:
            self.base_name = self.original_name
            self.extension = ""
            
        if not self.translated_name:
            self.translated_name = self.original_name
            
    def update_translated_name(self, name: str, preserve_extension: bool):
        if self.item_type == ItemType.FILE and preserve_extension:
            self.translated_name = f"{name}{self.extension}"
        else:
            self.translated_name = name
            
        self.new_path = self.original_path.with_name(self.translated_name)
