import discord
import random
import asyncio
import numpy as np
from discord.utils import get
from constants import BOGGLE_BLOCKS, BOGGLE_STATE
from typing import Union, List


class BoggleGuess():

    def __init__(self, player: discord.member, guess: str, valid: bool = True) -> None:
        self.player = player
        self.guess = guess
        self.valid = valid

    def is_valid(self):
        return self.valid

    def set_invalid(self):
        self.valid = False

    def get_guess(self):
        return self.guess

    def __eq__(self, other: object) -> bool:
        return self.guess == other.guess


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
        self.game_time = 180
        self.guesses = {player: [] for player in self.players}
        self.results = {player: 0 for player in self.players}
        self.found_words = {}  # key=word, value=players

        with open("data/bogglewords.txt", 'r') as file:
            self.words = set(line.strip().upper() for line in file)

    # TODO: add button to rotate the board
    def show_board(self, client: discord.Client):
        board = ""
        for i in range(self.board_size):
            for j in range(self.board_size):
                emoji_name = "gray_" + self.board[i][j]
                board += str(get(client.emojis, name=emoji_name))
                if j == self.board_size - 1:
                    board += "\n"
        return board

    def check_surrounding_letters(self, possibilities, guess):
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

    def is_valid(self, player, guess) -> Union[None, BoggleGuess]:
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

    def add_guess(self, player, guess):
        guess = guess.upper()
        boggle_guess = self.is_valid(player, guess)
        if boggle_guess:
            boggle_guess = BoggleGuess(player, guess, True)
            if guess not in self.found_words:
                self.found_words[guess] = [boggle_guess]
            elif boggle_guess not in self.found_words[guess]:
                self.found_words[guess].append(boggle_guess)
            print("Added guess", guess)

    def calculate_results(self):
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

    async def start(self):
        self.state = BOGGLE_STATE[1]
        for player in self.players:
            embed = discord.Embed(title="Boggle:", description=self.show_board(self.client))
            await player.send(embed=embed)

        print("before sleep")
        await asyncio.sleep(self.game_time)
        print("after sleep")

        self.state = BOGGLE_STATE[2]
        self.calculate_results()

        self.state = BOGGLE_STATE[3]
        return self.results
