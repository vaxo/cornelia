class Settings:
    def __init__(self):
        self.sound_enabled = True
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.fullscreen = False
        self.show_fps = False
        self.day_mode = False  # False = night city, True = daytime with sun

    def to_dict(self):
        return {
            "sound_enabled": self.sound_enabled,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "fullscreen": self.fullscreen,
            "show_fps": self.show_fps,
            "day_mode": self.day_mode,
        }

    def from_dict(self, d):
        self.sound_enabled = d.get("sound_enabled", True)
        self.music_volume = d.get("music_volume", 0.7)
        self.sfx_volume = d.get("sfx_volume", 0.8)
        self.fullscreen = d.get("fullscreen", False)
        self.show_fps = d.get("show_fps", False)
        self.day_mode = d.get("day_mode", False)
