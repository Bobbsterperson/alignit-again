from constants import *
from kivy.core.window import Window

class GameLogic:
    def __init__(self, game):
        self.game = game

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
