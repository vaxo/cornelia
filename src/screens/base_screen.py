"""Base class shared by every screen (scene) in the game.

It wires up the handful of shared services each screen needs and defines the
lifecycle hooks the SceneManager calls. Subclasses override what they use.
"""


class BaseScreen:
    def __init__(self, game):
        self.game = game
        self.assets = game.assets
        self.audio = game.audio
        self.save = game.save

    def on_enter(self, **kwargs):
        """Called by SceneManager each time this screen becomes active."""
        pass

    def handle_events(self, events):
        """Process the frame's input events."""
        pass

    def update(self, dt):
        """Advance game logic; dt is milliseconds since last frame."""
        pass

    def render(self, surface):
        """Draw this screen onto *surface*."""
        pass
