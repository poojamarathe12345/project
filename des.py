import os
import requests
import shutil
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock


class WebScraperApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # URL Input
        self.url_input = TextInput(hint_text="Enter website URL", multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.url_input)

        # Scrape Button
        self.scrape_button = Button(text="Scrape Website", size_hint=(1, 0.1))
        self.scrape_button.bind(on_press=self.start_scraping)
        self.layout.add_widget(self.scrape_button)

        # Result Labels
        self.img_label = Label(text="Images Found: 0", size_hint=(1, 0.1))
        self.layout.add_widget(self.img_label)

        self.link_label = Label(text="Links Found: 0", size_hint=(1, 0.1))
        self.layout.add_widget(self.link_label)

        # Log Output
        self.log_label = Label(text="Status: Waiting for input...", size_hint=(1, 0.2))
        self.layout.add_widget(self.log_label)

        return self.layout

    def start_scraping(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.log_label.text = "Status: Please enter a valid URL."
            return

        self.log_label.text = "Status: Scraping website..."
        Clock.schedule_once(lambda dt: self.scrape_website(url), 0.1)

    def scrape_website(self, url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.log_label.text = f"Error: {e}"
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Count Images & Links
        img_tags = soup.find_all("img")
        link_tags = soup.find_all("a")

        self.img_label.text = f"Images Found: {len(img_tags)}"
        self.link_label.text = f"Links Found: {len(link_tags)}"

        # Download Images
        os.makedirs("downloaded_images", exist_ok=True)
        count = 1

        for img in img_tags:
            try:
                img_src = img.get("src")
                if not img_src:
                    continue

                img_url = urljoin(url, img_src)  # Convert relative URL to absolute
                img_ext = os.path.splitext(img_url)[-1]  # Extract extension

                if img_ext.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".svg"]:
                    continue

                img_path = f"downloaded_images/image_{count}{img_ext}"
                img_data = requests.get(img_url, stream=True)

                with open(img_path, "wb") as f:
                    shutil.copyfileobj(img_data.raw, f)

                count += 1
            except Exception as e:
                continue  # Ignore failed downloads

        self.log_label.text = "Status: Scraping complete!"


if __name__ == "__main__":
    WebScraperApp().run()