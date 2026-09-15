from config.constants import SCORE_PER_PASS, COMBO_BASE_BONUS


class ScoreManager:
    def __init__(self):
        self.score = 0
        self.best_score = 0
        self.combo = 0

    def reset(self, best=None):
        self.score = 0
        self.combo = 0
        if best is not None:
            self.best_score = best

    def on_pass(self, multiplier=1):
        self.combo += 1
        bonus = COMBO_BASE_BONUS * max(0, self.combo - 1)
        gained = (SCORE_PER_PASS + bonus) * multiplier
        self.score += int(gained)
        if self.score > self.best_score:
            self.best_score = self.score
        return int(gained)

    def reset_combo(self):
        self.combo = 0

    def get_score(self):
        return self.score

    def get_combo(self):
        return self.combo

    def get_best(self):
        return self.best_score
