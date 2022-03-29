from ast import alias
import discord
from discord.ext import commands, tasks
from discord.utils import get

from woordle_game import *
from woordle_games import *

import random
from datetime import datetime

#*********************#
#User commands woordle#
#*********************#

class Woordle(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.games = WoordleGames()
        # Reset all games and get new words by restart every 24 hours
        self.day_loop.start()

    def check_word(self, word):
        with open("all_words.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            return word.upper() in words

    @commands.command()
    async def test(self, ctx):
        woordlegame = self.games.get_woordle_game(ctx.author)
        print(woordlegame.letters["a"])
        await ctx.send(":regional_indicator_a:")

    @commands.command(usage="!woordle", 
                      description="Guess the next word for the Woordle",
                      aliases = ['w'])
    async def woordle(self, ctx, guess=None):
        # Check if there is a current word
        if self.games.word is None:
            embed = discord.Embed(title="Woordle", description="Woops, there is no word yet!", color=ctx.author.color)        
            await ctx.send(embed=embed)
            return
        # Delete message and check if the guess is valid
        # await ctx.message.delete()
        if guess == None:
            embed = discord.Embed(title="Woordle", description="Please insert a guess!", color=ctx.author.color)        
            await ctx.send(embed=embed)
            return
        if not self.check_word(guess) or len(guess) != 5:
            await ctx.message.add_reaction("❌")
            # embed = discord.Embed(title="Woordle", description="Your guess has to be a valid word!", color=ctx.author.color)        
            # await ctx.send(embed=embed)
            return

        # Get woordle and check if the game is valid
        woordle_game = self.games.get_woordle_game(ctx.author)
        if woordle_game == None:
            woordle_game = WoordleGame(self.games.word, ctx.author, ctx.message)
            message = self.games.add_woordle_game(woordle_game)
            if message != None:
                embed = discord.Embed(title="Woordle", description=message, color=ctx.author.color)        
                await ctx.send(embed=embed)
            else:    
                # Update board with guess, create message and add row
                woordle_game.update_board(guess, self.client)
                embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=0xff0000)        
                woordle_game.message = await ctx.send(embed=embed)
                if woordle_game.right_guess(guess):
                    woordle_game.stop()
                    embed = discord.Embed(title="Woordle", description="Congratulations, " + ctx.author.name + " finished the Woordle in: " + str(woordle_game.row) + "/6!", color=ctx.author.color)        
                    await ctx.send(embed=embed)
                woordle_game.add_row()
        elif not woordle_game.playing:
            embed = discord.Embed(title="Woordle", description="You have already finished the Woordle!", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            # Update board with guess, edit message
            woordle_game.update_board(guess, self.client)
            embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=ctx.author.color)        
            await woordle_game.message.edit(embed=embed)
            if woordle_game.right_guess(guess):
                woordle_game.stop()
                embed = discord.Embed(title="Woordle", description="Congratulations, " + ctx.author.name + " finished the Woordle in: " + str(woordle_game.row) + "/6!", color=ctx.author.color)        
                await ctx.send(embed=embed)
            elif woordle_game.row < 6:
                woordle_game.add_row()
            else: 
                woordle_game.stop()
                embed = discord.Embed(title="Woordle", description="The game has finished, the word was "+woordle_game.word+"!", color=ctx.author.color)        
                await ctx.send(embed=embed)

    @commands.command(usage="!woordlereset", 
                      description="Reset all current wordlegames",
                      help="This is an admin-only command",
                      aliases = ['wr'])
    async def woordlereset(self, ctx):
        # Check if author is admin
        if ctx.author.id != 656916865364525067:
            embed = discord.Embed(title="Woordle", description="You do not have permission to execute this command!", color=0xff0000)        
            await ctx.send(embed=embed)
        else:
            # Clear all games
            self.games.reset_woordle_games()
            embed = discord.Embed(title="Woordle", description="All the games have been reset!", color=0x11806a)        
            await ctx.send(embed=embed)

    @commands.command(usage="!setword <word>", 
                      description="Set the current word",
                      help="This is an admin-only command",
                      aliases = ['sw'])
    async def setword(self, ctx, word):
        if ctx.author.id != 656916865364525067:
            embed = discord.Embed(title="Woordle", description="You do not have permission to execute this command!", color=0xff0000)        
            await ctx.send(embed=embed)
        else:
            # Set current word
            if self.games.set_word(word):
                embed = discord.Embed(title="Woordle", description=word + " has been set as the new word!", color=0x11806a)        
                await ctx.send(embed=embed)
            else:
                await ctx.message.add_reaction("❌")
                embed = discord.Embed(title="Woordle", description=word + " is not a valid word!", color=0x11806a)        
                await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def day_loop(self):
        with open("woorden.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            word = random.choice(words)
            self.games.set_word(word)
        self.games.reset_woordle_games()
        print("The word has been changed to "+self.games.word)

#Allows to connect cog to bot    
def setup(client):
    client.add_cog(Woordle(client))