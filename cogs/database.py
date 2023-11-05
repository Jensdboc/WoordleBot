import discord
import sqlite3
import collections

from datetime import datetime
from discord.ext import commands

OWNER_ID = 656916865364525067

class Database(commands.Cog):
    """Class for interactions with the database"""

    def __init__(self, client: discord.Client) -> None:
        """
        Initialize the Database cog

        Parameters
        ----------
        client : discord.Client
            Discord Woordle bot
        """
        self.client = client
        self.db = sqlite3.connect("woordle.db")
        self.cur = self.db.cursor()

    @commands.command()
    async def get_games(self, ctx: commands.Context):
        """
        Retrieve the tables woordle_games

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        self.cur.execute("""
                         SELECT * FROM woordle_games
                         """)
        print("Fetching games")
        print(self.cur.fetchall())
        self.cur.close

    @commands.command()
    async def get_game(self, ctx: commands.Context):
        """
        Retrieve the tables game

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        self.cur.execute("""
                         SELECT * FROM game
                         """)
        print("Fetching game")
        print(self.cur.fetchall())
        self.cur.close

    @commands.command()
    async def get_player(self, ctx: commands.Context):
        """
        Retrieve the tables player

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        self.cur.execute("""
                         SELECT * FROM player
                         """)
        print("Fetching player")
        print(self.cur.fetchall())
        self.cur.close

    @commands.command()
    async def stats(self, ctx: commands.Context, member: discord.Member):
        """
        Send the statistics of a member

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        member : discord.Member
            Member the show the statistics of
        """
        def convert_str_to_time(str: str):
            """
            Converts a string to a float representing time

            Parameters
            ----------
            str: str
                String to be converted
            """
            str_split = str.split(":")
            return float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

        def game_won(id: int) -> bool:
            """
            Check if the game was won or not

            Parameters
            ----------
            id: int
                ID of game played

            Return
            ------
            won : bool
                Returns True if won, else False
            """
            self.cur.execute("""
                             SELECT guesses FROM game
                             WHERE id = ?
                             """, (id,))
            guess = self.cur.fetchall()[0][0]
            return guess != "X"

        def longest_streak(ids: list[int]) -> int:
            """
            Return the longest streak of games played

            Parameters
            ----------
            ids : list[int]
                List of games played

            Return
            ------
            streak : int
                Longest streak of games played
            """
            sorted(ids)
            streaks = []
            start_id = ids[0]
            streak = 1
            for id in ids[1:]:
                if id == start_id + 1:
                    streak += 1
                else:
                    streaks.append(streak)
                    streak = 1
                start_id = id
            streaks.append(streak)
            return max(streaks)

        def longest_win_streak(ids: list[int]) -> int:
            """
            Return the longest win streak of games played

            Parameters
            ----------
            ids : list[int]
                List of games played

            Return
            ------
            streak : int
                Longest win streak of games played
            """
            sorted(ids)
            streaks = []
            first = True
            streak = 0
            start_id = -1
            # Check if the first game has been won or not
            for id in ids:
                if (first or id == start_id + 1) and game_won(id):
                    streak += 1
                    start_id = id
                    first = False
                else:
                    streaks.append(streak)
                    streak = 0
                    first = True
            streaks.append(streak)
            return max(streaks)

        if member is None:
            embed = discord.Embed(title="Woordle stats", description="You have to provide a member!", color=ctx.author.color)
            await ctx.send(embed=embed)
            return

        self.cur.execute("""
                         SELECT * FROM game
                         WHERE person = ?
                         """, (member.id,))
        datas = self.cur.fetchall()
        game_count = len(datas)
        if game_count == 0:
            embed = discord.Embed(title=f"Woordle stats from {member.display_name}", description="This user hasn't played any games so far!", color=ctx.author.color)
            return

        guess_count = 0
        total_time = 0
        all_words = ""
        wrong_guess_count = 0
        fastest_time = None
        ids = []
        game_id = {}
        for data in datas:
            guess_count += data[1] if data[1] != 'X' else 6
            game_time = convert_str_to_time(data[2])
            total_time += game_time
            if fastest_time is None:
                fastest_time = total_time
            elif fastest_time > game_time:
                fastest_time = game_time
            ids.append(data[3])
            all_words += data[4]
            game_id.update({data[3]: data[4]})
            wrong_guess_count += data[5]

        message = f"Total games: {str(game_count)}\n"
        message += f"Average number of guesses: {str(round(guess_count/game_count, 3))}\n"
        message += f"Average time of guesses: {str(round(total_time/game_count, 3))} seconds\n"
        message += f"Highest streak: {str(longest_streak(ids))}\n"
        message += f"Highest win streak: {str(longest_win_streak(ids))}\n"
        message += f"Fastest time: {str(fastest_time)} seconds \n"
        message += f"Total wrong guesses: {str(wrong_guess_count)}\n"
        message += f"Favourite letter: {str(collections.Counter(all_words).most_common(1)[0][0])}\n"
        embed = discord.Embed(title=f"Woordle stats {member.display_name}", description=message, color=member.color)
        await ctx.send(embed=embed)

    @commands.command(usage="=shop",
                      description="Show which items the user can buy")
    async def shop(self, ctx: commands.Context):
        """
        Show the shop of a member

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        self.cur.execute("""
                         SELECT credits FROM player
                         WHERE id = ?
                         """, (ctx.author.id,))
        credits = self.cur.fetchall()[0][0]
        embed = discord.Embed(title=f"Woordle shop {ctx.author.display_name}", description=f"You have {credits} credits!", color=ctx.author.color)
        await ctx.send(embed=embed)

    @commands.command(usage="=rank <member>",
                      description="""Show the ranking. If no member is provided, show the author itself """,
                      aliases=['credit', 'credits'])
    async def rank(self, ctx: commands.Context, member: discord.Member=None):
        """
        Show the ranking

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        member: discord.Member
            The member to show the ranking of
            Only needed in case of progress        
        """
        id = ctx.author.id if member is None else member.id
        view = Ranking(id, self.db, self.cur, self.client)
        try:
            await ctx.reply(view=view)
        except Exception as e:
            print(e)

    @commands.command(usage="""
                            =add_game "2023-11-10" "656916865364525067" "5" "0:00:10.000" "3" "TESTSPAARDBOVEN" "0" "30"
                            """,
                      description="""
                                  Add a manual game to the database. This can only be done by the owner.
                                  """)
    async def add_game(self, ctx, date: str, id: str, guesses: str, 
                       timediff: str, counter: str, wordstring: str, 
                       wrong_guesses: str, credits_gained: str):
        """
        Add a manual game to the database

        Parameters
        ----------
        date: str
            Date to be inserted
        id: str
            Id to be inserted
        guesses: str
            Guesses to be inserted
        timediff: str
            Timediff to be inserted
        counter: str
            Counter to be inserted
        wordstring: str
            Wordstring to be inserted
        wrong_guesses: str
            Wrong_guesses to be inserted
        credits_gained: str
            Credits to be inserted
        """
        # =add_game "2023-11-10" "656916865364525067" "5" "0:00:10.000" "3" "TESTSPAARDBOVEN" "0" "30"
        # Change "2023-11-10" and "3"
        if ctx.author.id == OWNER_ID:
            try:
                self.cur.execute("""
                                 INSERT OR IGNORE INTO woordle_games (date, number_of_people, word)
                                 VALUES (?,?,?)
                                 """, [date, 1, "TESTS"])
            except Exception as e:
                await ctx.send(e)
            try:
                self.cur.execute("""
                                 INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses, credits_earned)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)
                                 """, (id, guesses, timediff, counter, wordstring, wrong_guesses, credits_gained))
            except Exception as e:
                await ctx.send(e)
            try:    
                self.cur.execute("""
                                SELECT * FROM player 
                                WHERE id = ?
                                """, (id,))
                player_data = self.cur.fetchall()
                if player_data == []:
                    self.cur.execute("""
                                INSERT INTO player (id, credits, xp, current_streak)
                                VALUES (?, ?, ?, ?)
                                """, (id, "0", "0", "0"))
            except Exception as e:
                await ctx.send(e)
            try:
                self.cur.execute("""
                                 UPDATE player
                                 SET credits = credits + ? 
                                 WHERE id = ?
                                 """, (int(credits_gained), id))
            except Exception as e:
                await ctx.send(e)

            self.db.commit()
            await ctx.send("Game added")
            
