import pygame
import os
from config.paths import SFX_DIR, MUSIC_DIR

# Playlist, in order. Each track crossfades into the next; the list loops.
MUSIC_FILES = [
    "Loli Mou.mp3",
    "Maco Mamuko  Whiskey, colatequila.mp3",
]


class AudioManager:
    """Handles SFX and a looping background-music PLAYLIST with crossfades.

    Tracks play in order on two reserved mixer channels. About LOOP_LEAD_S
    seconds before the current track ends we start the NEXT track on the other
    channel (fading in) while fading the current one out — so tracks blend
    smoothly with no gap, and the playlist wraps around forever. Requires
    update(dt) each frame.
    """

    MUSIC_FADE_MS = 2000     # crossfade length
    LOOP_LEAD_S = 2.0        # switch this many seconds before the end
    START_FADE_MS = 900      # gentle fade-in on first play

    def __init__(self, settings):
        self.settings = settings
        self._sfx = {}
        self._tracks = []        # list of (Sound, length_seconds)
        self._track_idx = 0
        self._cur_len = 0.0
        self._music_active = False
        self._music_start = 0
        self._chan_idx = 0

        # Reserve channels 0 & 1 for the music crossfade; SFX use the rest.
        try:
            pygame.mixer.set_reserved(2)
            self._music_channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
        except pygame.error:
            self._music_channels = []

        self._load_sounds()
        self._load_music()

    def _load_sounds(self):
        sfx_files = {
            # Collisions scream like a goat; the old crash.wav is still on disk
            "crash": "goat_scream.wav",
            "score": "score.wav",
            "click": "click.wav",
            "thunder": "thunder.wav",
            "powerup": "powerup.wav",
            "shield": "shield.wav",
            "shield_break": "shield_break.wav",
            "extra_life": "extra_life.wav",
            "chicken": "chicken.wav",
            "chick": "chick.wav",
            "engine": "engine_loop.ogg",
        }
        for key, fname in sfx_files.items():
            path = os.path.join(SFX_DIR, fname)
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(self.settings.sfx_volume)
                    self._sfx[key] = snd
                except Exception:
                    pass

    def _load_music(self):
        for fname in MUSIC_FILES:
            path = os.path.join(MUSIC_DIR, fname)
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    self._tracks.append((snd, snd.get_length()))
                except Exception:
                    pass

    # ---- SFX -----------------------------------------------------------
    def play_sfx(self, name):
        if not self.settings.sound_enabled:
            return
        if name in self._sfx:
            try:
                self._sfx[name].play()
            except Exception:
                pass

    # ---- Music ---------------------------------------------------------
    def play_music(self):
        if not self.settings.sound_enabled or not self._tracks:
            return
        if self._music_active or not self._music_channels:
            return
        self._chan_idx = 0
        self._track_idx = 0
        sound, length = self._tracks[0]
        ch = self._music_channels[0]
        try:
            ch.set_volume(self.settings.music_volume)
            ch.play(sound, fade_ms=self.START_FADE_MS)
        except Exception:
            return
        self._cur_len = length
        self._music_start = pygame.time.get_ticks()
        self._music_active = True

    def update(self, dt):
        """Advance the crossfade playlist. Call once per frame."""
        if not self._music_active or not self._tracks:
            return
        if not self.settings.sound_enabled:
            return
        elapsed = (pygame.time.get_ticks() - self._music_start) / 1000.0
        if elapsed >= max(0.5, self._cur_len - self.LOOP_LEAD_S):
            self._crossfade_next()

    def next_track(self):
        """Immediately crossfade to the next song (skip button)."""
        if not self._music_active or len(self._tracks) < 2:
            return
        if not self.settings.sound_enabled:
            return
        self._crossfade_next()

    def _crossfade_next(self):
        # Advance to the next track in the playlist (wrapping around).
        self._track_idx = (self._track_idx + 1) % len(self._tracks)
        sound, length = self._tracks[self._track_idx]
        old = self._music_channels[self._chan_idx]
        self._chan_idx = 1 - self._chan_idx
        new = self._music_channels[self._chan_idx]
        try:
            old.fadeout(self.MUSIC_FADE_MS)
            new.set_volume(self.settings.music_volume)
            new.play(sound, fade_ms=self.MUSIC_FADE_MS)
        except Exception:
            pass
        self._cur_len = length
        self._music_start = pygame.time.get_ticks()

    def stop_music(self):
        for ch in self._music_channels:
            try:
                ch.fadeout(600)
            except Exception:
                pass
        self._music_active = False

    def set_sound_enabled(self, val):
        self.settings.sound_enabled = val
        if not val:
            self.stop_music()
        else:
            self.play_music()

    def set_music_volume(self, vol):
        self.settings.music_volume = round(max(0.0, min(1.0, vol)), 2)
        for ch in self._music_channels:
            try:
                ch.set_volume(self.settings.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, vol):
        self.settings.sfx_volume = round(max(0.0, min(1.0, vol)), 2)
        for s in self._sfx.values():
            try:
                s.set_volume(self.settings.sfx_volume)
            except Exception:
                pass

    def update_volume(self):
        vol = self.settings.music_volume if self.settings.sound_enabled else 0.0
        for ch in self._music_channels:
            try:
                ch.set_volume(vol)
            except Exception:
                pass
        for s in self._sfx.values():
            try:
                s.set_volume(1.0 if self.settings.sound_enabled else 0.0)
            except Exception:
                pass
