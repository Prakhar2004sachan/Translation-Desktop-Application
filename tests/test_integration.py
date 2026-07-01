import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app import App
from models.config import AppConfig
from models.translation_item import ItemStatus
from utils.background_worker import BackgroundWorker

@pytest.mark.asyncio
async def test_integration_flow(temp_dir):
    # Setup mock configuration
    config = AppConfig()
    config.last_directory = str(temp_dir)
    config.provider = "Gemini"
    config.api_keys["Gemini"] = "mock_key"
    config.filter_settings.ignore_folders.append("ignored_folder")
    
    from filesystem.renamer import Renamer
    with patch("models.config.AppConfig.load", return_value=config):
        app = App()
        
    app.renamer = Renamer(history_file=str(temp_dir / "undo_history.json"))
        
    assert len(app.items) == 0
    
    # 1. Run Scan Directory
    app.start_scan()
    # Wait for the background scan task to complete
    app.worker.executor.shutdown(wait=True)
    # Re-instantiate background worker since shutdown() closes the pool
    app.worker = BackgroundWorker(max_workers=2)
    
    # We should have 7 scanned items (ignored items skipped)
    assert len(app.items) == 7
    for item in app.items:
        assert item.status == ItemStatus.PENDING
        assert item.translated_name == item.original_name
        
    # 2. Select/Deselect items:
    # Deselect folder2 and folder2/file4.srt
    for item in app.items:
        if "folder2" in item.relative_path:
            item.selected_for_rename = False
            
    # 3. Translate Selected
    # Mock the Gemini client response
    mock_client = MagicMock()
    mock_response = MagicMock()
    # - folder1
    # - folder1/subfolder
    # - folder1/file1.txt
    # - folder1/file2.jpg
    # - folder1/subfolder/file3.png
    mock_response.text = '["FolderA", "SubfolderB", "FileA", "FileB", "FileC"]'
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("google.genai.Client", return_value=mock_client):
        app.start_translation()
        # Wait for translation to complete
        app.worker.executor.shutdown(wait=True)
        app.worker = BackgroundWorker(max_workers=2)
        
    # Verify translation results
    for item in app.items:
        if item.selected_for_rename:
            assert item.status == ItemStatus.READY
            assert item.translated_name != item.original_name
        else:
            assert item.status == ItemStatus.PENDING
            assert item.translated_name == item.original_name
            
    # 4. Start Renaming
    app.start_renaming()
    # Wait for renaming to complete
    app.worker.executor.shutdown(wait=True)
    
    # Diagnostic prints
    print("\nFILESYSTEM STATE AFTER RENAME:")
    for path in temp_dir.rglob("*"):
        print(f"  Exist: {path.relative_to(temp_dir)}")
        
    print("\nITEMS STATE AFTER RENAME:")
    for item in app.items:
        print(f"  Item: original_path={item.original_path.relative_to(temp_dir) if item.original_path.exists() else item.original_path.name} status={item.status} error={item.error_message} new_path={item.new_path}")
    
    # Verify filesystem state
    assert (temp_dir / "FolderA").exists()
    assert (temp_dir / "FolderA" / "FileA.txt").exists()
    assert (temp_dir / "FolderA" / "SubfolderB" / "FileC.png").exists()
    # Unselected folder2 remains unchanged
    assert (temp_dir / "folder2").exists()
    assert (temp_dir / "folder2" / "file4.srt").exists()
