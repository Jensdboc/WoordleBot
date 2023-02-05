import discord
from sqlite3 import Timestamp
from discord.utils import get

class WoordleGame:

    def __init__(self, word, author : discord.member, message = discord.message, time = Timestamp):
        self.word = word
        self.woordle_list = [letter for letter in self.word] if self.word != None else None
        self.author = author
        self.message = message
        self.board = [['⬛'] * 5 for _ in range(6)]
        self.row = 1
        self.column = 5
        self.playing = True
        self.timestart = time
        self.letters = {"a":":regional_indicator_a:","b":":regional_indicator_b:","c":":regional_indicator_c:",
                        "d":":regional_indicator_d:","e":":regional_indicator_e:","f":":regional_indicator_f:",
                        "g":":regional_indicator_g:","h":":regional_indicator_h:","i":":regional_indicator_i:",
                        "j":":regional_indicator_j:","k":":regional_indicator_k:","l":":regional_indicator_l:",
                        "m":":regional_indicator_m:","n":":regional_indicator_n:","o":":regional_indicator_o:",
                        "p":":regional_indicator_p:","q":":regional_indicator_q:","r":":regional_indicator_r:",
                        "s":":regional_indicator_s:","t":":regional_indicator_t:","u":":regional_indicator_u:",
                        "v":":regional_indicator_v:","w":":regional_indicator_w:","x":":regional_indicator_x:",
                        "y":":regional_indicator_y:","z":":regional_indicator_z:"}            
    
    def add_row(self):
        self.row += 1

    def right_guess(self, guess):
        return self.word.lower() == guess.lower()

    def stop(self):
        self.playing = False

    def display(self, client : discord.client):
        alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        board = ""
        for i in range(self.row):
            for j in range(self.column):
                board += self.board[i][j]
            board += "\n"
        board += "\n"
        for index, letter in enumerate(alphabet):
            if index == 13:
                board += "\n"
            if get(client.emojis, name=self.letters[letter]) == None:
                board += self.letters[letter]
            else:
                board += str(get(client.emojis, name=self.letters[letter]))
        return board

    def display_end(self):
        end_board = ""
        colors = {"green":"🟩","yellow":"🟨","gray":"⬛"}
        for i in range(self.row):
            for j in range(self.column):
                if self.board[i][j][2:7] == "green":
                    end_board += colors["green"]
                elif self.board[i][j][2:8] == "yellow":
                    end_board += colors["yellow"]
                elif self.board[i][j][2:6] == "gray":
                    end_board += colors["gray"]
            end_board += "\n"
        end_board += "\n"
        # print(end_board)
        return end_board

    def update_board(self, guess, client : discord.client):
        # Copy all letters from word
        temp_list = self.woordle_list.copy()
        # Handle all correct spots
        for letter in range(len(guess)):
            if guess[letter].lower() == self.word[letter].lower():
                temp_list.remove(guess[letter].upper())
                emoji_name = "green_" + str(guess[letter]).upper()
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))
                self.letters[str(guess[letter]).lower()] = emoji_name
            else:
                emoji_name = "gray_" + str(guess[letter]).upper()
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))
                if self.letters[str(guess[letter]).lower()] != "green_" + str(guess[letter]).upper():
                    self.letters[str(guess[letter]).lower()] = emoji_name
        # Handle all correct letters on wrong spots
        for letter in range(len(guess)):
            emoji_name = "yellow_" + str(guess[letter]).upper()
            green_emoji = "green_" + str(guess[letter]).upper()
            if self.board[self.row - 1][letter] != str(get(client.emojis, name=green_emoji)) and guess[letter].upper() in temp_list:
                # print(self.board[self.row - 1])
                temp_list.remove(guess[letter].upper())
                self.board[self.row - 1][letter] = str(get(client.emojis, name=emoji_name))
                if self.letters[str(guess[letter]).lower()] != green_emoji:
                    self.letters[str(guess[letter]).lower()] = emoji_name               