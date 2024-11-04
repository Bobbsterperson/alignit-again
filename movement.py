from kivy.clock import Clock

class Movement:
    def __init__(self, game):
        self.game = game

    def move_color_button_step_by_step(self):
        self.game.sound_manager.play_sound('moving_button')
        if not self.game.is_moving:
            self.start_move()
        self.process_movement_step()

    def start_move(self):
        self.game.is_moving = True
        self.game.is_animation_running = True

    def process_movement_step(self):
        current_pos = self.game.move_path.pop(0)
        next_pos = self.game.move_path[0]
        self.move_color(current_pos, next_pos)
        if len(self.game.move_path) > 1:
            Clock.schedule_once(lambda dt: self.process_movement_step(), 0.1)
            self.game.sound_manager.play_sound('moving_button')
        else:
            self.finalize_move(next_pos)

    def move_color(self, current_pos, next_pos):
        colored_button = self.game.grid_buttons[current_pos[0] * 9 + current_pos[1]]
        normal_button = self.game.grid_buttons[next_pos[0] * 9 + next_pos[1]]
        self.game.game_logic.create_trail_effect(current_pos)
        self.move_color_to_normal_button(colored_button, normal_button)

    def move_color_to_normal_button(self, colored_button, normal_button):
        normal_button.background_normal = colored_button.background_normal
        normal_button.background_down = colored_button.background_down
        normal_button.background_color = [1, 1, 1, 1]
        self.game.grid_state[normal_button.row][normal_button.col] = 1
        self.game.grid_state[colored_button.row][colored_button.col] = 0
        colored_button.background_normal = ''
        colored_button.background_down = ''
        colored_button.background_color = [0, 0, 0, 0.5]

    def finalize_move(self, final_pos):
        self.game.is_moving = False
        self.game.is_animation_running = False
        self.game.game_logic.check_line_of_same_color(self.game.grid_buttons[final_pos[0] * 9 + final_pos[1]])
        self.handle_post_move_updates()

    def handle_post_move_updates(self):
        if not self.game.lines_cleared:
            self.game.next_colors = self.game.current_colors
            self.game.update_color_buttons()
            self.game.game_logic.assign_random_colors_to_buttons()
        self.game.lines_cleared = False
        self.game.game_logic.space_info()
