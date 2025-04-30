import os
import tempfile
import threading
import re
import speech_recognition as sr
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivymd.uix.snackbar import Snackbar
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.clock import Clock
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from gtts import gTTS
import pygame
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel

Window.size = (360, 640)

KV_FILE = 'unicom.kv'

class UniComApp(MDApp):
    def build(self):
        self.title = 'UniCom Translator'
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        self.root = Builder.load_file(KV_FILE)

        self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")

        self.langs = {
            "English": "en",
            "French": "fr",
            "German": "de",
            "Hindi": "hi",
            "Spanish": "es",
            "Tamil": "ta",
            "Japanese": "ja",
            "Chinese": "zh"
        }

        self.recognition_langs = {
            "English": "en-US",
            "French": "fr-FR",
            "German": "de-DE",
            "Hindi": "hi-IN",
            "Spanish": "es-ES",
            "Tamil": "ta-IN",
            "Japanese": "ja-JP",
            "Chinese": "zh-CN"
        }

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

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.RECORD_AUDIO])

        pygame.mixer.init()

        return self.root

    def set_source_lang(self, lang):
        self.source_lang = lang
        self.root.ids.source_lang_spinner.text = lang
        self.menu_source.dismiss()
        try:
            self.root.ids.input_text.font_name = f"{lang}Font"
        except Exception as e:
            print(f"Font error for {lang}: {e}")

    def set_target_lang(self, lang):
        self.target_lang = lang
        self.root.ids.target_lang_spinner.text = lang
        self.menu_target.dismiss()

    def clean_text(self, text):
        return re.sub(r'[^\x00-\x7F\u0900-\u097F\u0B80-\u0BFF\u3040-\u30FF\u4E00-\u9FFF]+', ' ', text)

    def translate_text(self):
        input_text = self.root.ids.input_text.text.strip()
        if not input_text:
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
        translated_text = self.clean_text(translated_text)
        self.root.ids.output_text.text = translated_text

        try:
            self.root.ids.output_text.font_name = f"{self.target_lang}Font"
        except Exception as e:
            print(f"Font error for {self.target_lang}: {e}")

    def speak_output_text(self):
        text = self.root.ids.output_text.text.strip()
        if not text:
            Snackbar(text="No translated text to speak").open()
            return

        target_language = self.langs.get(self.target_lang, "en")

        try:
            tts = gTTS(text=text, lang=target_language, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name
                tts.save(temp_filename)

            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Unload the music to release the file
            pygame.mixer.music.unload()

            # Now safely delete the temporary file
            os.remove(temp_filename)

        except Exception as e:
            Snackbar(text=f"TTS Error: {str(e)}").open()

    def speech_to_text(self):
        content_label = MDLabel(text="Please speak now...")
        
        self.dialog = MDDialog(
            title="Listening",
            content_cls=content_label,
            size_hint=(0.8, 0.4)
        )
        self.dialog.open()

        threading.Thread(target=self._listen_and_transcribe, daemon=True).start()

    def _listen_and_transcribe(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                recog_lang = self.recognition_langs.get(self.source_lang, "en-US")
                text = recognizer.recognize_google(audio, language=recog_lang)
                text = str(text).strip()
                text = self.clean_text(text)

                Clock.schedule_once(lambda dt: self.set_input_text(text))

            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: Snackbar(text="Sorry, could not understand the audio.").open())
            except sr.RequestError:
                Clock.schedule_once(lambda dt: Snackbar(text="Speech Recognition service is unavailable.").open())
            except Exception as e:
                Clock.schedule_once(lambda dt: Snackbar(text=f"Error: {str(e)}").open())
            finally:
                Clock.schedule_once(lambda dt: self.dialog.dismiss())

    def set_input_text(self, text):
        try:
            self.root.ids.input_text.text = text
            self.root.ids.input_text.font_name = f"{self.source_lang}Font"
        except Exception as e:
            Snackbar(text=f"Font/Text Error: {str(e)}").open()

    def toggle_dark_mode(self, switch, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"


if __name__ == '__main__':
    UniComApp().run()