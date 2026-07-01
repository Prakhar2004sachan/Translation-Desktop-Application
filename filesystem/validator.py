import os
from pathlib import Path
from utils.unicode import sanitize_filename, normalize_text

class PathValidator:
    def __init__(self):
        # Windows reserved names
        self.reserved_names = {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }

    def validate_and_correct(self, filename: str) -> str:
        # Check reserved
        base = filename.split('.')[0].upper()
        if base in self.reserved_names:
            filename = f"renamed_{filename}"

        # Sanitize
        filename = sanitize_filename(filename)
        
        # Max length
        # Typically 255 chars for filename
        if len(filename) > 240:
            name, ext = os.path.splitext(filename)
            filename = name[:240 - len(ext)] + ext

        return normalize_text(filename)

    def resolve_collision(self, target_path: Path) -> Path:
        """
        If target_path exists, append (1), (2), etc.
        """
        if not target_path.exists():
            return target_path

        directory = target_path.parent
        stem = target_path.stem
        ext = target_path.suffix

        counter = 1
        while True:
            new_name = f"{stem} ({counter}){ext}"
            new_path = directory / new_name
            if not new_path.exists():
                return new_path
            counter += 1
