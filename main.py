from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button

class MyGameApp(App):
    def build(self):
        # Window.size = (Window.width, Window.height)
        Window.size = (600, 900)
        main_layout = BoxLayout(orientation='vertical')
        spacer = BoxLayout(size_hint_y=None, height=Window.height * 0.5)
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(1, 0.6))
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        for i in range(81):
            button = Button(text=f'{i + 1}', size_hint=(1/9, 1/9))
            grid_layout.add_widget(button)
        main_layout.add_widget(spacer)
        main_layout.add_widget(grid_layout)

        return main_layout

if __name__ == '__main__':
    MyGameApp().run()
