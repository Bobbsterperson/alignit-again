from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
import random
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock

COLOR_BUTTONS = ['icons/blue.png', 'icons/green.png', 'icons/orange.png', 'icons/pink.png', 'icons/purple.png', 'icons/turquoise.png', 'icons/yellow.png']
BACKGR = 'icons/background.png'

class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.selected_button = None
        self.grid_buttons = []
        self.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        self.colored_button_pos_flag = False
        self.but_pos = []

    def create_top_layout(self):
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.09, padding=[10, 10, 10, 10], spacing=20)
        reset_button = Button(background_normal='icons/restart.png', size_hint=(0.1, 1))
        reset_button.bind(on_press=self.reset_game)
        save_exit_button = Button(background_normal='icons/savexit.png', size_hint=(0.1, 1))
        save_exit_button.bind(on_press=self.save_and_exit)
        self.score_label = Label(text='0000', size_hint=(0.25, 1))
        self.update_font_size(self.score_label)
        score_button = Button(background_normal='icons/score.png', size_hint=(0.1, 1))
        score_button.bind(on_press=self.increase_score)     
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(score_button) 
        return top_layout


    def create_the_layouts(self):
        color_buttons_layout = self.create_color_buttons_layout()
        grid_layout = self.create_grid_layout()
        color_grid_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        color_grid_layout.add_widget(color_buttons_layout)
        color_grid_layout.add_widget(grid_layout)
        return color_grid_layout

    def create_color_buttons_layout(self):
        color_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10, padding=[10, 80, 230, 10])
        selected_colors = random.sample(COLOR_BUTTONS, 3)
        for color in selected_colors:
            color_button = Button(background_normal=color, size_hint=(0.05, 1))
            color_buttons_layout.add_widget(color_button)
        return color_buttons_layout

    def create_grid_layout(self):
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(1, 0.6), spacing=4)
        for row in range(9):
            for col in range(9):
                button = Button(size_hint=(1, 1))
                button.background_color = [0, 0, 0, 0.5]
                button.row = row
                button.col = col
                grid_layout.add_widget(button)
                self.grid_buttons.append(button)
                button.bind(on_press=self.on_button_click)
        return grid_layout
    


    
    def on_button_click(self, button):
        if self.selected_button and self.selected_button.background_normal in COLOR_BUTTONS:
            if self.grid_state[button.row][button.col] == 0:
                self.move_color_to_normal_button(self.selected_button, button)
                self.selected_button = None
                self.assign_random_colors_to_buttons()
                self.space_info()
                return
            else:
                self.selected_button.background_color = [1, 1, 1, 1]
        self.selected_button = button
        if self.selected_button.background_normal in COLOR_BUTTONS:
            self.selected_button.background_color = [1.5, 1.5, 1.5, 1]
            self.colored_button_pos_flag = True
        else:
            self.selected_button.background_color = [0, 0, 0, 0.5]
            self.colored_button_pos_flag = False
        print(self.colored_button_pos_flag)

        


    def move_color_to_normal_button(self, colored_button, normal_button):
        normal_button.background_normal = colored_button.background_normal
        normal_button.background_down = colored_button.background_down
        normal_button.background_color = [1, 1, 1, 1]
        self.grid_state[normal_button.row][normal_button.col] = 1
        colored_button.background_normal = ''
        colored_button.background_down = ''
        colored_button.background_color = [0, 0, 0, 0.5]
        self.grid_state[colored_button.row][colored_button.col] = 0


    def space_info(self):
        spaces = 0
        for i in self.grid_state:
            for j in i:
                if j == 0:
                    spaces += 1
        print(spaces)
        for row in self.grid_state:
            print(row)
        print("============================")
        
    def check_for_free_pos(self):
        return [
            button
            for button in self.grid_buttons
            if self.grid_state[button.row][button.col] == 0
        ]

    def assign_random_colors_to_buttons(self):
        available_buttons = self.check_for_free_pos()
        if len(available_buttons) >= 3:
            selected_buttons = random.sample(available_buttons, 3)
            selected_colors = random.sample(COLOR_BUTTONS, 3)
            for button, color in zip(selected_buttons, selected_colors):
                button.background_normal = color
                button.background_down = color
                button.background_color = [1, 1, 1, 1]
                self.grid_state[button.row][button.col] = 1

    def increase_score(self, instance):
        self.score += 1
        self.score_label.text = f'{self.score:04d}'

    def update_font_size(self, label):
        window_height = Window.size[1]
        label.font_size = window_height * 0.09

    def on_size(self, *args):
        self.update_font_size(self.score_label)

    def reset_game(self, instance):
        """TODO: fix this method"""
        self.score = 0
        self.score_label.text = '0000'
        self.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        for button in self.grid_buttons:
            button.background_normal = ''
            button.background_color = [0, 0, 0, 0.5]
        self.assign_random_colors_to_buttons()
        self.space_info()



    def save_and_exit(self, instance):
        App.get_running_app().stop()

    def build(self):
        Window.size = (600, 1050)
        parent = RelativeLayout()
        parent.add_widget(Image(source=BACKGR, fit_mode='cover'))
        main_layout = BoxLayout(orientation='vertical')    
        top_layout = self.create_top_layout()
        color_grid_layout = self.create_the_layouts() 
        main_layout.add_widget(top_layout)
        main_layout.add_widget(BoxLayout(size_hint_y=0.1))
        main_layout.add_widget(color_grid_layout)
        parent.add_widget(main_layout)
        self.assign_random_colors_to_buttons()
        return parent

if __name__ == '__main__':
    MyGameApp().run()
