from constants import *
from kivy.core.window import Window
from kivy.animation import Animation
from sound import SoundManager
import json

class GameLogic:
    def __init__(self, game):
        self.game = game
        self.sound_manager = SoundManager()

    def check_direction(self, button, vectors, initial_color, color_to_check):
        line = [button]
        current_color = initial_color if initial_color != CROWN else color_to_check
        for dx, dy in vectors:
            row, col = button.row, button.col
            while True:
                row += dx
                col += dy
                if 0 <= row < 9 and 0 <= col < 9:
                    adjacent_button = self.game.grid_buttons[row * 9 + col]
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

    def get_direction_vectors(self):
        return {
            "horizontal": [(0, -1), (0, 1)],
            "vertical": [(-1, 0), (1, 0)],
            "diagonal1": [(-1, -1), (1, 1)],
            "diagonal2": [(-1, 1), (1, -1)]
        }

    def update_font_size(self, label):
        window_height = Window.size[1]
        label.font_size = window_height * 0.09

    def clear_button_colors(self, buttons):
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
            anim.bind(on_complete=self.game.animation_complete)
            anim.start(button)
        self.cleanup_free_spaces()
        self.game.space_info()

    def remove_button(self, button):
        button.background_normal = ''
        button.background_color = [0, 0, 0, 0.5]
        self.game.grid_state[button.row][button.col] = 0
        button.disabled = False

    def cleanup_free_spaces(self):
        for row in range(9):
            for col in range(9):
                if self.game.grid_state[row][col] == 0:
                    button = self.game.grid_buttons[row * 9 + col]
                    if button.background_normal != '' or button.background_color != [0, 0, 0, 0.5]:
                        button.background_normal = ''
                        button.background_color = [0, 0, 0, 0.5]

    def update_score_label(self):
        self.game.score_label.text = f'{self.game.score:04d}'

    def get_high_scores(self):
        self.sound_manager.play_sound('ui')
        try:
            with open('high_scores.json', 'r') as f:
                high_scores = json.load(f)
        except FileNotFoundError:
            high_scores = []
        if self.game.score > (high_scores[0] if high_scores else 0):
            high_scores.append(self.game.score)
            high_scores = sorted(set(high_scores), reverse=True)[:5]
            with open('high_scores.json', 'w') as f:
                json.dump(high_scores, f)
        return high_scores
    
    def increase_score_by(self, count):
        self.game.score += count
        self.game.score_label.text = f'{self.game.score:04d}'
        self.game.check_score_for_bomb(count)
        self.game.update_bomb_info_label()