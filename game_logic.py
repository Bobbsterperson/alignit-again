from constants import CROWN, COLOR_BUTTONS
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.clock import Clock
import random


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

    def clear_button_colors(self, buttons):
        self.game.sound_manager.play_sound('complete_line')
        buttons_to_remove = []

        def remove_all_buttons(instance, value):
            for button in buttons_to_remove:
                self.remove_button(button)
        for button in buttons:
            buttons_to_remove.append(button)
            button.disabled = True
            self.game.is_animation_running = True
            anim = Animation(background_color=[1, 1, 0, 1], duration=0.2)
            anim += Animation(background_color=[1, 1, 1, 0.5], duration=0.3)
            anim.bind(on_complete=lambda anim, value: remove_all_buttons(anim, value))
            anim.bind(on_complete=self.animation_complete)
            anim.start(button)
        self.cleanup_free_spaces()
        self.space_info()

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

    def clear_button_colors(self, buttons):
        self.cleanup_free_spaces()
        self.game.sound_manager.play_sound('complete_line')
        buttons_to_remove = []
    
        def remove_all_buttons(instance, value):
            for button in buttons_to_remove:
                self.remove_button(button)
        for button in buttons:
            buttons_to_remove.append(button)
            button.disabled = True
            self.game.is_animation_running = True
            anim = Animation(background_color=[1, 1, 0, 1], duration=0.2)
            anim += Animation(background_color=[1, 1, 1, 0.5], duration=0.3)
            anim.bind(on_complete=lambda anim, value: remove_all_buttons(anim, value))
            anim.bind(on_complete=self.animation_complete)
            anim.start(button)

    def increase_score_by(self, count):
        self.game.score += count
        self.game.score_label.text = f'{self.game.score:04d}'
        self.game.check_score_for_bomb(count)
        self.game.update_bomb_info_label()

    def handle_line_for_button(self, button):
        line_buttons = self.check_line_of_same_color(button)
        if len(line_buttons) >= 5:
            self.increase_score_by(len(line_buttons))
            for btn in line_buttons:
                self.clear_button_color(btn)

    def clear_button_color(self, button):
        button.background_normal = ''
        button.background_color = [0, 0, 0, 0.5]
        self.game.grid_state[button.row][button.col] = 0

    def space_info(self):
        spaces = sum(row.count(0) for row in self.game.grid_state)
        print(spaces)
        for row in self.game.grid_state:
            print(row)
        print("============================")

    def get_high_scores_text(self):
        high_scores = self.game.svld.get_high_scores()
        last_five_scores = high_scores[-5:] if len(high_scores) > 5 else high_scores
        score_text = "\n".join([f"{i + 1}. {score}" for i, score in enumerate(last_five_scores)])
        return score_text
    
    def highlight_matching_buttons(self, color):
        matching_buttons = [button for button in self.game.grid_buttons if button.background_normal == color]
        if matching_buttons:
            for button in matching_buttons:
                self.highlight_new_button(button)

    def highlight_buttons(self, buttons):
        for button in buttons:
            button.background_color = [1, 0, 0, 1] 

    def assign_color_to_button(self, button, color):
        button.background_normal = color
        button.background_down = color
        button.background_color = [1, 1, 1, 1]
        self.game.grid_state[button.row][button.col] = 1
        self.highlight_new_button(button)

    def check_for_game_over(self):
        if all(all(cell != 0 for cell in row) for row in self.game.grid_state):
            self.game.svld.save_game()
            self.game.show_game_over_popup()
            self.cleanup_free_spaces()

    def highlight_new_button(self, button):
        self.game.is_animation_running = True
        anim = Animation(background_color=[3, 3, 3, 1], duration=0.3)
        anim += Animation(background_color=[1, 1, 1, 1], duration=0.2)
        anim.bind(on_complete=self.animation_complete)
        anim.start(button)

    def animation_complete(self, animation, widget):
        self.game.is_animation_running = False
        self.cleanup_free_spaces()

    def create_trail_effect(self, position):
        button = self.game.grid_buttons[position[0] * 9 + position[1]]
        size_hint_x = button.width / Window.width
        size_hint_y = button.height / Window.height
        trail_button = Button(
            background_normal=button.background_normal,
            background_color=[1, 1, 1, 0.3],
            size_hint=(size_hint_x, size_hint_y),
            pos_hint={"x": button.x / Window.width, "y": button.y / Window.height}
        )
        self.game.root.add_widget(trail_button)
        Clock.schedule_once(lambda dt: self.remove_trail(trail_button), 0.3)

    def process_movement_step(self):
        current_pos = self.game.move_path.pop(0)
        next_pos = self.game.move_path[0]
        self.game.movement.move_color(current_pos, next_pos)
        if len(self.game.move_path) > 1:
            Clock.schedule_once(lambda dt: self.process_movement_step(), 0.1)
            self.game.sound_manager.play_sound('moving_button')
        else:
            self.game.movement.finalize_move(next_pos)


    def remove_trail(self, trail_button):
        self.game.root.remove_widget(trail_button)
        self.cleanup_free_spaces()

    def check_for_free_pos(self):
        return [button for button in self.game.grid_buttons if self.game.grid_state[button.row][button.col] == 0]

    def assign_random_colors_to_buttons(self):
        selected_buttons = self.select_buttons_for_colors()
        if not selected_buttons:
            return
        for button, color in zip(selected_buttons, self.game.next_colors[:len(selected_buttons)]):
            self.assign_color_to_button(button, color)
            self.handle_line_for_button(button)
        self.check_for_game_over()

    def select_buttons_for_colors(self):
        available_buttons = self.check_for_free_pos()
        num_colors_to_spawn = min(len(available_buttons), len(self.game.next_colors))
        if num_colors_to_spawn == 0:
            return None
        return random.sample(available_buttons, num_colors_to_spawn)
    
    def bomb_visual_effect(self, affected_buttons):
        for button in affected_buttons:
            original_scale = button.size_hint[:]
            scale_up = Animation(size_hint=(1.2, 1.2), duration=0.1)
            scale_down = Animation(size_hint=original_scale, duration=0.1)
            color_change = Animation(background_color=(1, 0, 0, 1), duration=0.1) + Animation(background_color=(0, 0, 0, 0.5), duration=0.2)
            scale_up.start(button)
            scale_down.start(button)
            color_change.start(button)