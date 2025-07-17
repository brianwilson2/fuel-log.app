from sqlite3 import connect
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner


class FuelTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        font_size = 32

        self.add_widget(Label(text="Vehicle:", font_size=font_size))
        self.vehicle_spinner = Spinner(
            text="Transit",
            values=["Transit", "Tiguan"],
            size_hint=(1, None),
            height=60,
            font_size=font_size,
        )
        self.add_widget(self.vehicle_spinner)

        self.add_widget(Label(text="Mileage (miles):", font_size=font_size))
        self.mileage_input = TextInput(input_filter='int', multiline=False, font_size=font_size, size_hint=(1, None), height=60)
        self.add_widget(self.mileage_input)

        self.add_widget(Label(text="Litres filled:", font_size=font_size))
        self.litres_input = TextInput(input_filter='float', multiline=False, font_size=font_size, size_hint=(1, None), height=60)
        self.add_widget(self.litres_input)

        self.add_widget(Label(text="Price paid (£):", font_size=font_size))
        self.price_input = TextInput(input_filter='float', multiline=False, font_size=font_size, size_hint=(1, None), height=60)
        self.add_widget(self.price_input)

        self.add_widget(Label(text="Date (dd/mm/yyyy):", font_size=font_size))
        self.date_input = TextInput(text=datetime.today().strftime('%d/%m/%Y'), multiline=False, font_size=font_size, size_hint=(1, None), height=60)
        self.add_widget(self.date_input)

        buttons_layout = BoxLayout(size_hint=(1, None), height=80, spacing=20, padding=(0, 10))
        self.submit_button = Button(text="Submit", font_size=font_size)
        self.submit_button.bind(on_press=self.calculate_and_store)
        buttons_layout.add_widget(self.submit_button)

        self.close_button = Button(text="Close App", font_size=font_size)
        self.close_button.bind(on_press=self.close_app)
        buttons_layout.add_widget(self.close_button)

        self.add_widget(buttons_layout)

        self.result_label = Label(text="", font_size=font_size, size_hint=(1, None), height=60)
        self.add_widget(self.result_label)

    def calculate_and_store(self, instance):
        try:
            mileage = int(self.mileage_input.text)
            litres = float(self.litres_input.text)
            price = float(self.price_input.text)
            date_str = self.date_input.text
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            date_db = date_obj.strftime('%Y-%m-%d')

            mpg = mileage / (litres * 0.219969)
            l_per_100km = (litres / (mileage * 1.60934)) * 100

            self.result_label.text = f"MPG: {mpg:.2f} | L/100km: {l_per_100km:.2f}"

            conn = connect("fuel_data.db")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle TEXT,
                    date TEXT,
                    mileage INTEGER,
                    litres REAL,
                    price REAL,
                    mpg REAL,
                    l_per_100km REAL
                )
            ''')
            cursor.execute('''
                INSERT INTO fuel_log (vehicle, date, mileage, litres, price, mpg, l_per_100km)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.vehicle_spinner.text, date_db, mileage, litres, price, mpg, l_per_100km))
            conn.commit()
            conn.close()
        except Exception as e:
            self.result_label.text = f"Error: {str(e)}"

    def close_app(self, instance):
        App.get_running_app().stop()


class FuelApp(App):
    def build(self):
        return FuelTracker()


if __name__ == '__main__':
    FuelApp().run()
