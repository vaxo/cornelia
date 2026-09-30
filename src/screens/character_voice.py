"""Idle character calls: the chicken clucks, the chick peeps,
the sun yawns and the dalmatian barks while you fly.

Mixed into the two play screens. A character only has a voice if its PlayerCar
carries a `voice` SFX key (the cars don't), and it only calls out while the run
is actually live — not before the first flap, not after a crash.
"""

# Milliseconds between calls.
VOICE_INTERVAL = 8000


class CharacterVoiceMixin:
    def init_voice(self):
        self._voice_timer = 0.0

    def tick_voice(self, dt, car):
        voice = getattr(car, "voice", None)
        if not voice:
            return
        self._voice_timer += dt
        if self._voice_timer >= VOICE_INTERVAL:
            # Subtract rather than zero so the cadence doesn't drift on long frames
            self._voice_timer -= VOICE_INTERVAL
            self.audio.play_sfx(voice)
