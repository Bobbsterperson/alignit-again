from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
import random
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from astar import astar
from sound import SoundManager
from game_logic import GameLogic
from constants import *
from movement import Movement
from save_load import GameLoader
from bomb import Bomb
from kivy.core.window import Window
from kivy.uix.button import Button

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
        reset_button = Button(background_normal="icons/restart.png", size_hint=(None, None), size=(50, 50))
        save_exit_button = Button(background_normal='icons/savexit.png', size_hint=(None, None), size=(50, 50))      
        self.score_label = Label(text='0000', font_size=self.calculate_dynamic_font_size())
        Window.bind(on_resize=self.on_window_resize)
        score_button = Button(background_normal='icons/score.png', size_hint=(None, None), size=(50, 50))
        reset_button.bind(on_press=self.svld.reset_game)
        save_exit_button.bind(on_press=self.svld.save_and_exit)
        score_button.bind(on_press=self.game_logic.show_high_scores_popup)
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(score_button)
        top_layout.bind(size=self.update_top_button_sizes)
        return top_layout

    def calculate_dynamic_font_size(self, base_font_ratio=0.1):
        screen_width_inches = Window.width / Window.dpi
        screen_height_inches = Window.height / Window.dpi
        min_dimension_inches = min(screen_width_inches, screen_height_inches)
        return f"{int(min_dimension_inches * Window.dpi * base_font_ratio)}sp"

    def on_window_resize(self, *args):
        self.score_label.font_size = self.calculate_dynamic_font_size(base_font_ratio=0.1)
        self.bomb_info_label.font_size = self.calculate_dynamic_font_size()
        self.update_grid_size()

    def update_grid_size(self):
        square_size = min(Window.width, Window.height) * 0.5
        self.root.children[0].children[0].children[1].size = (square_size, square_size)

    def update_top_button_sizes(self, instance, size):
        button_count = len(instance.children) + 1
        button_width = size[0] / button_count
        for button in instance.children:
            if isinstance(button, Button):
                button.size_hint = (None, None)
                button.size = (button_width, button_width)
        self.score_label.size_hint = (1 , None)
        self.score_label.height = button_width
    
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

    def update_color_buttons(self):
        self.color_buttons_layout.clear_widgets()
        self.color_buttons = []
        self.current_colors = random.sample(COLOR_BUTTONS, 3)
        buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=10)
        for color in self.current_colors:
            color_button = Button(background_normal=color, size_hint=(None, None))
            color_button.bind(on_press=lambda btn, color=color: self.game_logic.highlight_matching_buttons(color))
            buttons_layout.add_widget(color_button)  
            self.color_buttons.append(color_button)
        self.bomb_button = Button(background_normal='icons/bomb.jpg', size_hint=(None, None))
        self.bomb_button.bind(on_press=self.bomb.use_bomb)
        buttons_layout.add_widget(self.bomb_button)
        self.bomb_info_label = Label(
            text=f'{SCORE_NEEDED_FOR_BOMB - self.need}', 
            font_size=self.calculate_dynamic_font_size(),
            size_hint=(None, None), 
            halign='right', 
            valign='middle',
            padding=(10, 0)
        )
        self.color_buttons_layout.add_widget(buttons_layout)
        self.color_buttons_layout.add_widget(self.bomb_info_label)
        self.color_buttons_layout.bind(size=self.update_button_sizes)
        self.update_button_sizes(self.color_buttons_layout, self.color_buttons_layout.size)
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

    def show_game_over_popup(self):
        self.sound_manager.play_sound('gameover')
        high_scores = self.game_logic.get_high_scores()
        best_score = high_scores[0] if high_scores else 0
        content = BoxLayout(orientation='vertical')
        game_over_label = Label(text=f"Score: {self.score}", font_size=FONT_SIZE_GAME_OVER)
        restart_button = Button(text="Restart", size_hint=(1, 0.4))
        content.add_widget(game_over_label)
        content.add_widget(restart_button)
        popup = Popup(title="Game Over", content=content, size_hint=(1.1, 1.1))
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

    def create_popup_layout(self, score_text):
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        five_best_label = self.create_five_best_score(score_text)
        content_layout.add_widget(five_best_label)
        mute_button = self.create_mute_button()
        bomb_button = self.create_bomb_button()
        content_layout.add_widget(mute_button)
        content_layout.add_widget(bomb_button)     
        return content_layout

    def create_five_best_score(self, score_text):
        return Label(text=score_text, font_size=self.calculate_dynamic_font_size())

    def create_mute_button(self):   
        mute_button = Button(size_hint=(1, 0.2))
        mute_button.text = "Unmute" if self.sound_manager.is_muted else "Mute"
        mute_button.bind(on_press=self.toggle_mute)
        return mute_button

    def toggle_mute(self, instance):
        self.sound_manager.toggle_mute()
        instance.text = "Unmute" if self.sound_manager.is_muted else "Mute"
        if not self.sound_manager.is_muted:
            self.sound_manager.play_background_music()

    def create_bomb_button(self):
        bomb_button = Button(
            text="Bomb On" if self.bomb_disabled else "Bomb Off",
            size_hint=(1, 0.2)
        )
        bomb_button.bind(on_press=self.toggle_bomb)
        return bomb_button

    def toggle_bomb(self, instance):
        self.bomb_disabled = not self.bomb_disabled
        instance.text = "Bomb On" if self.bomb_disabled else "Bomb Off"
        self.bomb.update_bomb_button_state()
        self.update_bomb_info_label()

    def build(self):
        # aspect_ratio = 16 / 9
        # width = Window.width
        # Window.size = (width, int(width * aspect_ratio))
        # Window.size = (600, 1000)
        # Window.size = (540, 1200)
        Window.fullscreen = 'auto'
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
        self.game_logic.space_info()
        return parent
    
if __name__ == '__main__':
    MyGameApp().run()
