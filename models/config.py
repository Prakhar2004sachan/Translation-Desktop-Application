import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

def get_user_data_dir() -> Path:
    path = Path.home() / ".rename_tools"
    path.mkdir(parents=True, exist_ok=True)
    return path

@dataclass
class TranslationSettings:
    translate_folders: bool = True
    translate_files: bool = True
    preserve_file_extension: bool = True
    preserve_numbers: bool = True
    preserve_dates: bool = True
    preserve_symbols: bool = True
    keep_acronyms: bool = True
    keep_uppercase: bool = False
    translate_underscores: bool = False
    translate_hyphens: bool = False
    replace_spaces: bool = False
    normalize_unicode: bool = True
    skip_hidden_files: bool = True
    skip_system_folders: bool = True
    skip_executable_files: bool = True
    skip_symbolic_links: bool = True

@dataclass
class FilterSettings:
    ignore_extensions: List[str] = field(default_factory=lambda: [".exe", ".dll", ".sys", ".zip", ".rar", ".7z", ".iso"])
    ignore_folders: List[str] = field(default_factory=lambda: [".git", "node_modules", "venv", "build", "dist", "__pycache__"])
    ignore_file_patterns: List[str] = field(default_factory=lambda: ["*.log", "*.tmp", "*.bak"])

@dataclass
class AppConfig:
    last_directory: str = ""
    window_width: int = 1200
    window_height: int = 800
    source_language: str = "Auto Detect"
    target_language: str = "English"
    provider: str = "Google Translate"
    api_keys: Dict[str, str] = field(default_factory=dict)
    theme: str = "Dark"
    recent_folders: List[str] = field(default_factory=list)
    translation_settings: TranslationSettings = field(default_factory=TranslationSettings)
    filter_settings: FilterSettings = field(default_factory=FilterSettings)
    def save(self, filepath: Optional[str] = None):
        if filepath is None:
            filepath = str(get_user_data_dir() / "config.json")
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, filepath: Optional[str] = None) -> "AppConfig":
        if filepath is None:
            filepath = str(get_user_data_dir() / "config.json")
        path = Path(filepath)
        if not path.exists():
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                
                # Reconstruct nested dataclasses
                translation_settings = TranslationSettings(**data.get("translation_settings", {}))
                filter_settings = FilterSettings(**data.get("filter_settings", {}))
                
                data["translation_settings"] = translation_settings
                data["filter_settings"] = filter_settings
                
                return cls(**data)
            except Exception:
                return cls()
