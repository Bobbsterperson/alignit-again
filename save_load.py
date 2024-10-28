import json
from kivy.app import App
from sound import SoundManager
from game_logic import GameLogic
import random
from constants import *

class GameLoader:
    def __init__(self, game):
        self.game = game
        self.sound_manager = SoundManager()
        self.game_logic = GameLogic(self.game)

    def save_game(self):
        self.game.sound_manager.play_sound('ui')
        if self.game.is_moving or self.game.is_animation_running:
            return
        if self.game.selected_button:
            self.game.selected_button.background_color = [1, 1, 1, 1]
            self.game.selected_button = None
        game_state = {
            'grid_state': self.game.grid_state,
            'button_states': [
                {
                    'image': button.background_normal,
                    'opacity': button.background_color
                } for button in self.game.grid_buttons
            ],
            'score': self.game.score,
            'high_scores': self.game_logic.get_high_scores(),
            'bomb_uses': self.game.bomb_uses,
            'need': self.game.need,
            'bomb_disabled': self.game.bomb_disabled
        }
        with open('game_save.json', 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        try:
            with open('game_save.json', 'r') as f:
                game_state = json.load(f)
                self.game.grid_state = game_state['grid_state']
                self.game.score = game_state['score']
                self.game_logic.update_score_label()
                for button, button_state in zip(self.game.grid_buttons, game_state['button_states']):
                    button.background_normal = button_state['image']
                    button.background_color = button_state['opacity']
                self.game.bomb_uses = game_state.get('bomb_uses', 0)
                self.game.need = game_state.get('need', 0)
                self.game.bomb_disabled = game_state.get('bomb_disabled', False)
                self.game.update_bomb_info_label()
                self.game.update_bomb_button_state()
                self.game.check_score_for_bomb(0)
                self.game.space_info()
        except FileNotFoundError:
            self.game.assign_random_colors_to_buttons()
            print("No saved game")

    def save_and_exit(self, instance):
        if self.game.is_moving or self.game.is_animation_running:
            return
        else:
            self.sound_manager.stop_sound('background_music')
            self.save_game()
            App.get_running_app().stop()

    def reset_game(self, instance):
        self.sound_manager.play_sound('ui')
        if self.game.is_moving or self.game.is_animation_running:
            return
        self.game.score = 0
        self.game.score_label.text = '0000'
        self.game.grid_state = [[0 for _ in range(9)] for _ in range(9)]
        if self.game.selected_button:
            self.selected_button.background_color = [1, 1, 1, 1]
            self.selected_button = None
        for button in self.game.grid_buttons:
            button.background_normal = ''
            button.background_color = [0, 0, 0, 0.5]
        self.game.color_buttons_layout.clear_widgets()
        self.game.update_color_buttons()
        self.game.next_colors = random.sample(COLOR_BUTTONS, 3)
        self.game.bomb_uses = 0
        self.game.need = 0
        self.game.update_bomb_button_state()
        self.game.assign_random_colors_to_buttons()
        self.game_logic.cleanup_free_spaces()
        self.game.space_info()