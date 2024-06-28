import discord
import random
import asyncio
import numpy as np
from discord.utils import get
from typing import Union, List

from constants import BOGGLE_BLOCKS, BOGGLE_STATE


class BoggleGuess():

    def __init__(self, player: discord.member, guess: str, valid: bool = True) -> None:
        self.player = player
        self.guess = guess
        self.valid = valid

    def is_valid(self) -> bool:
        """
        Check if the guess has not been guessed twice

        Return
        ------
        valid : bool
            If the guess is valid or not
        """
        return self.valid

    def set_invalid(self) -> None:
        """
        Set the guess to invalid
        """
        self.valid = False

    def get_guess(self) -> str:
        """
        Get the value of the guess

        Return
        ------
        guess : str
            The value of the guess
        """
        return self.guess

    def __eq__(self, other: object) -> bool:
        """
        Overwrite equal operator

        Return
        ------
        equal : bool
            If the guess is equal or not
        """
        return self.guess == other.guess and self.valid == other.valid


class BoggleGame():
    """Class representing a boggle game"""

    def __init__(self, players: List[discord.Member], client: discord.Client, game_id) -> None:
        self.players = players
        self.client = client
        self.game_id = game_id
        self.blocks = BOGGLE_BLOCKS.copy()
        random.shuffle(self.blocks)
        self.board_size = 4
        self.board = np.array([block[random.randint(0, 5)] for block in self.blocks]).reshape(self.board_size, self.board_size)

        self.state = BOGGLE_STATE[0]
        self.refresh_time = 30
        self.game_time = 180
        self.found_words = {}  # key=word, value=players
        self.results = None
        self.guesses = None

        with open("data/bogglewords.txt", 'r') as file:
            self.words = set(line.strip().upper() for line in file)

    def rotate_board(self) -> None:
        """
        Rotate the board 90 degrees to the left
        """
        self.board = np.rot90(self.board)

    def show_board(self, client: discord.Client, time: int = 0) -> discord.Embed:
        """
        Show the board in an embed

        Parameters
        ----------
        client : discord.Client
            Discord Woordle bot
        time : int
            Time spend in the game

        Return
        ------
        board : discord.Embed
            The embed with the board
        """
        board = ""
        for i in range(self.board_size):
            for j in range(self.board_size):
                emoji_name = "gray_" + self.board[i][j]
                board += str(get(client.emojis, name=emoji_name))
                if j == self.board_size - 1:
                    board += "\n"
        return discord.Embed(title="Boggle:", description=board + "\n" + "Time left: " + str(self.game_time - time) + "s")

    def show_words_per_player(self, player: discord.Member) -> discord.Embed:
        """
        Show the list of words guessed by the player

        Parameters
        ----------
        player : discord.Member
            The player to show the list of words of

        Return
        ------
        message : discord.Embed
            The embed with the list of words guessed by the player
        """
        message = ""
        for guess in self.guesses[player]:
            if guess.is_valid():
                message += guess.get_guess() + "\n"
            else:
                message += "~~" + guess.get_guess() + "~~\n"
        return discord.Embed(title="List of words:", description=message)

    def check_surrounding_letters(self, possibilities: List[(int, int)], guess: BoggleGuess) -> bool:
        """
        Check if the surrounding letters match the next letter in the guess

        Parameters
        ----------
        possibilities : List[(int, int)]
            List of previous coordinates of the guess
        guess : str
            The guess to check

        Return
        ------
        valid : bool
            If the guess has been found or not
        """
        current_i, current_j = possibilities[-1]
        for ii in range(max(0, current_i - 1), min(current_i + 2, self.board_size)):
            for jj in range(max(0, current_j - 1), min(current_j + 2, self.board_size)):
                if (ii, jj) not in possibilities and self.board[ii][jj] == guess[len(possibilities)]:
                    # Add next letter to possibilities and check for further letters
                    possibilities.append((ii, jj))
                    if len(possibilities) == len(guess):
                        return True
                    valid = self.check_surrounding_letters(possibilities, guess)
                    if valid:
                        return True
                    # Remove last letter from possibilities to search for other surrounding letters
                    possibilities.remove((ii, jj))
        return False

    def is_valid(self, player: discord.Member, guess: BoggleGuess) -> Union[None, BoggleGuess]:
        """
        Check if the guess is valid

        Parameters
        ----------
        player : discord.Member
            The player who made the guess
        guess : str
            The guess to check

        Return
        ------
        guess : BoggleGuess
            The guess if it is valid, else None
        """
        # Check if guess has been checked previously
        # Set previous guesses and the current one to invalid
        if guess in self.found_words:
            for boggle_guess in self.found_words[guess]:
                boggle_guess.set_invalid()
            return BoggleGuess(player, guess, False)

        # Check if guess is a valid word
        if guess not in self.words:
            return False

        # Check if guess is on the board
        # 1) Go over all possible positions on the board
        # 2) If the letter at the position matches the first letter of the guess, add it to possibilities
        # 3) Look for surrounding letters and see if they match the rest of the guess
        #   3a) If they do, add them to possibilities
        #   3b) If there are no surrounding letters, delete the last entry in possibilities and continue the previous loop
        # 4) Repeat until the word is found or until there are no more possibilities
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == guess[0]:
                    possibilities = [(i, j)]

                    if self.check_surrounding_letters(possibilities, guess):
                        return BoggleGuess(player, guess, True)

        return False

    def add_guess(self, player: discord.Member, guess: BoggleGuess) -> bool:
        """
        Add a guess to the game

        Parameters
        ----------
        player : discord.Member
            The player who made the guess
        guess : BoggleGuess
            The guess to add

        Return
        ------
        valid : bool
            If the guess is valid or not
        """
        guess = guess.upper()
        boggle_guess = self.is_valid(player, guess)
        if boggle_guess:
            boggle_guess = BoggleGuess(player, guess, True)
            if guess not in self.found_words.keys():
                self.found_words[guess] = [boggle_guess]
            elif boggle_guess not in self.found_words[guess]:
                self.found_words[guess].append(boggle_guess)
            return True

        return False

    def calculate_results(self) -> None:
        """
        Calculate the score for each player
        """
        self.results = {player: 0 for player in self.players}
        self.guesses = {player: [] for player in self.players}
        for guesses in self.found_words.values():
            if len(guesses) == 1:
                guess = guesses[0].guess
                player = guesses[0].player
                if len(guess) <= 4:
                    self.results[player] += 1
                elif len(guess) == 5:
                    self.results[player] += 2
                elif len(guess) == 6:
                    self.results[player] += 3
                elif len(guess) == 7:
                    self.results[player] += 5
                elif len(guess) >= 8:
                    self.results[player] += 11
            for guess in guesses:
                player = guess.player
                self.guesses[player].append(guess)

    async def start(self) -> dict[discord.Member, int]:
        """
        Execute the flow of a BoggleGame

        Return
        ------
        results : dict[discord.Member, int]
            The score for each player
        """
        self.state = BOGGLE_STATE[1]
        view = BoggleBoard(self.client, self)
        for player in self.players:
            board_message = await player.send(embed=self.show_board(self.client), view=view)

        for i in range(self.game_time):
            if i > 0:
                board_embed = self.show_board(self.client, i)
                if i % self.refresh_time == 0:
                    new_board_message = await player.send(embed=board_embed)
                    await board_message.delete()
                    board_message = new_board_message
                else:
                    await board_message.edit(embed=board_embed)
            await asyncio.sleep(1)

        self.state = BOGGLE_STATE[2]
        self.calculate_results()

        for player in self.players:
            await player.send(embed=self.show_words_per_player(player))

        self.state = BOGGLE_STATE[3]
        return self.results


class BoggleBoard(discord.ui.View):
    def __init__(self, client: discord.Client, game: BoggleGame):
        super().__init__()
        self.client = client
        self.game = game

    @discord.ui.button(label="↪️", style=discord.ButtonStyle.blurple)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.game.rotate_board()
        await interaction.response.edit_message(embed=self.game.show_board(), view=self)

    @discord.ui.button(label="↩️", style=discord.ButtonStyle.blurple)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for _ in range(3):
            self.game.rotate_board()
        await interaction.response.edit_message(embed=self.game.show_board(), view=self)
