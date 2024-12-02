import json
import random
from constants import COLOR_BUTTONS, EASY_COLOR_BUTTONS
from kivy.clock import Clock

class GameLoader:
    def __init__(self, game):
        self.game = game

    def save_game(self):
        self.game.sound_manager.play_sound('ui')
        if self.game.is_moving or self.game.is_animation_running:
            return
        if self.game.selected_button:
            self.game.selected_button.background_color = [1, 1, 1, 1]
            self.game.selected_button = None
        mode_key = 'bomb_mode' if self.game.bomb_mode else 'normal_mode'
        save_file = 'game_save.json'
        try:
            with open(save_file, 'r') as f:
                game_state = json.load(f)
        except FileNotFoundError:
            game_state = {
                'normal_mode': {'high_scores': []},
                'bomb_mode': {'high_scores': []}
            }
        current_high_scores = game_state[mode_key].get('high_scores', [])
        if not current_high_scores or self.game.score > max(current_high_scores):
            current_high_scores.append(self.game.score)
            current_high_scores = sorted(current_high_scores, reverse=True)[:5]
            game_state[mode_key]['high_scores'] = current_high_scores
        game_state[mode_key].update({
            'grid_state': self.game.grid_state,
            'button_states': [
                {
                    'image': button.background_normal,
                    'opacity': button.background_color
                } for button in self.game.grid_buttons
            ],
            'score': self.game.score,
            'bomb_uses': self.game.bomb_uses,
            'need': self.game.need,
            'bomb_disabled': self.game.bomb_disabled,
            'muted': self.game.sound_manager.is_muted,
            'color_buttons': [btn.background_normal for btn in self.game.color_buttons]
        })
        with open(save_file, 'w') as f:
            json.dump(game_state, f, indent=4)

    def load_game(self, mode_state_file=None):
        save_file = 'game_save.json'
        try:
            with open(save_file, 'r') as f:
                game_state = json.load(f)
            mode_key = 'bomb_mode' if self.game.bomb_mode else 'normal_mode'
            mode_data = game_state.get(mode_key, {})
            self.game.grid_state = mode_data.get('grid_state', [])
            self.game.score = mode_data.get('score', 0)
            self.game.high_scores = mode_data.get('high_scores', [])
            self.game.game_logic.update_score_label()
            for button, button_state in zip(self.game.grid_buttons, mode_data.get('button_states', [])):
                button.background_normal = button_state.get('image', '')
                button.background_color = button_state.get('opacity', [1, 1, 1, 1])
            self.game.bomb_uses = mode_data.get('bomb_uses', 0)
            self.game.need = mode_data.get('need', 0)
            self.game.bomb_disabled = mode_data.get('bomb_disabled', False)
            self.game.sound_manager.is_muted = mode_data.get('muted', False)
            color_buttons_data = mode_data.get('color_buttons', [])
            if color_buttons_data:
                self.game.update_color_buttons(saved_colors=color_buttons_data)
            else:
                self.game.update_color_buttons()
            self.game.update_bomb_info_label()
            self.game.bomb.update_bomb_button_state()
            self.game.check_score_for_bomb(0)
        except FileNotFoundError:
            Clock.schedule_once(lambda dt: self.game.game_logic.assign_random_colors_to_buttons(), 0)

    def game_state_exists(self):
        save_file = 'game_save.json'
        try:
            with open(save_file, 'r') as f:
                game_state = json.load(f)
            return self.game.mode_state_file in game_state
        except FileNotFoundError:
            return False

    def reset_game(self, instance):
        self.game.color_set = EASY_COLOR_BUTTONS if self.game.bomb_mode else COLOR_BUTTONS
        self.game.sound_manager.play_sound('ui')
        if self.game.is_moving or self.game.is_animation_running:
            return
        bomb_mode = self.game.bomb_mode
        self.game.score = 0
        self.game.score_label.text = '0000'
        self.game.grid_state = [[0 for _ in range(self.game.grid_scale)] for _ in range(self.game.grid_scale)]
        if self.game.selected_button:
            self.game.selected_button.background_color = [1, 1, 1, 1]
            self.game.selected_button = None
        for button in self.game.grid_buttons:
            button.background_normal = ''
            button.background_color = [0, 0, 0, 0.5]
        self.game.color_buttons_layout.clear_widgets()
        self.game.update_color_buttons()
        self.game.next_colors = random.sample(self.game.color_set, 3)
        self.game.bomb_uses = 0
        self.game.need = 0
        self.game.bomb.update_bomb_button_state()
        self.game.game_logic.assign_random_colors_to_buttons()
        self.game.game_logic.cleanup_free_spaces()
        self.game.bomb_mode = bomb_mode

    def get_high_scores(self, mode):
        save_file = 'game_save.json'
        try:
            with open(save_file, 'r') as f:
                game_state = json.load(f)
        except FileNotFoundError:
            game_state = {'normal_mode': {}, 'bomb_mode': {}}
        mode_data = game_state.get(f'{mode}_mode', {})
        high_scores = mode_data.get('high_scores', [])
        return high_scores
  
    def save_and_exit(self, instance):
        if self.game.is_moving or self.game.is_animation_running:
            return
        else:
            self.game.sound_manager.stop_sound('background_music')
            self.save_game()
            self.game.get_running_app().stop()