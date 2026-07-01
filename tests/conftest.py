import pytest
from pathlib import Path
from models.config import FilterSettings, TranslationSettings

@pytest.fixture
def temp_dir(tmp_path):
    # Set up a mock folder structure for tests:
    # rename_test/
    #   folder1/
    #     file1.txt
    #     file2.jpg
    #     subfolder/
    #       file3.png
    #   folder2/
    #     file4.srt
    #   ignored_folder/
    #     file5.txt
    #   ignored.sys
    
    d = tmp_path / "rename_test"
    d.mkdir()
    
    f1 = d / "folder1"
    f1.mkdir()
    (f1 / "file1.txt").write_text("data")
    (f1 / "file2.jpg").write_text("data")
    
    sf = f1 / "subfolder"
    sf.mkdir()
    (sf / "file3.png").write_text("data")
    
    f2 = d / "folder2"
    f2.mkdir()
    (f2 / "file4.srt").write_text("data")
    
    ig_f = d / "ignored_folder"
    ig_f.mkdir()
    (ig_f / "file5.txt").write_text("data")
    
    (d / "ignored.sys").write_text("data")
    
    return d

@pytest.fixture
def filter_settings():
    return FilterSettings(
        ignore_extensions=[".sys"],
        ignore_folders=["ignored_folder"],
        ignore_file_patterns=[]
    )

@pytest.fixture
def translation_settings():
    return TranslationSettings(
        translate_folders=True,
        translate_files=True,
        preserve_file_extension=True
    )
