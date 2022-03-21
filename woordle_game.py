import discord
from discord.utils import get
import numpy as np
from sympy import false

class WoordleGame:
    def __init__(self, author : discord.member, message = discord.message):
        self.word = "giraf"
        self.woordle_list = [letter for letter in self.word]
        self.author = author
        self.message = message
        self.board = [['⬛'] * 5 for _ in range(6)]
        self.row = 1
        self.column = 5
        self.playing = True
    
    def add_row(self):
        self.row += 1

    def right_guess(self, guess):
        return self.word.lower() == guess.lower()

    def stop(self):
        self.playing = False

    def display(self):
        board = ""
        for i in range(self.row):
            for j in range(self.column):
                board += self.board[i][j]
            board += "\n"
        return board

    def update_board(self, guess, client : discord.client):
        # Copy all letters from word
        temp_list = self.woordle_list.copy()
        # Handle all correct spots
        for letter in range(len(guess)):
            if guess[letter].lower() == self.word[letter].lower():
                temp_list.remove(guess[letter].lower())
                emoji_name = "green_" + str(guess[letter]).upper()
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))
            else:
                emoji_name = "gray_" + str(guess[letter]).upper()
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))
        # Handle all correct letters on wrong spots
        for letter in range(len(guess)):
            emoji_name = "yellow_" + str(guess[letter]).upper()
            green_emoji = "green_" + str(guess[letter]).upper()
            if self.board[self.row - 1][letter] != green_emoji and guess[letter].lower() in temp_list:
                temp_list.remove(guess[letter].lower())
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))



    