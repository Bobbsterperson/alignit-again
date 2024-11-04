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
            'background_music': SoundLoader.load('icons/thesong.mp3'),
            'bomb': SoundLoader.load('icons/bomb.mp3')
        }
        self.sounds['gameover'].volume = 1
        self.sounds['background_music'].volume = 1
        self.sounds['bomb'].volume = 1
        if self.sounds['background_music']:
            self.sounds['background_music'].loop = True
        self.is_muted = False

    def play_sound(self, sound_name):
        if self.is_muted:
            return
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def stop_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].stop()

    def stop_all_sounds(self):
        for sound in self.sounds.values():
            if sound:
                sound.stop()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_all_sounds()
        else:
            self.play_sound('background_music')

    def play_background_music(self):
        if not self.is_muted and self.sounds['background_music']:
            self.sounds['background_music'].play()
