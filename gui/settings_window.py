from imgui_bundle import imgui
from models.config import AppConfig

class SettingsWindow:
    def __init__(self, config: AppConfig):
        self.config = config
        self.is_open = False

    def render(self):
        if not self.is_open:
            return

        expanded, self.is_open = imgui.begin("Settings", True)
        if not expanded:
            imgui.end()
            return

        imgui.text("Translation Provider")
        providers = ["Google Translate", "DeepL", "OpenAI", "Gemini"]
        current = providers.index(self.config.provider) if self.config.provider in providers else 0
        changed, new_idx = imgui.combo("Provider", current, providers)
        if changed:
            self.config.provider = providers[new_idx]

        imgui.separator()
        imgui.text("API Keys (Stored locally)")
        
        for provider in ["DeepL", "OpenAI", "Gemini"]:
            key = self.config.api_keys.get(provider, "")
            changed, new_key = imgui.input_text(f"{provider} Key", key, flags=imgui.InputTextFlags_.password)
            if changed:
                self.config.api_keys[provider] = new_key

        imgui.separator()
        imgui.text("UI Theme")
        themes = ["Dark", "Light", "Classic"]
        current_theme = themes.index(self.config.theme) if self.config.theme in themes else 0
        changed, new_theme = imgui.combo("Theme", current_theme, themes)
        if changed:
            self.config.theme = themes[new_theme]
            self._apply_theme()

        if imgui.button("Save Settings"):
            self.config.save()
            self.is_open = False

        imgui.end()

    def _apply_theme(self):
        if self.config.theme == "Dark":
            imgui.style_colors_dark()
        elif self.config.theme == "Light":
            imgui.style_colors_light()
        else:
            imgui.style_colors_classic()