class Ranking(discord.ui.View):
    def __init__(self, id: int, db: sqlite3.Connection, cur: sqlite3.Cursor, client: discord.Client):
        """
        Initialize the Ranking UI

        Parameters
        ----------
        id : int
            Id of the requested user
        db: sqlite3.Connection
            Database with games and player info
        cur: sqlite3.Cursor
            Cursor to access the database
        client: discord.Client
            Bot itself
        """
        super().__init__()
        self.value = None
        self.id = id
        self.db = db
        self.cur = cur
        self.client = client

    @discord.ui.button(label="All time", style=discord.ButtonStyle.blurple)
    async def all(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the all time stats

        Parameters
        ----------
        interaction: discord.Interaction 
            Used to handle button interaction
        button: discord.ui.Button
            Button object
        """
        try:
            self.cur.execute("""
                            SELECT id, credits FROM player
                            ORDER BY credits DESC
                            """)
            datas = self.cur.fetchall()
            title = "Top users (all time):"
            message = ""
            try:
                for i, data in enumerate(datas):
                    user = await self.client.fetch_user(data[0])
                    requested_user = await self.client.fetch_user(self.id)
                    if i == 0:
                        rank = ":first_place:"
                    elif i == 1:
                        rank = ":second_place:"
                    elif i == 2:
                        rank = ":third_place:"
                    else: 
                        rank = str(i+1)
                    if user == requested_user:
                        message += rank + ": **" + user.display_name + "**: " + str(data[1]) + " credits\n"
                    else:
                        message += rank + ": " + user.display_name + ": " + str(data[1]) + " credits\n"
            except Exception as e:
                print(e)
            embed = discord.Embed(title=title, description=message)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(e)

    @discord.ui.button(label="Monthly", style=discord.ButtonStyle.green)
    async def month(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the monthly stats

        Parameters
        ----------
        interaction: discord.Interaction 
            Used to handle button interaction
        button: discord.ui.Button
            Button object
        """
        try:
            self.cur.execute("""
                             SELECT game.person, SUM(game.credits_earned) FROM game
                             WHERE game.id IN (
                                SELECT woordle_games.id FROM woordle_games
                                WHERE strftime("%m", woordle_games.date) = ?
                                    AND strftime("%Y", woordle_games.date) = ?
                                )
                             GROUP BY game.person
                             """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = self.cur.fetchall()
            title = "Top users (monthly):"
            message = ""
            try:
                for i, data in enumerate(datas):
                    user = await self.client.fetch_user(data[0])
                    requested_user = await self.client.fetch_user(self.id)
                    if i == 0:
                        rank = ":first_place:"
                    elif i == 1:
                        rank = ":second_place:"
                    elif i == 2:
                        rank = ":third_place:"
                    else: 
                        rank = str(i+1)
                    if user == requested_user:
                        message += rank + ": **" + user.display_name + "**: " + str(data[1]) + " credits\n"
                    else:
                        message += rank + ": " + user.display_name + ": " + str(data[1]) + " credits\n"
            except Exception as e:
                print(e)
            embed = discord.Embed(title=title, description=message)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(e)

    # @discord.ui.button(label="Progress", style=discord.ButtonStyle.red)
    # async def progress(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     """
    #     Show to UI for the progress of a certain user

    #     Parameters
    #     ----------
    #     interaction: discord.Interaction 
    #         Used to handle button interaction
    #     button: discord.ui.Button
    #         Button object
    #     """
    #     try:
    #         requested_user = await self.client.fetch_user(self.id)
    #         embed = discord.Embed(title=f"Progress of **{requested_user.display_name}**:", description="Currently WIP")
    #         await interaction.response.edit_message(embed=embed)
    #     except Exception as e:
    #         print(e)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Database(client))
