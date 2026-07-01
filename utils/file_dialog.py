import tkinter as tk
from tkinter import filedialog
import sys

def main():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    if folder_path:
        print(folder_path)

if __name__ == "__main__":
    main()
