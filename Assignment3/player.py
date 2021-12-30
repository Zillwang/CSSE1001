"""Class for representing a Player entity within the game."""

__version__ = "1.1.0"

from game.entity import DynamicEntity


class Player(DynamicEntity):
    """A player in the game"""
    _type = 3
    _invincible_step = 0

    def __init__(self, name: str = "Mario", max_health: float = 20):
        """Construct a new instance of the player.

        Parameters:
            name (str): The player's name
            max_health (float): The player's maximum & starting health
        """
        super().__init__(max_health=max_health)

        self._name = name
        self._score = 5
        self._realScore = 0

    def get_name(self) -> str:
        """(str): Returns the name of the player.
        """
        return self._name

    def attack(self, world, fireball):
        """

        """
        x = self.get_position()[0]
        y = self.get_position()[1]
        world.add_mob(fireball, x + 22, y)

    def get_score(self) -> int:
        """(int): Get the players current score.
        """
        return self._score

    def get_realscore(self):
        return self._realScore

    def change_realscore(self, change):
        self._realScore += change
        self.renderUI()

    def change_score(self, change: float = 1):
        """Increase the players score by the given change value.
        """
        self._score += change

    def damage(self, n=1):
        if self._invincible_step == 0:
            self._score = self._score - n
            self.renderUI()

    def heal(self, n=1):
        self._score = self._score + n
        self.renderUI()

    def invincible(self, step):
        self._invincible_step = step

    def renderUI(self):
        self._ui.setScore(self._score)
        self._ui.setPercent(self._score / self._max_health)
        self._ui.setRealScore(self.get_realscore())

    def connectUI(self, ui):
        self._ui = ui
        self.renderUI()

    def step(self, time_delta, game_data):
        if self._invincible_step > 0:
            self._invincible_step -= 1

    def __repr__(self):
        return f"Player({self._name!r})"
