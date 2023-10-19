import sqlite3
import time
import random
import discord
from discord.ext import commands, tasks
from datetime import timedelta

from woordle_game import WoordleGame
from woordle_games import WoordleGames

CHANNEL_ID = 1161262990989991936


class Woordle(commands.Cog):
    """Class for Woordle commands"""

    def __init__(self, client: discord.Client) -> None:
        """
        Initialize the Woordle cog

        Parameters
        ----------
        client : discord.Client
            Discord Woordle bot
        """
        self.client = client
        self.games = WoordleGames()
        self.db = sqlite3.connect("woordle.db")
        cur = self.db.cursor()
        self.wordstring = ""
        self.wrong_guesses = 0
        self.counter = int(cur.execute("""
                                       SELECT id FROM woordle_games
                                       WHERE id = (SELECT max(id) FROM woordle_games)
                                       """).fetchall()[0][0])
        self.games.set_word(cur.execute("""
                                        SELECT word FROM woordle_games
                                        WHERE id = (SELECT max(id) FROM woordle_games)
                                        """).fetchall()[0][0])
        print("Counter: ", self.counter)
        print("Word: ", self.games.word)
        cur.close()

    def check_word(self, word: str) -> bool:
        """
        Check if a given word appears in "all_words.txt"

        Returns
        -------
        check : bool
            Return True if word in file, otherwise False
        """
        with open("all_words.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            return word.upper() in words

    @commands.command(usage="=woordle",
                      description="Guess the next word for the Woordle",
                      aliases=['w'])
    async def woordle(self, ctx: commands.Context, guess: str = None):
        """
        Play one guess in a WoordleGame

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        guess : str
            Current guess in a WoordleGame
        """
        if ctx.channel.type != discord.ChannelType.private:
            embed = discord.Embed(title="Woordle", description="Woops, maybe you should start a game in private!", color=ctx.author.color)
            await ctx.send(embed=embed)
            return

        # Other-games, De Boomhut Van Nonkel Jerry: 878308113604812880
        # Bot-spam, De Boomhut Van Nonkel Jerry: 765211470744518658
        # Private channel: 1003268990476496906
        # Emilia server: 1039877136179277864
        # Tom en Jerry: 1054342112474316810
        # Woordle server: 1161262990989991936
        # channel_ids = [954028573830811703] # Bot-test
        # channel_ids = [878308113604812880, 1039877136179277864, 1054342112474316810, 1161262990989991936]

        with open("channels.txt", "r") as file:
            lines = file.readlines()
            channel_ids = [int(line[:-1]) for line in lines]

        # Check if there is a current word
        if self.games.word is None:
            embed = discord.Embed(title="Woordle", description="Woops, there is no word yet!", color=ctx.author.color)
            await ctx.send(embed=embed)
            return
        # Delete message and check if the guess is valid
        if guess is None:
            embed = discord.Embed(title="Woordle", description="Please insert a guess!", color=ctx.author.color)
            await ctx.send(embed=embed)
            return
        if not self.check_word(guess) or len(guess) != 5:
            self.wrong_guesses += 1
            await ctx.message.add_reaction("❌")
            return

        def show_results(id: int) -> discord.Embed:
            """
            Process WoordleGame information

            Parameters
            ----------
            id : int
                ID of the player of the WoordleGame

            Return
            ------
            embed : discord.Embed
                Ending message of a WoordleGame
            """
            # Make embed
            woordle_game.stop()
            woordle_game.display_end()
            timediff = str(timedelta(seconds=(time.time() - woordle_game.timestart)))[:-3]
            embed = discord.Embed(title=f"Woordle {str(self.counter)} {str(woordle_game.row)}/6 by {ctx.author.name}: {timediff}",
                                  description=woordle_game.display_end(), color=ctx.author.color)

            # Process information
            cur = self.db.cursor()
            cur.execute("""
                        INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (id, str(woordle_game.row), timediff, self.counter, self.wordstring, self.wrong_guesses))
            cur.execute("""
                        UPDATE woordle_games
                        SET number_of_people = number_of_people + 1
                        WHERE id = ?;
                        """, (str(self.counter),))  # This has to be a a string, can't insert integers
            self.db.commit()
            return embed

        # Get woordle and check if the game is valid
        woordle_game = self.games.get_woordle_game(ctx.author)
        if woordle_game is None:
            woordle_game = WoordleGame(self.games.word, ctx.author, ctx.message, time.time())
            message = self.games.add_woordle_game(woordle_game)
            # Woordle was already started
            if message is not None:
                embed = discord.Embed(title="Woordle", description=message, color=ctx.author.color)
                await ctx.send(embed=embed)
            else:
                # Update board with guess, create message and add row
                woordle_game.update_board(guess, self.client)
                embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=0xff0000)
                self.wordstring += guess
                woordle_game.message = await ctx.send(embed=embed)
                if woordle_game.right_guess(guess):
                    result_embed = show_results(ctx.author.id)
                    for id in channel_ids:
                        channel = self.client.get_channel(id)
                        await channel.send(embed=result_embed)
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
                result_embed = show_results(ctx.author.id)
                for id in channel_ids:
                    channel = self.client.get_channel(id)
                    await channel.send(embed=result_embed)
            elif woordle_game.row < 6:
                woordle_game.add_row()
            else:
                woordle_game.stop()
                timediff = str(timedelta(seconds=(time.time() - woordle_game.timestart)))
                embed_private = discord.Embed(title="Woordle", description=f"Better luck next time, the word was {woordle_game.word}!", color=ctx.author.color)
                await ctx.send(embed=embed_private)
                for id in channel_ids:
                    channel = self.client.get_channel(id)
                    embed = discord.Embed(title=f"Woordle {str(self.counter)} X/6 by {ctx.author.name}: {timediff[:-3]}",
                                          description=woordle_game.display_end(), color=ctx.author.color)
                    await channel.send(embed=embed)

                # Process information
                cur = self.db.cursor()
                cur.execute("""
                            INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, (ctx.author.id, "failed", timediff, self.counter, self.wordstring, self.wrong_guesses))
                cur.execute("""
                            UPDATE woordle_games
                            SET number_of_people = number_of_people + 1
                            WHERE id = ?;
                            """, str(self.counter))  # This has to be a a string, can't insert integers
                player_data = cur.execute("""
                                          SELECT * FROM player
                                          WHERE id = ?
                                          """, id)
                print(player_data)
                self.db.commit()

    @commands.command(usage="=woordlereset",
                      description="Reset all current wordlegames",
                      help="This is an admin-only command",
                      aliases=['wr'])
    async def woordlereset(self, ctx: commands.Context):
        """
        Reset all WoordleGames

        Parameter
        ---------
        ctx : commands.Context
            Context the command is represented in
        """
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
                      aliases=['sw'])
    async def setword(self, ctx: commands.Context, word: str):
        """
        Manually set a word

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        word : str
            Word to set
        """
        if ctx.author.id != 656916865364525067:
            embed = discord.Embed(title="Woordle", description="You do not have permission to execute this command!", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            # Set current word
            if self.games.set_word(word):
                embed = discord.Embed(title="Woordle", description=f"{word} has been set as the new word!", color=0x11806a)
                await ctx.send(embed=embed)
            else:
                await ctx.message.add_reaction("❌")
                embed = discord.Embed(title="Woordle", description=f"{word} is not a valid word!", color=0x11806a)
                await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def day_loop(self):
        """
        Loop changing the word every 24 hours
        """
        with open("woorden.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            word = random.choice(words)
            self.games.set_word(word)
        self.counter += 1
        self.games.reset_woordle_games()
        print(f"The word has been changed to {self.games.word}")


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Woordle(client))
