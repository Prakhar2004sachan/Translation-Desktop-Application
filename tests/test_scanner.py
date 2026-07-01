from pathlib import Path
from filesystem.scanner import DirectoryScanner
from models.translation_item import ItemType

def test_scanner_finds_all_items_except_ignored(temp_dir, filter_settings):
    scanner = DirectoryScanner(filter_settings)
    items = list(scanner.scan(temp_dir))
    
    # We expect:
    # Folders: folder1, folder1/subfolder, folder2
    # Files: folder1/file1.txt, folder1/file2.jpg, folder1/subfolder/file3.png, folder2/file4.srt
    # Skipped: ignored_folder (and all its contents), ignored.sys
    
    expected_folders = {"folder1", "folder1/subfolder", "folder2"}
    expected_files = {"folder1/file1.txt", "folder1/file2.jpg", "folder1/subfolder/file3.png", "folder2/file4.srt"}
    
    found_folders = {item.relative_path for item in items if item.item_type == ItemType.FOLDER}
    found_files = {item.relative_path for item in items if item.item_type == ItemType.FILE}
    
    assert found_folders == expected_folders
    assert found_files == expected_files

def test_scanner_relative_path_and_properties(temp_dir, filter_settings):
    scanner = DirectoryScanner(filter_settings)
    items = list(scanner.scan(temp_dir))
    
    for item in items:
        # Verify relative path math is correct
        assert item.original_path.relative_to(temp_dir) == Path(item.relative_path)
        
        # Verify base_name and extension properties are set correctly
        if item.item_type == ItemType.FILE:
            assert item.extension == item.original_path.suffix
            assert item.base_name == item.original_path.stem
        else:
            assert item.base_name == item.original_name
            assert item.extension == ""
