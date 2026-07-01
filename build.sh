#!/bin/bash
set -e

echo "Cleaning up previous builds..."
rm -rf build dist *.spec

echo "Generating icons..."
source venv/bin/activate
python utils/generate_icons.py

echo "Building standalone macOS Application using PyInstaller..."
pyinstaller --clean --noconfirm --windowed \
    --icon=assets/icon.icns \
    --name="Translation Desktop Application" \
    --add-data "assets:assets" \
    main.py

echo "Creating macOS drag-and-drop DMG Installer..."
# Create temporary folder structure for DMG
DMG_TEMP="dist/dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copy the app bundle
cp -R "dist/Translation Desktop Application.app" "$DMG_TEMP/"

# Create symlink to /Applications inside the DMG folder
ln -s /Applications "$DMG_TEMP/Applications"

# Generate the DMG disk image using macOS hdiutil
DMG_PATH="dist/Translation-Desktop-Application-Installer.dmg"
rm -f "$DMG_PATH"

hdiutil create -volname "Translation Desktop Application" -srcfolder "$DMG_TEMP" -ov -format UDZO "$DMG_PATH"

# Clean up temp folder
rm -rf "$DMG_TEMP"

echo "Build complete!"
echo "App bundle: dist/Translation Desktop Application.app"
echo "DMG Installer: dist/Translation-Desktop-Application-Installer.dmg"
