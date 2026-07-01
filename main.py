import sys
from imgui_bundle import imgui, immapp, hello_imgui
from app import App

def main():
    app_instance = App()
    
    runner_params = immapp.RunnerParams()
    runner_params.app_window_params.window_title = "Translation Desktop Application"
    runner_params.app_window_params.window_geometry.size = (1200, 800)
    
    def load_fonts():
        import os
        from imgui_bundle import hello_imgui
        
        # We need a font that supports CJK.
        font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        
        # Load the font if it exists. hello_imgui will try to load standard ranges.
        # We must set inside_assets=False because it's an absolute system path
        if os.path.exists(font_path):
            params = hello_imgui.FontLoadingParams()
            params.inside_assets = False
            hello_imgui.load_font(font_path, 16.0, params)
            
    def gui():
        app_instance.render()
        
    runner_params.callbacks.load_additional_fonts = load_fonts
    runner_params.callbacks.show_gui = gui
    
    # Run the application
    immapp.run(runner_params)

    # Save config and shutdown threadpool
    app_instance.config.save()
    app_instance.shutdown()

if __name__ == "__main__":
    main()
