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
from astar import astar

CROWN = 'icons/crown.png'
COLOR_BUTTONS = ['icons/blue.png', 
                 'icons/green.png', 
                #  'icons/orange.png', 
                #  'icons/pink.png', 
                #  'icons/purple.png', 
                #  'icons/turquoise.png', 
                #  'icons/yellow.png', 
                 CROWN]
BACKGR = 'icons/background.png'

class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.selected_button = None
        self.grid_buttons = []
        self.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        self.is_moving = False
        self.current_colors = []
        self.next_colors = []

    def create_top_layout(self):
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.09, padding=[10, 10, 10, 30], spacing=20)
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
        self.color_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10, padding=[10, 150, 230, 10])
        self.update_color_buttons()
        return self.color_buttons_layout

    def update_color_buttons(self):
        self.color_buttons_layout.clear_widgets()
        self.current_colors = random.sample(COLOR_BUTTONS, 3)
        for color in self.current_colors:
            color_button = Button(background_normal=color, size_hint=(0.1, 1))
            self.color_buttons_layout.add_widget(color_button)

    def create_grid_layout(self):
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(1, 0.5), spacing=4)
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
        if self.is_moving:
            return
        if self.selected_button and self.selected_button.background_normal in COLOR_BUTTONS:
            if self.grid_state[button.row][button.col] == 0:
                start = (self.selected_button.row, self.selected_button.col)
                end = (button.row, button.col)
                path = astar(self.grid_state, start, end)
                if path:
                    self.move_path = path
                    self.move_color_button_step_by_step()
                    self.selected_button = None
                else:
                    print("No free path available")
            else:
                self.selected_button.background_color = [1, 1, 1, 1]
                self.selected_button = None
        if button.background_normal in COLOR_BUTTONS:
            if self.selected_button:
                self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = button
            self.selected_button.background_color = [1.5, 1.5, 1.5, 1]
        else:
            if self.selected_button:
                self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = None

    def move_color_button_step_by_step(self):
        if not self.is_moving:
            self.is_moving = True
        current_pos = self.move_path.pop(0)
        next_pos = self.move_path[0]
        colored_button = self.grid_buttons[current_pos[0] * 9 + current_pos[1]]
        normal_button = self.grid_buttons[next_pos[0] * 9 + next_pos[1]]
        self.move_color_to_normal_button(colored_button, normal_button)
        if len(self.move_path) > 1:
            Clock.schedule_once(lambda dt: self.move_color_button_step_by_step(), 0.1)
        else:
            self.is_moving = False
            self.next_colors = self.current_colors
            self.update_color_buttons()
            self.assign_random_colors_to_buttons()
            self.space_info()

    def move_color_to_normal_button(self, colored_button, normal_button):
        normal_button.background_normal = colored_button.background_normal
        normal_button.background_down = colored_button.background_down
        normal_button.background_color = [1, 1, 1, 1]
        self.grid_state[normal_button.row][normal_button.col] = 1
        self.grid_state[colored_button.row][colored_button.col] = 0
        colored_button.background_normal = ''
        colored_button.background_down = ''
        colored_button.background_color = [0, 0, 0, 0.5]
        line_buttons = self.check_line_of_same_color(normal_button)
        if len(line_buttons) >= 5:
            self.increase_score_by(len(line_buttons))
            for btn in line_buttons:
                btn.background_normal = ''
                btn.background_color = [0, 0, 0, 0.5]
                self.grid_state[btn.row][btn.col] = 0

    def check_line_of_same_color(self, button):
        initial_color = button.background_normal
        if initial_color not in COLOR_BUTTONS and initial_color != CROWN:
            return []
        directions = {
            "horizontal": [(0, -1), (0, 1)],
            "vertical": [(-1, 0), (1, 0)],
            "diagonal1": [(-1, -1), (1, 1)],
            "diagonal2": [(-1, 1), (1, -1)]
        }
        all_line_positions = set()
        for direction, vectors in directions.items():
            for color_to_check in COLOR_BUTTONS:
                line = [button]
                current_color = initial_color if initial_color != CROWN else color_to_check

                for dx, dy in vectors:
                    row, col = button.row, button.col
                    while True:
                        row += dx
                        col += dy
                        if 0 <= row < 9 and 0 <= col < 9:
                            adjacent_button = self.grid_buttons[row * 9 + col]
                            adjacent_color = adjacent_button.background_normal

                            if adjacent_color == current_color or adjacent_color == CROWN:
                                line.append(adjacent_button)
                            elif current_color == CROWN and adjacent_color in COLOR_BUTTONS:
                                line.append(adjacent_button)
                                current_color = adjacent_color
                            else:
                                break
                        else:
                            break
                if len(line) >= 5:
                    all_line_positions.update(line)
        if len(all_line_positions) > 0:
            for button in all_line_positions:
                button.background_normal = ''
        return list(all_line_positions)

    def space_info(self):
        spaces = sum(row.count(0) for row in self.grid_state)
        print(spaces)
        for row in self.grid_state:
            print(row)
        print("============================")

    def check_for_free_pos(self):
        return [button for button in self.grid_buttons if self.grid_state[button.row][button.col] == 0]

    def assign_random_colors_to_buttons(self):
        available_buttons = self.check_for_free_pos()
        if len(available_buttons) >= len(self.next_colors):
            selected_buttons = random.sample(available_buttons, len(self.next_colors))
            for button, color in zip(selected_buttons, self.next_colors):
                button.background_normal = color
                button.background_down = color
                button.background_color = [1, 1, 1, 1]
                self.grid_state[button.row][button.col] = 1
                line_buttons = self.check_line_of_same_color(button)
                if len(line_buttons) >= 5:
                    self.increase_score_by(len(line_buttons))
                    for btn in line_buttons:
                        btn.background_normal = ''
                        btn.background_color = [0, 0, 0, 0.5]
                        self.grid_state[btn.row][btn.col] = 0

    def increase_score_by(self, count):
        self.score += count
        self.score_label.text = f'{self.score:04d}'

    def increase_score(self, instance):
        self.score += 1
        self.score_label.text = f'{self.score:04d}'

    def update_font_size(self, label):
        window_height = Window.size[1]
        label.font_size = window_height * 0.09

    def on_size(self, *args):
        self.update_font_size(self.score_label)

    def reset_game(self, instance):
        self.score = 0
        self.score_label.text = '0000'
        self.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        for button in self.grid_buttons:
            button.background_normal = ''
            button.background_color = [0, 0, 0, 0.5]
        self.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.update_color_buttons()
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
        main_layout.add_widget(top_layout)
        main_layout.add_widget(self.create_the_layouts())
        parent.add_widget(main_layout)
        self.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.assign_random_colors_to_buttons()
        self.space_info()
        return parent

if __name__ == '__main__':
    MyGameApp().run()
