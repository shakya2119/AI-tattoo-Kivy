import openai
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# Set your OpenAI API key
openai.api_key = 'api_key'

class ImageGeneratorApp(App):
    def build(self):
        self.membership_levels = {'Basic': 9.99, 'Premium': 39.99, 'Pro': 69.99}
        self.selected_button = None
        self.selected_level = None

        # Set background color to sky blue
        Window.clearcolor = (0.529, 0.808, 0.922, 1)

        main_layout = BoxLayout(orientation='vertical',  width=1179, height=2556, padding=10, spacing=10)

        # Headline
        headline_label = Label(text='ARTBOX', size_hint=(1, None), height=50, font_size='36sp', color=(0, 0, 1, 1), font_family='Segoe Print')
        main_layout.add_widget(headline_label)

        # Input prompt
        self.input_prompt = TextInput(hint_text='Enter your prompt', size_hint=(None, None), width=400, height=50)
        main_layout.add_widget(self.input_prompt)

        # Button to generate images
        self.generate_button = Button(text='Generate', size_hint=(None, None), width=400, height=50, background_color=(0, 0, 1, 1))
        self.generate_button.bind(on_press=self.generate_image)
        main_layout.add_widget(self.generate_button)

        # GridLayout for membership buttons and renew button
        membership_layout = GridLayout(cols=2, spacing=10, size_hint=(1, None), height=110)
        self.membership_buttons = {}
        for level, price in self.membership_levels.items():
            button_text = f"{level}: ${price}/month"
            button = Button(text=button_text, size_hint=(None, None), size=(200, 50))
            button.bind(on_press=self.on_membership_select)
            membership_layout.add_widget(button)
            self.membership_buttons[level] = button

        # Renew Plan button
        self.renew_button = Button(text='Renew Plan', size_hint=(None, None), size=(200, 50), background_color=(1, 0, 0, 1))
        self.renew_button.bind(on_press=self.renew_membership)
        membership_layout.add_widget(self.renew_button)

        # Adding an empty widget to fill the space in the GridLayout
        empty_widget = Label(size_hint=(None, None), size=(200, 50))
        membership_layout.add_widget(empty_widget)

        main_layout.add_widget(membership_layout)

        # ScrollView to contain the image layout
        self.scroll_view = ScrollView(size_hint=(1, 1))

        # Layout for images inside the ScrollView
        self.image_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.image_layout.bind(minimum_height=self.image_layout.setter('height'))

        # Adding initial placeholder labels
        self.image_widgets = []
        for _ in range(15):  # Placeholder for initial images based on Basic level
            label = Label(text='Image will appear here', size_hint=(None, None), size=(200, 200))
            self.image_layout.add_widget(label)
            self.image_widgets.append(label)

        self.scroll_view.add_widget(self.image_layout)
        main_layout.add_widget(self.scroll_view)

        self.scroll_view.bar_color = (0, 0, 0, 1)  # Set scrollbar color to black

        return main_layout

    def on_membership_select(self, instance):
        # Reset background color of previously selected button
        if self.selected_button:
            self.selected_button.background_color = (1, 1, 1, 1)  # White color

        # Set background color of the newly selected button
        instance.background_color = (0, 1, 0, 1)  # Green color
        self.selected_button = instance

        self.selected_level = instance.text.split(':')[0]
        # Update image widgets and other parameters based on the selected membership level
        for button in self.membership_buttons.values():
            if button != instance:
                button.disabled = True  # Disable other buttons after selection
        self.generate_button.text = 'Generate'
        # Adjust other parameters like storage capacity, etc.

    def renew_membership(self, instance):
        # Reset the background color of the renew button
        self.renew_button.background_color = (1, 0, 0, 1)  # Red color

        # Reset selected membership level
        self.selected_level = None

        # Enable all membership buttons
        for button in self.membership_buttons.values():
            button.disabled = False

        # Reset generate button text
        self.generate_button.text = 'Generate'

        # Reset background color of the previously selected button
        if self.selected_button:
            self.selected_button.background_color = (1, 1, 1, 1)  # White color
            self.selected_button = None

    def generate_image(self, instance):
        # Get the user prompt
        prompt = self.input_prompt.text

        # Check if a membership level is selected
        if not self.selected_level:
            self.show_popup("Error", "Please select a membership plan.")
            return

        # Check if the prompt is empty
        if not prompt:
            self.show_popup("Error", "Please enter a prompt.")
            return

        # Determine the number of images based on the selected membership level
        if self.selected_level == 'Premium':
            num_images = 7
        elif self.selected_level == 'Pro':
            num_images = 10
        else:
            # Default to 5 images for Basic membership
            num_images = 5

        # Call OpenAI to generate images based on the prompt
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=num_images,  # Number of images based on selected membership level
                size="512x512"
            )

            # Clear existing images
            for widget in self.image_widgets:
                self.image_layout.remove_widget(widget)
            self.image_widgets.clear()

            # Update image widgets with the URLs of the generated images
            for data in response['data']:
                image_url = data['url']
                image = AsyncImage(source=image_url, size_hint=(None, None), size=(200, 200))
                image.bind(on_touch_down=self.on_image_click)
                self.image_layout.add_widget(image)
                self.image_widgets.append(image)

        except Exception as e:
            self.show_popup("Error", f"Error generating images: {e}")

    def on_image_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Create a popup with the clicked image
            popup_layout = BoxLayout(orientation='vertical')
            popup_image = AsyncImage(source=instance.source, size_hint=(1, 1))
            button_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)
            close_button = Button(text='Close')
            download_button = Button(text='Download')

            button_layout.add_widget(close_button)
            button_layout.add_widget(download_button)

            popup_layout.add_widget(popup_image)
            popup_layout.add_widget(button_layout)

            popup = Popup(title='Image Preview', content=popup_layout, size_hint=(0.9, 0.9))
            close_button.bind(on_press=popup.dismiss)
            download_button.bind(on_press=lambda x: self.download_image(instance.source))

            popup.open()
            return True
        return False

    def download_image(self, image_url):
        # Define the download path and filename
        file_path = f"downloaded_image.jpg"

        # Download the image
        try:
            urllib.request.urlretrieve(image_url, file_path)
            print(f"Image successfully downloaded to {file_path}")
        except Exception as e:
            self.show_popup("Error", f"Error downloading image: {e}")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message_label = Label(text=message, size_hint=(1, None), height=50)
        close_button = Button(text='X', size_hint=(None, None), size=(20, 20), background_color=(1, 0, 0, 1))

    # Horizontal layout for close button
        close_layout = BoxLayout(size_hint=(1, None), height=50, padding=5, spacing=5)
        close_layout.add_widget(Label())  # Empty space to push the button to the right
        close_layout.add_widget(close_button)

        popup_layout.add_widget(close_layout)
        popup_layout.add_widget(message_label)

        popup = Popup(title=title, content=popup_layout, size_hint=(None, None), size=(300, 150))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    ImageGeneratorApp().run()
