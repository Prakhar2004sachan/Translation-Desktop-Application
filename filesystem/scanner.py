from pathlib import Path
from typing import List, Generator
from models.config import FilterSettings
from models.translation_item import TranslationItem, ItemType
import os

class DirectoryScanner:
    def __init__(self, filter_settings: FilterSettings):
        self.filters = filter_settings

    def is_ignored(self, path: Path) -> bool:
        # Ignore folders
        for folder in self.filters.ignore_folders:
            if folder in path.parts:
                return True
        
        # Ignore extensions
        if path.is_file() and path.suffix.lower() in [ext.lower() for ext in self.filters.ignore_extensions]:
            return True
            
        return False

    def scan(self, root_dir: Path) -> Generator[TranslationItem, None, None]:
        for root, dirs, files in os.walk(root_dir, topdown=True):
            # Mutate dirs in place to prevent os.walk from descending into ignored dirs
            dirs[:] = [d for d in dirs if not self.is_ignored(Path(root) / d)]
            
            for d in dirs:
                dir_path = Path(root) / d
                if not self.is_ignored(dir_path):
                    yield TranslationItem(
                        original_path=dir_path,
                        original_name=d,
                        item_type=ItemType.FOLDER,
                        relative_path=str(dir_path.relative_to(root_dir))
                    )
            
            for f in files:
                file_path = Path(root) / f
                if not self.is_ignored(file_path):
                    yield TranslationItem(
                        original_path=file_path,
                        original_name=f,
                        item_type=ItemType.FILE,
                        relative_path=str(file_path.relative_to(root_dir))
                    )
