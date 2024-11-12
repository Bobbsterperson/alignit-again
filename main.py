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
        self.bomb_disabled = True
        self.svld = GameLoader(self)
        self.color_buttons = []
        self.bomb_mode = False
        self.color_set = COLOR_BUTTONS

    def create_top_layout(self):   
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        reset_button = Button(background_normal="icons/restart.png", size_hint=(None, None), size=(50, 50))
        save_exit_button = Button(background_normal='icons/savexit.png', size_hint=(None, None), size=(50, 50))      
        self.score_label = Label(text='0000', font_size="10sp")
        score_button = Button(background_normal='icons/score.png', size_hint=(None, None), size=(50, 50))
        reset_button.bind(on_press=self.svld.reset_game)
        save_exit_button.bind(on_press=self.svld.save_and_exit)
        score_button.bind(on_press=self.show_high_scores_popup)
        top_layout.add_widget(reset_button)
        top_layout.add_widget(save_exit_button)
        top_layout.add_widget(self.score_label)
        top_layout.add_widget(score_button)
        top_layout.bind(size=self.update_top_button_sizes)
        top_layout.bind(size=self.update_score_font_size)
        return top_layout

    def update_score_font_size(self, instance, size):
        self.score_label.font_size = size[0] / 7       
        
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

    def update_color_buttons(self, saved_colors=None):
        self.color_set = EASY_COLOR_BUTTONS if self.bomb_mode else COLOR_BUTTONS
        self.color_buttons_layout.clear_widgets()
        self.color_buttons = []
        if saved_colors:
            self.current_colors = saved_colors
        else:
            self.current_colors = random.sample(self.color_set, 3)
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
            size_hint=(0.4, None), 
        )
        self.color_buttons_layout.add_widget(buttons_layout)
        self.color_buttons_layout.add_widget(self.bomb_info_label)
        self.color_buttons_layout.bind(size=self.update_button_sizes)
        self.update_button_sizes(self.color_buttons_layout, self.color_buttons_layout.size)
        self.bomb.update_bomb_button_state()
        buttons_layout.bind(size=self.update_bomb_font_size)
    
    def update_bomb_font_size(self, instance, size):
        self.bomb_info_label.font_size = size[0] / 7

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
        self.bomb.update_bomb_button_state()
        self.game_logic.cleanup_free_spaces()
        self.sound_manager.play_sound('click_button')
        self.game_logic.check_for_game_over()  # only way for now to avoid game over when a line could be completed without triggering check_for_game_over if all grid is full
        if self.is_moving or self.is_animation_running:
            return
        if self.selected_button and self.selected_button.background_normal in self.color_set:
            self.handle_selected_button(button)
        elif button.background_normal in self.color_set:
            self.select_button(button)
            self.game_logic.jiggle_button(button)
        else:
            self.deselect_button()

    def handle_selected_button(self, button):
        if self.is_valid_move(button):
            self.move_button(button)
        else:
            self.cancel_selection()

    def is_valid_move(self, button):
        return self.grid_state[button.row][button.col] == 0

    def move_button(self, button):
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
            self.game_logic.cleanup_free_spaces()

    def cancel_selection(self):
        self.selected_button.background_color = [1, 1, 1, 1]
        self.selected_button = None
        self.game_logic.cleanup_free_spaces()

    def select_button(self, button):
        if self.selected_button:
            self.selected_button.background_color = [1, 1, 1, 1]
        self.selected_button = button
        self.selected_button.background_color = [1.5, 1.5, 1.5, 1]
        self.game_logic.cleanup_free_spaces()

    def deselect_button(self):
        if self.selected_button:
            self.selected_button.background_color = [1, 1, 1, 1]
        self.selected_button = None
        self.game_logic.cleanup_free_spaces()

    def show_game_over_popup(self):
        self.sound_manager.play_sound('gameover')
        content = BoxLayout(orientation='vertical')
        game_over_label = Label(text=f"Score: {self.score}", font_size=f"{self.score_label.width / 3}", color=(1, 1, 1, 1))
        restart_button = Button(text="Restart", size_hint=(1, 0.4), background_color=(0, 0.5, 1, 1), font_size=f"{self.score_label.width / 5}")
        content.add_widget(game_over_label)
        content.add_widget(restart_button)
        popup = Popup(title="Game Over", content=content, size_hint=(1.1, 1.1), background='icons/background.png')
        restart_button.bind(on_press=lambda *args: (self.svld.reset_game(None), popup.dismiss()))
        popup.open()

    def update_bomb_info_label(self):
        self.bomb_info_label.text = f'{SCORE_NEEDED_FOR_BOMB - self.need}' if not self.bomb_disabled else ""
        self.bomb.update_bomb_button_state()

    def show_high_scores_popup(self, instance):
        score_text = self.game_logic.get_high_scores_text()
        content_layout = self.create_popup_layout(score_text)
        popup = Popup(title='High Scores', content=content_layout, size_hint=(1, 1), background_color=(0, 0, 0, 0))
        popup.bind(on_touch_down=lambda *args: popup.dismiss())
        popup.open()

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
        bomb_mode_button = self.create_bomber_mode_button()
        content_layout.add_widget(mute_button)
        content_layout.add_widget(bomb_mode_button)    
        return content_layout

    def create_five_best_score(self, score_text):
        return Label(text=score_text, font_size=self.score_label.width / 3)

    def create_mute_button(self):   
        mute_button = Button(size_hint=(1, 0.15), background_color=(1, 1.5, 2, 1), font_size=f"{self.score_label.width / 5}")
        mute_button.text = "Unmute" if self.sound_manager.is_muted else "Mute"
        mute_button.bind(on_press=self.toggle_mute)
        return mute_button

    def toggle_mute(self, instance):
        self.sound_manager.toggle_mute()
        instance.text = "Unmute" if self.sound_manager.is_muted else "Mute"
        if not self.sound_manager.is_muted:
            self.sound_manager.play_background_music()

    def create_bomber_mode_button(self):
        bomb_mode_button = Button(
            text="Classic Mode" if self.bomb_mode else "Bomber Mode",
            size_hint=(1, 0.15),
            background_color=(1, 1.5, 2, 1),
            font_size=f"{self.score_label.width / 5}"
        )
        bomb_mode_button.bind(on_press=lambda instance: self.toggle_bomber_mode(instance))
        return bomb_mode_button

    def toggle_mode_save(funk):
        def wrapper(self, instance):
            self.svld.save_game()
            funk(self, instance)
            self.svld.reset_game(instance)
        return wrapper

    @toggle_mode_save
    def toggle_bomber_mode(self, instance):
        self.bomb_mode = not self.bomb_mode
        instance.text = "Classic Mode" if self.bomb_mode else "Bomber Mode"
        self.color_set = EASY_COLOR_BUTTONS if self.bomb_mode else COLOR_BUTTONS
        if self.bomb_mode:
            self.bomb_disabled = False
        else:
            self.bomb_disabled = True      
        self.update_bomb_button_text()
        self.update_color_buttons()
        
    def update_bomb_button_text(self):
        self.bomb_button.text = "Bomb Off" if not self.bomb_disabled else "Bomb On"
        self.bomb.update_bomb_button_state()

    def build(self):
        Window.size = (600, 1000)
        parent = RelativeLayout()
        self.background = Image(source=BACKGR, fit_mode='cover')
        parent.add_widget(self.background)     
        main_layout = BoxLayout(orientation='vertical')    
        top_layout = self.create_top_layout()
        main_layout.add_widget(top_layout)
        main_layout.add_widget(self.create_the_layouts())
        parent.add_widget(main_layout)     
        self.svld.load_game()
        self.next_colors = random.sample(self.color_set, 3)
        self.sound_manager.play_sound('background_music')
        self.game_logic.space_info()
        self.game_logic.cleanup_free_spaces() 
        return parent
    
if __name__ == '__main__':
    MyGameApp().run()
