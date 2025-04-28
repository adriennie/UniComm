from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar
from kivy.core.text import LabelBase
from kivy.utils import platform

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from gtts import gTTS
from playsound import playsound

import os
import tempfile

Window.size = (360, 640)

KV_FILE = 'unicom.kv'

class UniComApp(MDApp):
    def build(self):
        self.title = 'UniCom Translator'
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Load UI
        self.root = Builder.load_file(KV_FILE)

        # Load translation model
        self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")

        # Language codes
        self.langs = {
            "English": "en",
            "French": "fr",
            "German": "de",
            "Hindi": "hi",
            "Spanish": "es",
            "Tamil": "ta",
            "Japanese": "ja",
            "Chinese": "zh",
        }

        # Font registration
        self.fonts = {
            "English": "assets/fonts/NotoSans-Regular.ttf",
            "French": "assets/fonts/NotoSans-Regular.ttf",
            "German": "assets/fonts/NotoSans-Regular.ttf",
            "Hindi": "assets/fonts/NotoSansDevanagari-Regular.ttf",
            "Spanish": "assets/fonts/NotoSans-Regular.ttf",
            "Tamil": "assets/fonts/NotoSansTamil-Regular.ttf",
            "Japanese": "assets/fonts/NotoSansCJKjp-Regular.otf",
            "Chinese": "assets/fonts/NotoSansCJKjp-Regular.otf",
        }

        for lang, font_path in self.fonts.items():
            try:
                LabelBase.register(name=f"{lang}Font", fn_regular=font_path)
            except Exception as e:
                print(f"Could not register font for {lang}: {e}")

        # Dropdown Menus
        menu_items_source = [
            {"text": lang, "on_release": lambda x=lang: self.set_source_lang(x)} for lang in self.langs
        ]
        self.menu_source = MDDropdownMenu(
            caller=self.root.ids.source_lang_spinner,
            items=menu_items_source,
            width_mult=4
        )

        menu_items_target = [
            {"text": lang, "on_release": lambda x=lang: self.set_target_lang(x)} for lang in self.langs
        ]
        self.menu_target = MDDropdownMenu(
            caller=self.root.ids.target_lang_spinner,
            items=menu_items_target,
            width_mult=4
        )

        self.source_lang = "English"
        self.target_lang = "French"

        self.root.ids.source_lang_spinner.text = self.source_lang
        self.root.ids.target_lang_spinner.text = self.target_lang

        return self.root

    def set_source_lang(self, lang):
        self.source_lang = lang
        self.root.ids.source_lang_spinner.text = lang
        self.menu_source.dismiss()

    def set_target_lang(self, lang):
        self.target_lang = lang
        self.root.ids.target_lang_spinner.text = lang
        self.menu_target.dismiss()

    def translate_text(self):
        input_text = self.root.ids.input_text.text
        if not input_text.strip():
            Snackbar(text="Please enter text to translate").open()
            return

        src_lang_code = self.langs[self.source_lang]
        tgt_lang_code = self.langs[self.target_lang]

        self.tokenizer.src_lang = src_lang_code

        encoded = self.tokenizer(input_text, return_tensors="pt")
        generated_tokens = self.model.generate(
            **encoded,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang_code)
        )
        translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        self.root.ids.output_text.text = translated_text

        # Apply correct font
        try:
            self.root.ids.output_text.font_name = f"{self.target_lang}Font"
        except Exception as e:
            print(f"Font error for {self.target_lang}: {e}")

    def speak_output_text(self):
        text = self.root.ids.output_text.text
        if not text.strip():
            Snackbar(text="No translated text to speak").open()
            return

        target_language = self.langs.get(self.target_lang, "en")

        try:
            tts = gTTS(text=text, lang=target_language)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name
                tts.save(temp_filename)

            playsound(temp_filename)

            # Clean up
            os.remove(temp_filename)

        except Exception as e:
            Snackbar(text=f"Error in speech: {str(e)}").open()

    def toggle_dark_mode(self, switch, value):
        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

if __name__ == '__main__':
    UniComApp().run()
