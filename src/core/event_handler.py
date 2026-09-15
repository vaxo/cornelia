import pygame


class EventHandler:
    def __init__(self, game):
        self._game = game

    def collect(self):
        # SCALED maps mouse events into logical coordinates, so no translation
        # is needed here.
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self._game.toggle_fullscreen()
            else:
                events.append(event)
        return events
