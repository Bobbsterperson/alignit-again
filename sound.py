from kivy.core.audio import SoundLoader

class SoundManager:
    def __init__(self):
        self.sounds = {
            'no_path': SoundLoader.load('icons/no_path.wav'),
            'click_button': SoundLoader.load('icons/click.wav'),
            'moving_button': SoundLoader.load('icons/move.wav'),
            'ui': SoundLoader.load('icons/ui_butt.wav'),
            'complete_line': SoundLoader.load('icons/complete_line.wav'),
            'gameover': SoundLoader.load('icons/flatline.wav'),
            'background_music': SoundLoader.load('icons/thesong.mp3')
        }
        self.sounds['gameover'].volume = 0.4
        self.sounds['background_music'].volume = 0.4

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def stop_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].stop()

    def set_loop(self, sound_name, loop):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].loop = loop
