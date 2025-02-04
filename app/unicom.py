from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.clock import Clock
from processImage import read,read_text


class UniComApp(MDApp):
    
    def build(self):
        # Set the window size to mobile size (360x640)
        Window.size = (360, 700)
        # Load the layout from the KV file (unicom.kv)
        return Builder.load_file("unicom.kv")

    def on_start(self):
        # Ensure the navigation drawer is closed by default when the app starts
        self.root.ids.nav_drawer.set_state("close")
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.root.ids.cam.play = False
        print(self.root.ids)

    def show_text_input(self):
        # Placeholder function for text input
        self.show_popup("Enter Text", "Text input function is a placeholder!")

    def start_speech_to_text(self):
        # Placeholder function for speech to text
        self.show_popup("Speech to Text", "Speech to Text function is a placeholder!")

    def start_ocr(self):
        # Placeholder function for OCR
        self.show_popup("OCR", "OCR function is a placeholder!")

    def show_popup(self, title, message):
        # Create the content for the dialog (MDBoxLayout in this case)
        content = MDDialogHeadlineText(text=title, halign="center")
        # Create the MDDialog and pass the content to it via content_cls
        self.dialog = MDDialog(content,MDDialogSupportingText(text=message, halign="center"))
        # Open the dialog
        self.dialog.open()

    def go_back(self):
        """Method to go back to the main screen."""
        self.root.ids.screen_manager.current = 'content_screen'

    def toggle_dark_mode(self, state):
        """Toggles between dark and light mode based on the toggle button state."""
        if state:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"


class CameraClick(FloatLayout):
    def capture(self):
        print(self)
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        try:
            camera = app.root.ids['camera']
            if  not camera.play :
                camera.export_to_png(f"data/IMG.png")
                print(f"Captured image as IMG.png")
                read()
        except KeyError:
            print("Camera widget not found.")


if __name__ == "__main__":
    app=UniComApp()
    app.run()
