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
from sound import SoundManager
from game_logic import GameLogic
from constants import *
from movement import Movement
from save_load import GameLoader
from bomb import Bomb

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
        self.bomb_uses = 0
        self.need = 0
        self.bomb = Bomb(self)
        self.game_logic = GameLogic(self)
        self.movement = Movement(self)
        self.bomb_disabled = False
        self.svld = GameLoader(self)
        self.color_buttons = []

    def create_top_layout(self):
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        reset_button = Button(background_normal='icons/restart.png', size_hint=(None, None), size=(50, 50))
        save_exit_button = Button(background_normal='icons/savexit.png', size_hint=(None, None), size=(50, 50))      
        self.score_label = Label(text='0000', size_hint=(1, None), height=50)
        self.update_score_font_size()
        Window.bind(on_resize=self.on_window_resize)
        score_button = Button(background_normal='icons/score.png', size_hint=(None, None), size=(50, 50))
        reset_button.bind(on_press=self.svld.reset_game)
        save_exit_button.bind(on_press=self.svld.save_and_exit)
        score_button.bind(on_press=self.show_high_scores_popup)
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(score_button)
        top_layout.bind(size=self.update_top_button_sizes)
        return top_layout

    def update_score_font_size(self):
        self.score_label.font_size = f'{min(Window.width, Window.height) * 0.05}sp'

    def update_bomb_info_label_size(self):
        if self.bomb_info_label:
            self.bomb_info_label.font_size = f'{min(Window.width, Window.height) * 0.05}sp'
            self.bomb_info_label.size_hint = (None, None)
            self.bomb_info_label.size = (self.color_buttons_layout.width / (len(self.color_buttons) + 1), 30)

    def on_window_resize(self, *args):
        self.update_score_font_size()
        self.update_grid_size()
        self.update_bomb_info_label_size()

    def update_grid_size(self):
        square_size = min(Window.width, Window.height) * 0.5
        self.root.children[0].children[0].children[1].size = (square_size, square_size)

    def update_top_button_sizes(self, instance, size):
        button_count = len(instance.children)
        button_width = size[0] / button_count * 0.8

        for button in instance.children:
            if isinstance(button, Button):
                button.size_hint = (None, None)
                button.size = (button_width, button_width)
        self.score_label.size_hint = (1, None)
        self.score_label.height = button_width
        self.update_score_font_size()
    
    def create_the_layouts(self):
        color_buttons_layout = self.create_color_buttons_layout()
        grid_layout = self.create_grid_layout()
        color_grid_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        color_grid_layout.add_widget(color_buttons_layout)
        color_grid_layout.add_widget(grid_layout)
        return color_grid_layout
    
    def create_color_buttons_layout(self):
        self.color_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=10, padding=[10, 10, 10, 10])
        self.update_color_buttons()
        self.color_buttons_layout.bind(size=self.update_button_sizes)
        return self.color_buttons_layout
    
    def update_button_sizes(self, instance, size):
        button_count = len(self.color_buttons) + 3
        width = size[0] / button_count
        for button in self.color_buttons:
            button.size_hint = (None, None)
            button.size = (width, width)
        self.bomb_button.size = (width, width)
        self.bomb_info_label.size_hint = (None, None)
        self.bomb_info_label.size = (width, width)
    
    def highlight_matching_buttons(self, color):
        matching_buttons = [button for button in self.grid_buttons if button.background_normal == color]
        if matching_buttons:
            for button in matching_buttons:
                self.highlight_new_button(button)

    def highlight_buttons(self, buttons):
        for button in buttons:
            button.background_color = [1, 0, 0, 1] 

    def update_color_buttons(self):
        self.color_buttons_layout.clear_widgets()
        self.color_buttons = []
        self.current_colors = random.sample(COLOR_BUTTONS, 3)
        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=10)
        for color in self.current_colors:
            color_button = Button(background_normal=color, size_hint=(None, None))
            color_button.bind(on_press=lambda btn, color=color: self.highlight_matching_buttons(color))
            buttons_layout.add_widget(color_button)  
            self.color_buttons.append(color_button)
        self.bomb_button = Button(background_normal='icons/bomb.jpg', size_hint=(None, None))
        self.bomb_button.bind(on_press=self.bomb.use_bomb)
        buttons_layout.add_widget(self.bomb_button)
        self.bomb_info_label = Label(
            text=f'{SCORE_NEEDED_FOR_BOMB - self.need}', 
            font_size='100sp', 
            size_hint=(None, None), 
            height=50,
            halign='right', 
            valign='middle',
            padding=(10, 0)
        )
        self.color_buttons_layout.add_widget(buttons_layout)
        self.color_buttons_layout.add_widget(self.bomb_info_label)
        self.color_buttons_layout.bind(size=self.update_button_sizes)
        self.update_button_sizes(self.color_buttons_layout, self.color_buttons_layout.size)  # 
        self.bomb.update_bomb_button_state()

    def create_grid_layout(self):
        grid_layout = GridLayout(cols=9, rows=9, size_hint=(None, None), spacing=4)
        square_size = min(Window.width, Window.height) * 1.0
        grid_layout.size = (square_size, square_size)
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
        print(self.bomb_uses)
        self.bomb.update_bomb_button_state()
        self.game_logic.cleanup_free_spaces()
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
                    self.movement.move_color_button_step_by_step()
                    self.selected_button = None
                    self.game_logic.cleanup_free_spaces()
                else:
                    self.sound_manager.play_sound('no_path')
                    print("No free path available")
                    self.game_logic.cleanup_free_spaces()
            else:
                self.selected_button.background_color = [1, 1, 1, 1]
                self.selected_button = None
                self.game_logic.cleanup_free_spaces()
        if button.background_normal in COLOR_BUTTONS:
            if self.selected_button:
                self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = button
            self.selected_button.background_color = [1.5, 1.5, 1.5, 1]
            self.game_logic.cleanup_free_spaces()
        else:
            if self.selected_button:
                self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = None
            self.game_logic.cleanup_free_spaces()

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

    def check_line_of_same_color(self, button): 
        initial_color = button.background_normal
        if initial_color not in COLOR_BUTTONS and initial_color != CROWN:
            return []
        all_line_positions = set()
        directions = self.game_logic.get_direction_vectors()
        for direction, vectors in directions.items():
            for color_to_check in COLOR_BUTTONS:
                line = self.game_logic.check_direction(button, vectors, initial_color, color_to_check)
                if len(line) >= 5:
                    all_line_positions.update(line)
        self.game_logic.increase_score_by(len(all_line_positions))
        if all_line_positions:
            self.clear_button_colors(all_line_positions)
            self.lines_cleared = True
        self.game_logic.cleanup_free_spaces()
        return list(all_line_positions)

    def clear_button_colors(self, buttons):
        self.game_logic.cleanup_free_spaces()
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
                self.game_logic.increase_score_by(len(line_buttons))
                for btn in line_buttons:
                    btn.background_normal = ''
                    btn.background_color = [0, 0, 0, 0.5]
                    self.grid_state[btn.row][btn.col] = 0
        if all(all(cell != 0 for cell in row) for row in self.grid_state):
            self.show_game_over_popup()
            self.game_logic.cleanup_free_spaces()

    def highlight_new_button(self, button):
        self.is_animation_running = True
        anim = Animation(background_color=[3, 3, 3, 1], duration=0.3)
        anim += Animation(background_color=[1, 1, 1, 1], duration=0.2)
        anim.bind(on_complete=self.animation_complete)
        anim.start(button)

    def animation_complete(self, animation, widget):
        self.is_animation_running = False
        self.game_logic.cleanup_free_spaces()

    def show_game_over_popup(self):
        self.sound_manager.play_sound('gameover')
        high_scores = self.game_logic.get_high_scores()
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
        restart_button.bind(on_press=lambda *args: (self.svld.reset_game(None), popup.dismiss()))
        popup.open()

    def update_bomb_info_label(self):
        self.bomb_info_label.text = f'{SCORE_NEEDED_FOR_BOMB - self.need}' if not self.bomb_disabled else ""
        self.bomb.update_bomb_button_state()

    def check_score_for_bomb(self, count):
        self.need += count
        if self.need >= SCORE_NEEDED_FOR_BOMB:
            self.bomb_uses += 1
            self.need -= SCORE_NEEDED_FOR_BOMB
            self.bomb.update_bomb_button_state()

    def show_high_scores_popup(self, instance):
        high_scores = self.game_logic.get_high_scores()
        last_five_scores = high_scores[-5:] if len(high_scores) > 5 else high_scores
        score_text = "\n".join([f"{i + 1}. {score}" for i, score in enumerate(last_five_scores)])
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        score_label = Label(text=score_text, halign="center", valign="middle", font_size='40sp')
        score_label.bind(size=score_label.setter('text_size'))
        content_layout.add_widget(score_label)
        mute_button = Button(size_hint=(1, 0.2))
        bomb_button = Button(text="Bomb Off", size_hint=(1, 0.2))
        if not hasattr(self, 'sound_manager'):
            self.sound_manager = SoundManager()
        if self.sound_manager.is_muted:
            mute_button.text = "Unmute"
        else:
            mute_button.text = "Mute"

        def toggle_mute(instance):
            self.sound_manager.toggle_mute()
            if self.sound_manager.is_muted:
                mute_button.text = "Unmute"
            else:
                mute_button.text = "Mute"
                self.sound_manager.play_background_music()

        def toggle_bomb(instance):
            self.bomb_disabled = not self.bomb_disabled
            bomb_button.text = "Bomb Off" if not self.bomb_disabled else "Bomb On"
            self.bomb.update_bomb_button_state()
            self.update_bomb_info_label()
        mute_button.bind(on_press=toggle_mute)
        bomb_button.bind(on_press=toggle_bomb)
        content_layout.add_widget(mute_button)
        content_layout.add_widget(bomb_button)
        popup = Popup(title='High Scores', content=content_layout, size_hint=(0.5, 0.5))
        popup.open()

    def build(self):
        # aspect_ratio = 16 / 9
        # width = Window.width
        # Window.size = (width, int(width * aspect_ratio))
        # Window.size = (800, 1280)
        Window.size = (360, 640)
        # Window.fullscreen = 'auto'
        parent = RelativeLayout()
        parent.add_widget(Image(source=BACKGR, fit_mode='cover'))
        main_layout = BoxLayout(orientation='vertical')    
        top_layout = self.create_top_layout()
        main_layout.add_widget(top_layout)
        main_layout.add_widget(self.create_the_layouts())
        parent.add_widget(main_layout)
        self.svld.load_game()
        self.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.sound_manager.play_sound('background_music')
        self.space_info()
        return parent
    
if __name__ == '__main__':
    MyGameApp().run()
