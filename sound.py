from kivy.core.audio import SoundLoader

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.sounds = {}
        self.sound_files = {
            'no_path': 'icons/no_path.wav',
            'click_button': 'icons/click.wav',
            'moving_button': 'icons/move.wav',
            'ui': 'icons/ui_butt.wav',
            'complete_line': 'icons/complete_line.wav',
            'gameover': 'icons/flatline.wav',
            'background_music': 'icons/thesong.mp3',
            'bomb': 'icons/bomb.mp3'
        }
        self.music_is_muted = False
        self.ui_sounds_are_muted = False
        self._initialized = True
        self.load_background_music()

    def load_sound(self, sound_name):
        if sound_name in self.sound_files and sound_name not in self.sounds:
            self.sounds[sound_name] = SoundLoader.load(self.sound_files[sound_name])
        return self.sounds.get(sound_name)

    def load_background_music(self):
        self.load_sound('background_music')
        if self.sounds.get('background_music'):
            self.sounds['background_music'].loop = True

    def play_sound(self, sound_name):
        if self.ui_sounds_are_muted and sound_name != 'background_music':
            return
        sound = self.sounds.get(sound_name) or self.load_sound(sound_name)
        if sound:
            sound.play()

    def stop_sound(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.stop()

    def toggle_mute_background_music(self):
        self.music_is_muted = not self.music_is_muted
        if self.music_is_muted:
            self.stop_sound('background_music')
        else:
            self.play_background_music()

    def toggle_mute_ui_sounds(self):
        self.ui_sounds_are_muted = not self.ui_sounds_are_muted

    def play_background_music(self):
        if not self.music_is_muted and self.sounds.get('background_music'):
            self.sounds['background_music'].play()

