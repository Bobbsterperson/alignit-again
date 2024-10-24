from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
import random
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from astar import astar
import json
from sound import SoundManager

CROWN = 'icons/crown.png'
COLOR_BUTTONS = ['icons/blue.png', 
                 'icons/green.png', 
                 'icons/orange.png', 
                 'icons/pink.png', 
                 'icons/purple.png', 
                 'icons/turquoise.png', 
                 'icons/yellow.png', 
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
        self.is_animation_running = False
        self.lines_cleared = False
        self.sound_manager = SoundManager()

    def create_top_layout(self):
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.09, padding=[10, 10, 10, 30], spacing=20)
        reset_button = Button(background_normal='icons/restart.png', size_hint=(0.1, 1))
        reset_button.bind(on_press=self.reset_game)
        save_exit_button = Button(background_normal='icons/savexit.png', size_hint=(0.1, 1))
        save_exit_button.bind(on_press=self.save_and_exit)
        self.score_label = Label(text='0000', size_hint=(0.25, 1))
        self.update_font_size(self.score_label)
        score_button = Button(background_normal='icons/score.png', size_hint=(0.1, 1))
        score_button.bind(on_press=self.show_high_scores_popup)
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
        self.sound_manager.play_sound('click_button')
        if self.is_moving or self.is_animation_running:
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
                    self.sound_manager.play_sound('no_path')
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
        self.sound_manager.play_sound('moving_button')
        if not self.is_moving:
            self.is_moving = True
            self.is_animation_running = True
        current_pos = self.move_path.pop(0)
        next_pos = self.move_path[0]
        colored_button = self.grid_buttons[current_pos[0] * 9 + current_pos[1]]
        normal_button = self.grid_buttons[next_pos[0] * 9 + next_pos[1]]
        self.create_trail_effect(current_pos)
        self.move_color_to_normal_button(colored_button, normal_button)
        if len(self.move_path) > 1:
            Clock.schedule_once(lambda dt: self.move_color_button_step_by_step(), 0.1)
        else:
            self.is_moving = False
            self.is_animation_running = False
            self.check_line_of_same_color(normal_button)
            if not self.lines_cleared:
                self.next_colors = self.current_colors
                self.update_color_buttons()
                self.assign_random_colors_to_buttons()
            self.lines_cleared = False
            self.space_info()

    def cleanup_free_spaces(self):
        for row in range(9):
            for col in range(9):
                if self.grid_state[row][col] == 0:
                    button = self.grid_buttons[row * 9 + col]
                    if button.background_normal != '' or button.background_color != [0, 0, 0, 0.5]:
                        button.background_normal = ''
                        button.background_color = [0, 0, 0, 0.5]

    def create_trail_effect(self, position):
        button = self.grid_buttons[position[0] * 9 + position[1]]
        trail_button = Button(
            background_normal=button.background_normal,
            background_color=[1, 1, 1, 0.3],
            size_hint=(0.11, 0.067),
            pos_hint={"x": button.x / Window.width, "y": button.y / Window.height}
        )
        self.root.add_widget(trail_button)
        Clock.schedule_once(lambda dt: self.remove_trail(trail_button), 0.3)

    def remove_trail(self, trail_button):
        self.root.remove_widget(trail_button)

    def move_color_to_normal_button(self, colored_button, normal_button):
        normal_button.background_normal = colored_button.background_normal
        normal_button.background_down = colored_button.background_down
        normal_button.background_color = [1, 1, 1, 1]
        self.grid_state[normal_button.row][normal_button.col] = 1
        self.grid_state[colored_button.row][colored_button.col] = 0
        colored_button.background_normal = ''
        colored_button.background_down = ''
        colored_button.background_color = [0, 0, 0, 0.5]

    def check_line_of_same_color(self, button):
        initial_color = button.background_normal
        if initial_color not in COLOR_BUTTONS and initial_color != CROWN:
            return []
        all_line_positions = set()
        directions = self.get_direction_vectors()
        for direction, vectors in directions.items():
            for color_to_check in COLOR_BUTTONS:
                line = self.check_direction(button, vectors, initial_color, color_to_check)
                if len(line) >= 5:
                    all_line_positions.update(line)
        if all_line_positions:
            self.clear_button_colors(all_line_positions)
            self.lines_cleared = True
        self.cleanup_free_spaces()
        return list(all_line_positions)

    def get_direction_vectors(self):
        return {
            "horizontal": [(0, -1), (0, 1)],
            "vertical": [(-1, 0), (1, 0)],
            "diagonal1": [(-1, -1), (1, 1)],
            "diagonal2": [(-1, 1), (1, -1)]
        }

    def check_direction(self, button, vectors, initial_color, color_to_check):
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
        return line

    def clear_button_colors(self, buttons):
        self.cleanup_free_spaces()
        self.sound_manager.play_sound('complete_line')
        buttons_to_remove = []

        def remove_all_buttons(instance, value):
            for button in buttons_to_remove:
                self.remove_button(button)
        for button in buttons:
            buttons_to_remove.append(button)
            button.disabled = True
            self.is_animation_running = True
            anim = Animation(background_color=[1, 1, 0, 1], duration=0.2)
            anim += Animation(background_color=[1, 1, 1, 0.5], duration=0.3)
            anim.bind(on_complete=lambda anim, value: remove_all_buttons(anim, value))
            anim.bind(on_complete=self.animation_complete)
            anim.start(button)


    def remove_button(self, button):
        button.background_normal = ''
        button.background_color = [0, 0, 0, 0.5]
        self.grid_state[button.row][button.col] = 0
        button.disabled = False

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
        num_colors_to_spawn = min(len(available_buttons), len(self.next_colors))
        if num_colors_to_spawn == 0:
            return
        selected_buttons = random.sample(available_buttons, num_colors_to_spawn)
        for button, color in zip(selected_buttons, self.next_colors[:num_colors_to_spawn]):
            button.background_normal = color
            button.background_down = color
            button.background_color = [1, 1, 1, 1]
            self.grid_state[button.row][button.col] = 1
            self.highlight_new_button(button)
            line_buttons = self.check_line_of_same_color(button)
            if len(line_buttons) >= 5:
                self.increase_score_by(len(line_buttons))
                for btn in line_buttons:
                    btn.background_normal = ''
                    btn.background_color = [0, 0, 0, 0.5]
                    self.grid_state[btn.row][btn.col] = 0
        if all(all(cell != 0 for cell in row) for row in self.grid_state):
            self.show_game_over_popup()
            self.cleanup_free_spaces()

    def highlight_new_button(self, button):
        self.is_animation_running = True
        anim = Animation(background_color=[3, 3, 3, 1], duration=0.3)
        anim += Animation(background_color=[1, 1, 1, 1], duration=0.2)
        anim.bind(on_complete=self.animation_complete)
        anim.start(button)

    def animation_complete(self, animation, widget):
        self.is_animation_running = False
        self.cleanup_free_spaces()

    def show_game_over_popup(self):
        self.sound_manager.play_sound('gameover')
        high_scores = self.get_high_scores()
        best_score = high_scores[0] if high_scores else 0
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        game_over_label = Label(text=f"Score: {self.score}", font_size='50sp')
        if self.score > best_score:
            best_score_label = Label(text="New Best Score!", font_size='24sp', color=(1, 0.8, 0, 1))
            content.add_widget(best_score_label)
        restart_button = Button(text="Restart", size_hint=(1, 0.4))
        content.add_widget(game_over_label)
        content.add_widget(restart_button)
        popup = Popup(title="Game Over", content=content, size_hint=(0.5, 0.5))
        restart_button.bind(on_press=lambda *args: (self.reset_game(None), popup.dismiss()))
        popup.open()


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
        self.sound_manager.play_sound('ui')
        if self.is_moving or self.is_animation_running:
            return
        self.score = 0
        self.score_label.text = '0000'
        self.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        if self.selected_button:
            self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = None
        for button in self.grid_buttons:
            button.background_normal = ''
            button.background_color = [0, 0, 0, 0.5]
        self.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.update_color_buttons()
        self.assign_random_colors_to_buttons()
        self.cleanup_free_spaces()
        self.space_info()

    def save_game(self):
        self.sound_manager.play_sound('ui')
        if self.is_moving or self.is_animation_running:
            return
        if self.selected_button:
            self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = None
        game_state = {
            'grid_state': self.grid_state,
            'button_states': [
                {
                    'image': button.background_normal,
                    'opacity': button.background_color
                } for button in self.grid_buttons
            ],
            'score': self.score,
            'high_scores': self.get_high_scores()
        }
        
        with open('game_save.json', 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        try:
            with open('game_save.json', 'r') as f:
                game_state = json.load(f)
                self.grid_state = game_state['grid_state']
                self.score = game_state['score']
                self.update_score_label()
                for button, button_state in zip(self.grid_buttons, game_state['button_states']):
                    button.background_normal = button_state['image']
                    button.background_color = button_state['opacity'] 
                self.space_info()
        except FileNotFoundError:
            self.assign_random_colors_to_buttons()
            print("No saved game")

    def get_high_scores(self):
        self.sound_manager.play_sound('ui')
        try:
            with open('high_scores.json', 'r') as f:
                high_scores = json.load(f)
        except FileNotFoundError:
            high_scores = []
        if self.score > (high_scores[0] if high_scores else 0):
            high_scores.append(self.score)
            high_scores = sorted(set(high_scores), reverse=True)[:5]
            with open('high_scores.json', 'w') as f:
                json.dump(high_scores, f)

        return high_scores

    def show_high_scores_popup(self, instance):
        high_scores = self.get_high_scores()
        score_text = "\n".join([f"{i+1}. {score}" for i, score in enumerate(high_scores)])
        content = Label(text=score_text, halign="center", valign="middle", font_size='60sp')
        content.bind(size=content.setter('text_size'))
        popup = Popup(title='High Scores', content=content, size_hint=(0.5, 0.5))
        popup.open()

    def update_score_label(self):
        self.score_label.text = f'{self.score:04d}'

    def save_and_exit(self, instance):
        if self.is_moving or self.is_animation_running:
            return
        else:
            self.sound_manager.stop_sound('background_music')
            self.save_game()
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
        self.load_game()
        self.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.sound_manager.play_sound('background_music')
        self.sound_manager.set_loop('background_music', True)
        self.space_info()
        return parent
if __name__ == '__main__':
    MyGameApp().run()
