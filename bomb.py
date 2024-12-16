
class Bomb:
    def __init__(self, game):
        self.game = game       

    def use_bomb(self, instance):
            if self.game.selected_button:
                if self.game.bomb_uses > 0:
                    self.game.bomb_uses -= 1
                    self.update_bomb_button_state()
                    row = self.game.selected_button.row
                    col = self.game.selected_button.col
                    affected_buttons = []
                    for i in range(max(0, row - 1), min(9, row + 2)):
                        for j in range(max(0, col - 1), min(9, col + 2)):
                            affected_buttons.append(self.game.grid_buttons[i * 9 + j])
                    self.game.sound_manager.play_sound('bomb')
                    self.game.game_logic.bomb_visual_effect(affected_buttons)
                    for button in affected_buttons:
                        button.background_normal = ''
                        button.background_color = [1, 1, 1, 0.3]
                        self.game.grid_state[button.row][button.col] = 0
                    self.game.selected_button.background_color = [1, 1, 1, 1]
                    self.game.selected_button = None
                    self.game.game_logic.cleanup_free_spaces()
                    # self.game.game_logic.space_info()
                else:
                    print("No bomb uses left!")
            else:
                print("No button selected to use the bomb.")
            
    def remove_explosion(self, explosion):
        self.root.remove_widget(explosion)

    def update_bomb_button_state(self):
        self.game.bomb_button.disabled = self.game.bomb_disabled or self.game.bomb_uses <= 0


