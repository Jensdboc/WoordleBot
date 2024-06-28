from typing import Union

from boggle_game import BoggleGame


class BoggleGames:

    def __init__(self) -> None:
        self.games = []

    def add_game(self, game: BoggleGame) -> None:
        """
        Add a BoggleGame from the list of BoggleGames
        """
        if game.game_id in [g.game_id for g in self.games]:
            return None
        self.games.append(game)

    def remove_game(self, game: BoggleGame) -> None:
        """
        Remove a BoggleGame from the list of BoggleGames
        """
        self.games.remove(game)

    def get_game(self, game_id: int) -> Union[BoggleGame, None]:
        """
        Get a BoggleGame from the list of BoggleGames

        Parameters
        ----------
        game_id : int
            ID of the game
        Return
        ------
        game : BoggleGame
            The BoggleGame if exist, else None
        """
        for game in self.games:
            if game.game_id == game_id:
                return game
        return None
