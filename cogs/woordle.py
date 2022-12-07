from ast import alias
import discord
from discord.ext import commands, tasks
from discord.utils import get

from woordle_game import *
from woordle_games import *

import random
from datetime import datetime, timedelta
import time

import sqlite3

#*********************#
#User commands woordle#
#*********************#

class Woordle(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.games = WoordleGames()
        self.db = sqlite3.connect("woordle.db")
        cur = self.db.cursor()
        self.wordstring = ""
        self.wrong_guesses = 0
        self.counter = int(cur.execute('SELECT id FROM woordle_games WHERE id = (SELECT max(id) FROM woordle_games)').fetchall()[0][0])  
        self.games.set_word(cur.execute('SELECT word FROM woordle_games WHERE id = (SELECT max(id) FROM woordle_games)').fetchall()[0][0])
        print("Counter: ", self.counter)
        print("Word: ", self.games.word)
        cur.close()
        # Reset all games and get new words by restart every 24 hours
        # self.day_loop.start()

    def check_word(self, word):
        with open("all_words.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            return word.upper() in words

    @commands.command(usage="=woordle", 
                      description="Guess the next word for the Woordle",
                      aliases = ['w'])
    async def woordle(self, ctx, guess=None):
        if ctx.channel.type != discord.ChannelType.private:
            embed = discord.Embed(title="Woordle", description="Woops, maybe you should start a game in private!", color=ctx.author.color)        
            await ctx.send(embed=embed)
            return
        channel = self.client.get_channel(878308113604812880)  # Other-games, De Boomhut Van Nonkel Jerry: 878308113604812880 
                                                               # Bot-spam, De Boomhut Van Nonkel Jerry: 765211470744518658
                                                               # Private channel: 1003268990476496906
                                                               # Emilia server: 1039877136179277864
        channel2 = self.client.get_channel(1039877136179277864)
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
            self.wrong_guesses += 1
            await ctx.message.add_reaction("❌")
            # embed = discord.Embed(title="Woordle", description="Your guess has to be a valid word!", color=ctx.author.color)        
            # await ctx.send(embed=embed)
            return

        def show_results(id):
            # Make embed
            woordle_game.stop()
            woordle_game.display_end()
            timediff = str(timedelta(seconds=(time.time() - woordle_game.timestart)))[:-3]
            embed = discord.Embed(title="Woordle " + str(self.counter) + " "+ str(woordle_game.row) + "/6 by " + ctx.author.name + ": " + timediff, description=woordle_game.display_end(), color=ctx.author.color)        
            # Process information
            cur = self.db.cursor()
            cur.execute('INSERT INTO game VALUES (?, ?, ?, ?, ?, ?)', (id, str(woordle_game.row), timediff, self.counter, self.wordstring, self.wrong_guesses))
            cur.execute("""
                UPDATE woordle_games
                SET number_of_people = number_of_people + 1
                WHERE id = ?;
            """, (str(self.counter),))  # This has to be a a string, can't insert integers
            self.db.commit()
            return embed

        # Get woordle and check if the game is valid
        woordle_game = self.games.get_woordle_game(ctx.author)
        if woordle_game == None:
            woordle_game = WoordleGame(self.games.word, ctx.author, ctx.message, time.time())
            message = self.games.add_woordle_game(woordle_game)
            # Woordle was already started
            if message != None:
                embed = discord.Embed(title="Woordle", description=message, color=ctx.author.color)        
                await ctx.send(embed=embed)
            else:    
                # Update board with guess, create message and add row
                woordle_game.update_board(guess, self.client)
                embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=0xff0000)        
                self.wordstring += guess
                woordle_game.message = await ctx.send(embed=embed)
                if woordle_game.right_guess(guess):
                    await channel.send(embed = show_results(ctx.author.id))
                    await channel2.send(embed = show_results(ctx.author.id))
                woordle_game.add_row()
        elif not woordle_game.playing:
            embed = discord.Embed(title="Woordle", description="You have already finished the Woordle!", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            # Update board with guess, edit message
            woordle_game.update_board(guess, self.client)
            embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=ctx.author.color)        
            self.wordstring += guess
            await woordle_game.message.edit(embed=embed)
            if woordle_game.right_guess(guess):
                await channel.send(embed = show_results(ctx.author.id))
                await channel2.send(embed = show_results(ctx.author.id))
            elif woordle_game.row < 6:
                woordle_game.add_row()
            else: 
                woordle_game.stop()
                timediff = str(timedelta(seconds=(time.time() - woordle_game.timestart)))
                embed_private = discord.Embed(title="Woordle", description="Better luck next time, the word was " + woordle_game.word + "!", color=ctx.author.color)        
                embed = discord.Embed(title="Woordle " + str(self.counter) + " "+ "X/6 by " + ctx.author.name + ": " + timediff[:-3], description=woordle_game.display_end(), color=ctx.author.color)        
                await ctx.send(embed=embed_private)
                await channel.send(embed=embed)
                await channel2.send(embed=embed)
                # Process information
                cur = self.db.cursor()
                cur.execute('INSERT INTO game VALUES (?, ?, ?, ?, ?, ?)', (id, "failed", timediff, self.counter, self.wordstring, self.wrong_guesses))
                cur.execute("""
                    UPDATE woordle_games
                    SET number_of_people = number_of_people + 1
                    WHERE id = ?;
                """, str(self.counter))  # This has to be a a string, can't insert integers
                self.db.commit()

    @commands.command(usage="=woordlereset", 
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

    @commands.command(usage="=setword <word>", 
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
        self.counter += 1
        self.games.reset_woordle_games()
        print("The word has been changed to "+self.games.word)

#Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Woordle(client))
