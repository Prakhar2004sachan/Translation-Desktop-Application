import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class UndoManager:
    def __init__(self, history_file: str = "logs/undo_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.operations: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self):
        with open(self.history_file, "w") as f:
            json.dump(self.operations, f, indent=4)

    def record_rename(self, original_path: str, new_path: str):
        self.operations.append({
            "original_path": original_path,
            "new_path": new_path,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def undo_last_batch(self, count: int = 10):
        """
        Reverse the last 'count' renaming operations.
        Actually renames them back on the filesystem.
        """
        if not self.operations:
            return 0
            
        ops_to_undo = self.operations[-count:]
        undone = 0
        
        # We must iterate backwards to ensure children are renamed back before parents if they were somehow ordered weirdly
        for op in reversed(ops_to_undo):
            original = Path(op["original_path"])
            current = Path(op["new_path"])
            
            if current.exists():
                try:
                    current.rename(original)
                    undone += 1
                except Exception as e:
                    print(f"Failed to undo {current} -> {original}: {e}")
            
            self.operations.remove(op)
            
        self._save()
        return undone
