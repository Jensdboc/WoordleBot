import discord
from typing import Union

from woordle_game import WoordleGame


def check_word(word: str) -> bool:
    """
    Check if a given word appears in "woorden.txt"
    Returns
    -------
    check : bool
        Return True if word in file, otherwise False
    """
    with open("woorden.txt", 'r') as all_words:
        words = all_words.read().splitlines()
        return word.upper() in words


class WoordleGames:
    """Class representing the collection of woordle games of a certain date"""

    def __init__(self):
        self.games = []
        self.word = None

    def set_word(self, word: str) -> bool:
        """
        Set the word corresponding to the date

        Parameters
        ----------
        word : str
            Word corresponding to the date
        Return
        ------
        set : bool
            Return True if succeeded, otherwise False
        """
        if len(word) == 5 and check_word(word):
            self.word = word
            return True
        else:
            return False

    def add_woordle_game(self, woordlegame: WoordleGame) -> None:
        """
        Add a WoordleGame to the list of WoordleGames

        Parameters
        ----------
        woordlegame : WoordleGame
            WoordleGame to be added
        """
        for game in self.games:
            if game.author == woordlegame.author:
                return None
        self.games.append(woordlegame)

    def remove_woordle_game(self, game: WoordleGame) -> None:
        """
        Remove a WoordleGame from the list of WoordleGames

        Parameters
        ----------
        woordlegame : WoordleGame
            WoordleGame to be removed
        """
        self.games.remove(game)

    def get_woordle_game(self, author: discord.member) -> Union[WoordleGame, None]:
        """
        Get a WoordleGame from the list of WoordleGames

        Parameters
        ----------
        author: discord.member
            Author to search the WoordleGame for
        Return
        ------
        game : WoordleGame
            Return the game of the author from the current date if possible, else None
        """
        for game in self.games:
            if game.author == author:
                return game
        return None

    def reset_woordle_games(self) -> None:
        """
        Clear list of WoordleGames from current date
        """
        self.games = []
