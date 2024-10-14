from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button

class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0

    def build(self):
        Window.size = (600, 900)
        main_layout = BoxLayout(orientation='vertical')
        top_layout = self.create_top_layout()
        color_grid_layout = self.create_color_grid_layout() 
        main_layout.add_widget(top_layout)
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))
        main_layout.add_widget(color_grid_layout)
        return main_layout

    def create_top_layout(self):
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=[10, 10, 10, 10])
        reset_button = Button(text='Reset', size_hint=(0.15, 1))
        save_exit_button = Button(text='Save/Exit', size_hint=(0.15, 1))
        self.score_label = Label(text='0000', size_hint=(0.15, 1))
        score_button = Button(text='Score', size_hint=(0.15, 1))
        score_button.bind(on_press=self.increase_score)     
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(score_button) 
        return top_layout

    def create_color_grid_layout(self):
        color_buttons_layout = self.create_color_buttons_layout()
        grid_layout = self.create_grid_layout()
        color_grid_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        color_grid_layout.add_widget(color_buttons_layout)
        color_grid_layout.add_widget(grid_layout)
        return color_grid_layout

    def create_color_buttons_layout(self):
        color_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10, padding=[10, 10, 250, 10])
        colors = ['red', 'green', 'blue']     
        for color in colors:
            color_button = Button(text='', background_color=self.get_color(color), size_hint=(5, 1))
            color_button.bind(on_press=lambda instance, c=color: self.on_color_button_press(c))
            color_buttons_layout.add_widget(color_button)
        return color_buttons_layout

    def create_grid_layout(self):
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(1, 0.6))   
        for i in range(81):
            button = Button(text=f'{i + 1}', size_hint=(1, 1))
            grid_layout.add_widget(button)
        return grid_layout

    def get_color(self, color_name):
        if color_name == 'red':
            return (1, 0, 0, 1)
        elif color_name == 'green':
            return (0, 1, 0, 1)
        elif color_name == 'blue':
            return (0, 0, 1, 1)
        return (1, 1, 1, 1)

    def increase_score(self, instance):
        self.score += 1
        self.score_label.text = f'{self.score:04d}'

    def on_color_button_press(self, color):
        print(f'{color.capitalize()} button pressed!')

if __name__ == '__main__':
    MyGameApp().run()
