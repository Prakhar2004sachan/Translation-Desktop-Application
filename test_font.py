import sys
from imgui_bundle import imgui, immapp, hello_imgui
import os

def load_fonts():
    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    if os.path.exists(font_path):
        hello_imgui.load_font(font_path, 16.0)

def gui():
    imgui.text("Test: 你好")

params = immapp.RunnerParams()
params.callbacks.load_additional_fonts = load_fonts
params.callbacks.show_gui = gui
immapp.run(params)
