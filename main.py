from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button

class MyGameApp(App):
    def build(self):
        Window.size = (600, 900)
        main_layout = BoxLayout(orientation='vertical')
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=[10, 10, 10, 10])
        reset_button = Button(text='Reset', size_hint=(0.15, 1))
        save_exit_button = Button(text='Save/Exit', size_hint=(0.15, 1))
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(Label(size_hint=(0.6, 1)))
        score_button = Button(text='Score', size_hint=(0.15, 1))
        top_layout.add_widget(score_button)
        spacer = BoxLayout(size_hint_y=0.4)
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(1, 0.5))
        for i in range(81):
            button = Button(text=f'{i + 1}', size_hint=(1, 1))
            grid_layout.add_widget(button)
        main_layout.add_widget(top_layout)
        main_layout.add_widget(spacer)
        main_layout.add_widget(grid_layout)
        return main_layout

if __name__ == '__main__':
    MyGameApp().run()
