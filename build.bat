@echo off
echo Cleaning up previous builds...
rd /s /q build dist 2>nul
del /q *.spec 2>nul

echo Generating icons...
call venv\Scripts\activate.bat
python utils\generate_icons.py

echo Building standalone Windows Application using PyInstaller...
:: On Windows, PyInstaller uses semicolon ';' as separator for data files.
pyinstaller --clean --noconfirm --windowed ^
    --icon=assets\icon.ico ^
    --name="Translation Desktop Application" ^
    --add-data "assets;assets" ^
    main.py

echo Build complete! Standalone executable created at: dist\Translation Desktop Application\
pause
