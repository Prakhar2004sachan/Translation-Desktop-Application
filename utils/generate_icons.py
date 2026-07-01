from PIL import Image
from pathlib import Path

def main():
    icon_dir = Path("assets/iconikai-icon-pack/web")
    png_path = icon_dir / "android-chrome-512x512.png"
    
    if not png_path.exists():
        # Fallback to look in parent directory assets/ if moved
        png_path = Path("assets/android-chrome-512x512.png")
        
    if not png_path.exists():
        print("Error: Icon source file android-chrome-512x512.png not found.")
        return
        
    img = Image.open(png_path)
    
    # Ensure assets directory exists
    Path("assets").mkdir(exist_ok=True)
    
    # Save as Windows ICO
    ico_path = Path("assets/icon.ico")
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (128, 128), (256, 256)])
    print(f"Successfully generated Windows icon: {ico_path}")
    
    # Save as macOS ICNS
    icns_path = Path("assets/icon.icns")
    # ICNS files require specific sizes (e.g. 16, 32, 64, 128, 256, 512)
    # Pillow handles this automatically if the source is large enough (512x512 is perfect)
    img.save(icns_path, format="ICNS")
    print(f"Successfully generated macOS icon: {icns_path}")

if __name__ == "__main__":
    main()
