from pathlib import Path
from filesystem.renamer import Renamer
from filesystem.scanner import DirectoryScanner
from models.translation_item import ItemStatus, ItemType

def test_renamer_executes_batch_successfully(temp_dir, filter_settings, translation_settings):
    scanner = DirectoryScanner(filter_settings)
    items = list(scanner.scan(temp_dir))
    
    # Let's mock translations for a few selected items
    # We will rename:
    # folder1 -> folderA
    # folder1/subfolder -> folderA/subfolderB
    # folder1/subfolder/file3.png -> folderA/subfolderB/fileC.png
    
    for item in items:
        if item.relative_path == "folder1":
            item.update_translated_name("folderA", translation_settings.preserve_file_extension)
        elif item.relative_path == "folder1/subfolder":
            item.update_translated_name("subfolderB", translation_settings.preserve_file_extension)
        elif item.relative_path == "folder1/subfolder/file3.png":
            item.update_translated_name("fileC", translation_settings.preserve_file_extension)
        else:
            # Deselect the rest so they don't get renamed
            item.selected_for_rename = False
            
    renamer = Renamer(history_file=str(temp_dir / "undo_history.json"))
    success = renamer.execute_batch(items)
    
    assert success is True
    
    # Verify the paths on disk have changed correctly!
    assert (temp_dir / "folderA").exists()
    assert (temp_dir / "folderA" / "subfolderB").exists()
    assert (temp_dir / "folderA" / "subfolderB" / "fileC.png").exists()
    
    # Verify non-selected files are unchanged (parent folder is renamed, but the filename is original)
    assert (temp_dir / "folderA" / "file1.txt").exists()

def test_renamer_undo_batch(temp_dir, filter_settings, translation_settings):
    scanner = DirectoryScanner(filter_settings)
    items = list(scanner.scan(temp_dir))
    
    # Translate and select folder1 and folder1/file1.txt
    for item in items:
        if item.relative_path == "folder1":
            item.update_translated_name("folderA", translation_settings.preserve_file_extension)
        elif item.relative_path == "folder1/file1.txt":
            item.update_translated_name("fileA", translation_settings.preserve_file_extension)
        else:
            item.selected_for_rename = False
            
    renamer = Renamer(history_file=str(temp_dir / "undo_history.json"))
    assert renamer.execute_batch(items) is True
    
    # Verify renamed state
    assert (temp_dir / "folderA").exists()
    assert (temp_dir / "folderA" / "fileA.txt").exists()
    assert not (temp_dir / "folder1").exists()
    
    # Perform undo!
    undone_count = renamer.undo_manager.undo_last_batch()
    assert undone_count == 2
    
    # Verify restored state
    assert (temp_dir / "folder1").exists()
    assert (temp_dir / "folder1" / "file1.txt").exists()
    assert not (temp_dir / "folderA").exists()
