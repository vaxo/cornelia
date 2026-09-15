"""Cornelia - a 2D flappy-bird-style car game (pygame).

Entry point. Cross-platform (macOS / Windows / Linux):

    python3 main.py
"""
import os
import sys

# Make sure the project root is importable regardless of where we're launched
# from (matters for `python main.py` vs bundled builds).
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from src.core.game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
