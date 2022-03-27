import discord

from woordle_game import WoordleGame

def check_word(word):
    with open("woorden.txt", 'r') as all_words:
        words = all_words.read().splitlines()
        return word.upper() in words

class WoordleGames:

    def __init__(self):
        self.games = []
        self.word = None

    def set_word(self, word):
        if len(word) == 5 and check_word(word):
            self.word = word
            return True
        else:
            return False

    def add_woordle_game(self, woordlegame : WoordleGame):
        for game in self.games:
            if game.author == woordlegame.author:
                return "You already started a Woordle today!"
        self.games.append(woordlegame)
        return None
        
    def remove_woordle_game(self, game : WoordleGame):
        self.games.remove(game)
    
    def get_woordle_game(self, author : discord.member):
        for game in self.games:
            if game.author == author:
                return game
        return None

    def reset_woordle_games(self):
        self.games = []