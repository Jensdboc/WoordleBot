import discord
import random
from sqlite3 import Timestamp
from discord.utils import get  # For emojis
from constants import SKIN_MAP, LETTER_MAP

WORD_LENGTH = 5
MAX_GUESSES = 6
ALPHABET = [letter for letter in "abcdefghijklmnopqrstuvwxyz"]


class WoordleGame:
    """Class representing a woordle game"""

    def __init__(self, word, author: discord.member, id: int,
                 message: discord.message, time: Timestamp) -> None:
        """
        Initializes a WoordleGame

        Parameters
        ----------
        word : str
            Word for the current WoordleGame
        author : discord.member
            Author who created the WoordleGame
        id : int
            ID of current WoordleGames
        message : discord.message
            Discord message with the first guess
        time : Timestamps
            Start time of sending the discord message
        """
        self.word = word
        self.woordle_list = [letter for letter in self.word] if self.word is not None else None
        self.author = author
        self.id = id
        self.message = message
        self.board = [['⬛'] * WORD_LENGTH for _ in range(MAX_GUESSES)]
        self.row = 1
        self.playing = True
        self.timestart = time
        self.wrong_guesses = 0
        self.wordstring = ""
        self.failed = True
        self.time = 0
        self.letters = LETTER_MAP

    def add_row(self) -> None:
        """
        Add a row to the WoordleGame
        """
        self.row += 1

    def right_guess(self, guess: str) -> bool:
        """
        Check if the current guess is the correct one

        Return
        ------
        check : bool
            Return True if correct, else False
        """
        return self.word.lower() == guess.lower()

    def stop(self) -> None:
        """
        End the playing state of the WoordleGame
        """
        self.playing = False

    def display(self, client: discord.client) -> str:
        """
        Construct a string representing the current board of the WoordleGame

        Parameters
        ----------
        client : discord.client
            Discord Woordle bot

        Return
        ------
        board : str
            String representation of the current board of the WoordleGame
        """
        # Set current board
        board = ""
        for i in range(self.row):
            for j in range(WORD_LENGTH):
                board += self.board[i][j]
            board += "\n"
        board += "\n"

        # Set list of status of chosen letters
        for index, letter in enumerate(ALPHABET):
            if index == len(ALPHABET)/2:
                board += "\n"
            if get(client.emojis, name=self.letters[letter]) is None:
                board += self.letters[letter]
            else:
                board += str(get(client.emojis, name=self.letters[letter]))
        return board

    def display_end(self, client: discord.client, skin: str = "Default") -> str:
        """
        Convert the board string to a board string with emojis

        Return
        ------
        end_board : str
            String representation of the current board of the WoordleGame
        """
        end_board = ""
        for i in range(self.row):
            for j in range(WORD_LENGTH):
                if self.board[i][j][2:7] == "green":
                    color = "green"
                elif self.board[i][j][2:8] == "yellow":
                    color = "yellow"
                elif self.board[i][j][2:6] == "gray":
                    color = "gray"
                # Handle special cases
                if skin == "Random":
                    emoji_name = f"{color}_{str(random.choice(ALPHABET)).upper()}"
                    end_board += str(get(client.emojis, name=emoji_name))
                else:
                    end_board += SKIN_MAP[skin][color]
            end_board += "\n"
        end_board += "\n"
        return end_board

    def update_board(self, guess: str, client: discord.client) -> None:
        """
        Update the board according to the current guess

        Parameters
        ----------
        guess : str
            Current guess
        client : discord.client
            Discord Woordle bot
        """
        temp_list = self.woordle_list.copy()

        # Handle all correct and incorrect spots
        for index, letter in enumerate(guess):
            if letter.upper() == self.word[index].upper():
                temp_list.remove(letter.upper())
                emoji_name = "green_" + str(letter).upper()
            else:
                emoji_name = "gray_" + str(letter).upper()
            self.board[self.row - 1][index] = str(get(client.emojis, name=emoji_name))
            if self.letters[str(letter).lower()] != "green_" + str(letter).upper():
                self.letters[str(letter).lower()] = emoji_name

        # Handle all correct letters on wrong spots
        for index, letter in enumerate(guess):
            yellow_name = "yellow_" + str(letter).upper()
            green_emoji = "green_" + str(letter).upper()
            if self.board[self.row - 1][index] != str(get(client.emojis, name=green_emoji)) and letter.upper() in temp_list:
                temp_list.remove(letter.upper())
                self.board[self.row - 1][index] = str(get(client.emojis, name=yellow_name))
                if self.letters[str(letter).lower()] != green_emoji:
                    self.letters[str(letter).lower()] = yellow_name
