from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu
from kivymd.theming import ThemeManager
from kivy.core.window import Window
from kivymd.uix.button import MDRaisedButton
from kivy.utils import platform
from kivymd.uix.snackbar import Snackbar

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch

Window.size = (360, 640)

KV_FILE = 'unicom.kv'

class UniComApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.title = 'UniCom Translator'

        # Load UI
        self.root = Builder.load_file(KV_FILE)

        # Load language model
        self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")

        # Languages for dropdown
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
        generated_tokens = self.model.generate(**encoded, forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang_code))
        translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

        self.root.ids.output_text.text = translated_text

    def toggle_dark_mode(self, is_dark):
        self.theme_cls.theme_style = "Dark" if is_dark else "Light"


if __name__ == '__main__':
    UniComApp().run()