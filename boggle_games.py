from typing import Union

from boggle_game import BoggleGame
from constants import BOGGLE_STATE


class BoggleGames:

    def __init__(self) -> None:
        self.games = []

    def add_game(self, game: BoggleGame) -> None:
        if game.game_id in [g.game_id for g in self.games]:
            return None
        self.games.append(game)

    def remove_game(self, game: BoggleGame) -> None:
        self.games.remove(game)

    def remove_old_games(self) -> None:
        for game in self.games:
            if game.state == BOGGLE_STATE[3]:
                self.remove_game(game)

    def get_game(self, game_id: int) -> Union[BoggleGame, None]:
        for game in self.games:
            if game.game_id == game_id:
                return game
        return None
