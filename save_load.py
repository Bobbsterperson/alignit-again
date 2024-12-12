import json
import random
from constants import COLOR_BUTTONS, EASY_COLOR_BUTTONS

class GameLoader:
    def __init__(self, game):
        self.game = game

    def save_game(self):
        self.game.sound_manager.play_sound('ui')
        if self.is_busy():
            return
        self.deselect_button()
        current_mode_data = self.gather_game_data()
        self.save_to_file(current_mode_data)

    def is_busy(self):
        return self.game.is_moving or self.game.is_animation_running

    def deselect_button(self):
        if self.game.selected_button:
            self.game.selected_button.background_color = [1, 1, 1, 1]
            self.game.selected_button = None

    def gather_game_data(self):
        color_buttons_data = [btn.background_normal for btn in self.game.color_buttons]
        return {
            'grid_state': self.game.grid_state,
            'button_states': [
                {
                    'image': button.background_normal,
                    'opacity': button.background_color
                } for button in self.game.grid_buttons
            ],
            'score': self.game.score,
            'high_scores': self.get_high_scores(),
            'bomb_uses': self.game.bomb_uses,
            'need': self.game.need,
            'bomb_disabled': self.game.bomb_disabled,
            'muted': self.game.sound_manager.is_muted,
            'color_buttons': color_buttons_data,
            'bomb_mode': self.game.bomb_mode
        }

    def load_existing_save_data(self):
        unified_file = 'game_save.json'
        try:
            with open(unified_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'bomber': {}, 'normal': {}}

    def save_to_file(self, current_mode_data):
        unified_file = 'game_save.json'
        unified_data = self.load_existing_save_data()
        mode_key = 'bomber' if self.game.bomb_mode else 'normal'
        unified_data[mode_key] = current_mode_data
        with open(unified_file, 'w') as f:
            json.dump(unified_data, f, indent=4)


    def load_game(self):
        save_file = 'game_save.json'
        try:
            with open(save_file, 'r') as f:
                unified_data = json.load(f)
            mode_key = 'bomber' if self.game.bomb_mode else 'normal'
            game_state = unified_data.get(mode_key)
            if not game_state or 'grid_state' not in game_state:
                self.reset_game()
                return
            self.game.grid_state = game_state['grid_state']
            self.game.score = game_state['score']
            self.game.game_logic.update_score_label()
            self.game.bomb_mode = game_state['bomb_mode']
            self.game.high_scores = game_state.get('high_scores', [])
            for button, button_state in zip(self.game.grid_buttons, game_state['button_states']):
                button.background_normal = button_state['image']
                button.background_color = button_state['opacity']
            self.game.bomb_uses = game_state.get('bomb_uses', 0)
            self.game.need = game_state.get('need', 0)
            self.game.bomb_disabled = game_state.get('bomb_disabled', False)
            self.game.sound_manager.is_muted = game_state.get('muted', False)
            color_buttons_data = game_state.get('color_buttons', [])
            self.game.update_color_buttons(saved_colors=color_buttons_data or None)
            self.game.update_bomb_info_label()
            self.game.bomb.update_bomb_button_state()
            self.game.check_score_for_bomb(0)
        except FileNotFoundError:

            self.reset_game()

    def reset_game(self):
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

    def get_high_scores(self):
        self.game.sound_manager.play_sound('ui')
        save_file = 'game_save.json'
        mode_key = 'bomber' if self.game.bomb_mode else 'normal'
        try:
            with open(save_file, 'r') as f:
                unified_data = json.load(f)
        except FileNotFoundError:
            unified_data = {
                "bomber": {"high_scores": []},
                "normal": {"high_scores": []}
            }
        high_scores = unified_data.get(mode_key, {}).get('high_scores', [])
        if self.game.score > (high_scores[0] if high_scores else 0):
            high_scores.append(self.game.score)
            high_scores = sorted(set(high_scores), reverse=True)[:5]
            unified_data[mode_key]['high_scores'] = high_scores
            with open(save_file, 'w') as f:
                json.dump(unified_data, f)
        return high_scores
    
    def save_and_exit(self, instance):
        if self.game.is_moving or self.game.is_animation_running:
            return
        else:
            self.game.sound_manager.stop_sound('background_music')
            self.save_game()
            self.game.get_running_app().stop()