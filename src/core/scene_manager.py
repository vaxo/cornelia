class SceneManager:
    def __init__(self, game):
        self._game = game
        self._scenes = {}
        self._current_key = None
        self._current = None

    def register(self, key, screen):
        self._scenes[key] = screen

    def change(self, key, **kwargs):
        if key not in self._scenes:
            return
        self._current_key = key
        self._current = self._scenes[key]
        self._current.on_enter(**kwargs)

    def get_current(self):
        return self._current

    def get(self, key):
        return self._scenes.get(key)

    def get_key(self):
        return self._current_key

    def handle_events(self, events):
        if self._current:
            self._current.handle_events(events)

    def update(self, dt):
        if self._current:
            self._current.update(dt)

    def render(self, surface):
        if self._current:
            self._current.render(surface)
