import sqlite3
import time
import random
import discord
from discord.ext import commands, tasks
from datetime import timedelta

from woordle_game import WoordleGame
from woordle_games import WoordleGames

CHANNEL_ID = 1161262990989991936
RED_COLOR = 0xff0000
BLACK_COLOR = 0x000000


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
        self.cur = self.db.cursor()
        self.wordstring = ""
        self.wrong_guesses = 0
        self.counter = int(self.cur.execute("""
                                       SELECT id FROM woordle_games
                                       WHERE id = (SELECT max(id) FROM woordle_games)
                                       """).fetchall()[0][0])
        self.games.set_word(self.cur.execute("""
                                        SELECT word FROM woordle_games
                                        WHERE id = (SELECT max(id) FROM woordle_games)
                                        """).fetchall()[0][0])
        # TODO: set player color
        self.color = BLACK_COLOR

        with open("channels.txt", "r") as file:
            lines = file.readlines()
            self.channel_ids = [int(line[:-1]) for line in lines]

        print("Counter: ", self.counter)
        print("Word: ", self.games.word)

    async def check_valid_game(self, ctx: commands.Context, guess: str) -> bool:
        """
        Check if the game can be started/continued

        Parameters
        ----------
        ctx : commands.Context
            Context of the message
        guess : str
            The user's guess

        Returns
        -------
        valid : bool
            If the game is valid or not
        """
        embed = None
        # Check if the game is private
        if ctx.channel.type != discord.ChannelType.private:
            embed = discord.Embed(title="Woordle", description="Woops, maybe you should start a game in private!", color=RED_COLOR)
        # Check if there is a current word
        elif self.games.word is None:
            embed = discord.Embed(title="Woordle", description="Woops, there is no word yet!", color=RED_COLOR)
        # Delete message and check if the guess is valid
        elif guess is None:
            embed = discord.Embed(title="Woordle", description="Please insert a guess!", color=RED_COLOR)
        if embed is not None:
            await ctx.send(embed=embed)
        return embed is None

    async def check_valid_guess(self, ctx: commands.Context, guess: str) -> bool:
        """
        Check if the guess is a valid guess

        Parameters
        ----------
        ctx : commands.Context
            Context of the message
        guess : str
            The user's guess

        Returns
        -------
        valid : bool
            If the guess is valid or not
        """
        with open("all_words.txt", 'r') as all_words:
            words = all_words.read().splitlines()
        valid = guess.upper() in words and len(guess) == 5
        if not valid:
            self.wrong_guesses += 1
            await ctx.message.add_reaction("❌")
        return valid

    def show_results_and_push_database(self, ctx: commands.Context, id: int, woordle_game: WoordleGame, failed: bool = False) -> discord.Embed:
        """
        Process WoordleGame information

        Parameters
        ----------
        ctx : commands.Context
            Context of the message
        id : int
            ID of the player of the WoordleGame
        woordle_game : WoordleGame
            Current woordle game being played
        failed: bool
            Check if game has succeeded or not

        Return
        ------
        embed : discord.Embed
            Ending message of a WoordleGame
        """
        # Make embed
        woordle_game.stop()
        woordle_game.display_end()
        timediff = str(timedelta(seconds=(time.time() - woordle_game.timestart)))[:-3]
        if not failed:
            guesses = str(woordle_game.row)
            xp_gained = 5 if woordle_game.row < 4 else 3
        else:
            guesses = "X"
            xp_gained = 1
        public_embed = discord.Embed(title=f"Woordle {str(self.counter)} {guesses}/6 by {ctx.author.name}: {timediff}",
                                     description=woordle_game.display_end(), color=self.color)

        # Process information
        cur = self.db.cursor()
        self.cur.execute("""
                            SELECT * FROM player
                            WHERE id = ?
                            """, (id,))
        player_data = self.cur.fetchall()

        # If player not in the database yet, create player profile
        if player_data == []:
            cur.execute("""
                        INSERT INTO player (id, credits, xp, current_streak)
                        VALUES (?, ?, ?, ?)
                        """, (id, "0", "0", "0"))

        # Get current streak to calculate the credits gained
        # Every 10 streaks increase the multiplier by 5%
        self.cur.execute("""
                            SELECT current_streak FROM player
                            WHERE id = ?
                            """, (id,))
        if not failed:
            current_streak = self.cur.fetchall()[0][0] + 1
            if current_streak < 10:
                streak_credits = 0
            elif current_streak > 10 and current_streak < 25:
                streak_credits = 3
            elif current_streak > 25 and current_streak < 50:
                streak_credits = 5
            elif current_streak > 50 and current_streak < 100:
                streak_credits = 10
            elif current_streak > 100 and current_streak < 356:
                streak_credits = 15
            else:
                streak_credits = 20
            credits_gained = int(10 * (6 - woordle_game.row) + streak_credits)
        else:
            current_streak = 0

        self.cur.execute("""
                    UPDATE player
                    SET credits = credits + ?, xp = xp + ?, current_streak = ?
                    WHERE id = ?
                    """, (credits_gained, xp_gained, current_streak, id))
        self.cur.execute("""
                    INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses, credits_gained, xp_gained)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (id, guesses, timediff, self.counter, self.wordstring, self.wrong_guesses, credits_gained, xp_gained))
        self.cur.execute("""
                    UPDATE woordle_games
                    SET number_of_people = number_of_people + 1
                    WHERE id = ?;
                    """, (str(self.counter),))  # This has to be a a string, can't insert integers
        self.db.commit()
        return public_embed

    async def update_and_edit_game(self, ctx: commands.Context, guess: str, woordle_game: WoordleGame):
        woordle_game.update_board(guess, self.client)
        embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=self.color)
        self.wordstring += guess
        await woordle_game.message.edit(embed=embed)
        if woordle_game.right_guess(guess):
            result_embed = self.show_results_and_push_database(ctx.author.id)
            for id in self.channel_ids:
                channel = self.client.get_channel(id)
                await channel.send(embed=result_embed)
        elif woordle_game.row < 6:
            woordle_game.add_row()
        else:
            embed_private = discord.Embed(title="Woordle", description=f"Better luck next time, the word was {woordle_game.word}!", color=self.color)
            await ctx.send(embed=embed_private)
            result_embed = self.show_results_and_push_database(ctx.author.id, failed=True)
            for id in self.channel_ids:
                channel = self.client.get_channel(id)
                await channel.send(embed=result_embed)

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
        # Other-games, De Boomhut Van Nonkel Jerry: 878308113604812880
        # Emilia server: 1039877136179277864
        # Tom en Jerry: 1054342112474316810
        # Woordle server: 1161262990989991936
        # channel_ids = [878308113604812880, 1039877136179277864, 1054342112474316810, 1161262990989991936]

        # Perform checks
        if not await self.check_valid_game(ctx, guess):
            return
        if not await self.check_valid_guess(ctx, guess):
            return

        # Get woordle_game and check if the game is being played
        woordle_game = self.games.get_woordle_game(ctx.author)
        if woordle_game is None:
            # Check if (author, id) are already present in the database
            # This could happen if the bot was restarted and the author plays a second time this day
            past_game = self.cur.execute("""
                                         SELECT * FROM game
                                         WHERE person = ? AND id = ?
                                         """, (ctx.author.id, self.counter)).fetchall()
            if past_game == []:
                woordle_game = WoordleGame(self.games.word, ctx.author, self.counter, ctx.message, time.time())
                message = self.games.add_woordle_game(woordle_game)
                # Woordle was already started
                if message is not None:
                    embed = discord.Embed(title="Woordle", description=message, color=self.color)
                    await ctx.send(embed=embed)
                else:
                    # Update board with guess, create message and add row
                    woordle_game.update_board(guess, self.client)
                    embed = discord.Embed(title="Woordle", description=woordle_game.display(self.client), color=self.color)
                    self.wordstring += guess
                    woordle_game.message = await ctx.send(embed=embed)
                    if woordle_game.right_guess(guess):
                        result_embed = self.show_results_and_push_database(ctx.author.id)
                        for id in self.channel_ids:
                            channel = self.client.get_channel(id)
                            await channel.send(embed=result_embed)
                    woordle_game.add_row()
            else:
                embed = discord.Embed(title="Woordle", description="You have already finished the Woordle!", color=RED_COLOR)
                await ctx.send(embed=embed)
        elif not woordle_game.playing:
            embed = discord.Embed(title="Woordle", description="You have already finished the Woordle!", color=RED_COLOR)
            await ctx.send(embed=embed)
        else:
            # Update board with guess, edit message
            await self.update_and_edit_game(ctx, guess, woordle_game)

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
            embed = discord.Embed(title="Woordle", description="You do not have permission to execute this command!", color=RED_COLOR)
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
            embed = discord.Embed(title="Woordle", description="You do not have permission to execute this command!", color=RED_COLOR)
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
