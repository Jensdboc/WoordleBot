import discord
import sqlite3
import collections

from datetime import datetime
from discord.ext import commands

OWNER_ID = 656916865364525067
ELEMENTS_ON_PAGE = 5


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
        try:
            self.cur.execute("""
                            SELECT credits FROM player
                            WHERE id = ?
                            """, (ctx.author.id,))
            datas = self.cur.fetchall()

            if datas == []:
                credits = 0
            else:
                credits = datas[0][0]

            view = Shop(ctx.author.id, credits, self.db, self.cur, self.client)
            await ctx.reply(view=view)
        except Exception as e:
            print(e)

    @commands.command(usage="=rank <type> <member>",
                      description="""Show the ranking. If no member is provided, show the author itself.""")
    async def rank(self, ctx: commands.Context, type: str = "credit", member: discord.Member = None):
        """
        Show the ranking

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        type : str
            Type of stats
        member : discord.Member
            The member to show the ranking of
            Only needed in case of progress
        """
        id = ctx.author.id if member is None else member.id
        view = Ranking(id, type, self.db, self.cur, self.client)
        try:
            await ctx.reply(view=view)
        except Exception as e:
            print(e)

    @commands.command(usage="""
                            =add_game "2023-11-10" "656916865364525067" "5" "0:00:10.000" "3" "TESTSPAARDBOVEN" "0" "30" "5"
                            """,
                      description="""
                                  Add a manual game to the database. This can only be done by the owner.
                                  """)
    async def add_game(self, ctx, date: str, id: str, guesses: str,
                       timediff: str, counter: str, wordstring: str,
                       wrong_guesses: str, credits_gained: str, xp_gained: str):
        """
        Add a manual game to the database

        Parameters
        ----------
        date : str
            Date to be inserted
        id : str
            Id to be inserted
        guesses : str
            Guesses to be inserted
        timediff : str
            Timediff to be inserted
        counter : str
            Counter to be inserted
        wordstring : str
            Wordstring to be inserted
        wrong_guesses : str
            Wrong_guesses to be inserted
        credits_gained : str
            Credits to be inserted
        xp_gained : str
            Xp to be inserted
        """
        # =add_game "2023-11-10" "656916865364525067" "5" "0:00:10.000" "3" "TESTSPAARDBOVEN" "0" "30" "5"
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
                                 INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses, credits_gained, xp_gained)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                 """, (id, guesses, timediff, counter, wordstring, wrong_guesses, credits_gained, xp_gained))
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

    @commands.command()
    async def query(self, ctx: commands.Context, query: str):
        try:
            if ctx.author.id == OWNER_ID:
                self.cur.execute(query)
                datas = self.cur.fetchall()
                self.db.commit()
                if datas != []:
                    await ctx.send(datas)
            await ctx.message.add_reaction("✔️")
        except Exception as e:
            await ctx.send(e)
            await ctx.message.add_reaction("❌")


class Shop(discord.ui.View):
    def __init__(self, id: int, credits: int, db: sqlite3.Connection, cur: sqlite3.Cursor, client: discord.Client):
        """
        Initialize the Shop UI

        Parameters
        ----------
        id : int
            Id of the requested user
        credits : int
            Amount of credits from the user
        db : sqlite3.Connection
            Database with games and player info
        cur : sqlite3.Cursor
            Cursor to access the database
        client : discord.Client
            Bot itself
        """
        super().__init__()
        self.value = None
        self.id = id
        self.credits = credits
        self.db = db
        self.cur = cur
        self.client = client
        self.view = None
        self.page = 0

    @discord.ui.button(label="Skins", style=discord.ButtonStyle.blurple, row=1)
    async def skin(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.view = "skins"
        self.page = 0
        embed = self.make_embed(self.view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Items", style=discord.ButtonStyle.blurple, row=1)
    async def item(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.view = "items"
        self.page = 0
        embed = self.make_embed(self.view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Colors", style=discord.ButtonStyle.blurple, row=1)
    async def color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.view = "colors"
        self.page = 0
        embed = self.make_embed(self.view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.grey, row=1)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        embed = self.make_embed(self.view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.grey, row=1)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        embed = self.make_embed(self.view)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 1", style=discord.ButtonStyle.blurple, row=2)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = self.buy_item(self.page * ELEMENTS_ON_PAGE)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 2", style=discord.ButtonStyle.blurple, row=2)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = self.buy_item(self.page * ELEMENTS_ON_PAGE + 1)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 3", style=discord.ButtonStyle.blurple, row=2)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = self.buy_item(self.page * ELEMENTS_ON_PAGE + 2)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 4", style=discord.ButtonStyle.blurple, row=2)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = self.buy_item(self.page * ELEMENTS_ON_PAGE + 3)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 5", style=discord.ButtonStyle.blurple, row=2)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = self.buy_item(self.page * ELEMENTS_ON_PAGE + 4)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    def buy_item(self, index: int) -> str:
        """
        Update the database when buying an item

        Parameters
        ----------
        index : int
            Index of the item shown in embed

        Returns
        -------
        feedback : str
            Feedback message
        """
        try:
            # Retrieve item
            self.cur.execute("""
                             SELECT * FROM {}
                             """.format(self.view))
            datas = self.cur.fetchall()
            if (index >= len(datas)):
                return "No such item available!"
            item_to_buy = datas[index]

            # Check if item is already present or reached max
            self.cur.execute("""
                             SELECT * FROM {}
                             WHERE name = ? AND id = ?
                             """.format(f"{self.view}_player"), (item_to_buy[0], self.id))
            old_player_data = self.cur.fetchall()

            if old_player_data != []:
                if self.view == "items" and old_player_data[0][2] >= item_to_buy[4]:
                    return f"You have reached the maximum amount of **{item_to_buy[0]}** already!"
                elif self.view == "skins" or self.view == "colors":
                    # Unselect all the previous ones
                    self.cur.execute("""
                                     UPDATE {}
                                     SET selected = False
                                     WHERE selected = True
                                     """.format(f"{self.view}_player"))
                    # Select current one
                    self.cur.execute("""
                                     UPDATE {}
                                     SET selected = True
                                     WHERE name = ? AND id = ?
                                     """.format(f"{self.view}_player"), (item_to_buy[0], self.id))
                    return f"You selected **{item_to_buy[0]}**!"

            # Check if player has enough credits
            if (self.credits - item_to_buy[2] < 0):
                return f"You don't have enough credits. You have **{self.credits}**!"
            self.credits -= item_to_buy[2]
            self.cur.execute("""
                             UPDATE player
                             SET credits = ?
                             WHERE id = ?
                             """, (self.credits, self.id))
            if self.view == "items":
                if old_player_data != []:
                    self.cur.execute("""
                                    UPDATE {}
                                    SET amount = amount + 1
                                    WHERE name = ? AND id = ?
                                    """.format(f"{self.view}_player"), (item_to_buy[0], self.id))
                else:
                    self.cur.execute("""
                                    INSERT INTO {} (name, id, amount)
                                    VALUES (?, ?, ?)
                                    """.format(f"{self.view}_player"), (item_to_buy[0], self.id, 1))
            elif self.view == "skins" or self.view == "colors":
                # Unselect all the previous ones
                self.cur.execute("""
                                 UPDATE {}
                                 SET selected = False
                                 WHERE selected = True
                                 """.format(f"{self.view}_player"))
                # Insert and select current one
                self.cur.execute("""
                                 INSERT INTO {} (name, id, selected)
                                 VALUES (?, ?, ?)
                                 """.format(f"{self.view}_player"), (item_to_buy[0], self.id, True))
            self.db.commit()
        except Exception as e:
            print(e)
        return f"Succesfully bought **{item_to_buy[0]}**!"

    def make_embed(self, type: str, feedback: str = None) -> discord.Embed:
        """
        Return the current shop embed

        Parameters
        ----------
        type : str
            The type of items
        feedback : str
            Optional string for feedback

        Returns
        -------
        embed : discord.Embed
            The embed that will be showed
        """
        title = f"Shop {type} - Credits: {self.credits}"
        message = ""
        try:
            self.cur.execute("""
                             SELECT * FROM {}
                             """.format(type))
            datas = self.cur.fetchall()
            self.cur.execute("""
                             SELECT * FROM {}
                             WHERE id = ?
                             """.format(f"{type}_player"), (self.id,))
            player_datas = self.cur.fetchall()
            inventory = []
            selected = None
            for player_data in player_datas:
                inventory.append(player_data[0])
                if type != "items" and player_data[2] == 1:
                    selected = player_data[0]
            # Set the page number if necessary
            if self.page > len(datas) // ELEMENTS_ON_PAGE:
                self.page = len(datas) // ELEMENTS_ON_PAGE
            for i, data in enumerate(datas):
                if i >= self.page * ELEMENTS_ON_PAGE and i < (self.page + 1) * ELEMENTS_ON_PAGE:
                    rank = i + 1 - self.page * ELEMENTS_ON_PAGE
                    if selected == data[0]:
                        message += "*__"
                    message += f"{rank}: {data[0]} **[{data[3]}]**: {data[2]} credits"
                    if data[0] in inventory:
                        # Print amount of checkmarks in case of item
                        if type == "items":
                            for _ in range(player_datas[0][2]):
                                message += "\t :white_check_mark:"
                        elif selected == data[0]:
                            message += "\t :white_check_mark: __*"
                        else:
                            message += "\t :white_check_mark:"
                    message += "\n"
            if feedback:
                message += feedback
        except Exception as e:
            print(e)
        embed = discord.Embed(title=title, description=message)
        return embed


class Ranking(discord.ui.View):
    def __init__(self, id: int, type: str, db: sqlite3.Connection, cur: sqlite3.Cursor, client: discord.Client):
        """
        Initialize the Ranking UI

        Parameters
        ----------
        id : int
            Id of the requested user
        type : str
            Type of stats
        db : sqlite3.Connection
            Database with games and player info
        cur : sqlite3.Cursor
            Cursor to access the database
        client : discord.Client
            Bot itself
        """
        super().__init__()
        self.value = None
        self.id = id
        self.db = db
        self.cur = cur
        self.client = client
        self.type = type
        self.view = "all"
        self.list = ["credit", "xp", "current streak", "games played", "games won", "average guesses"]
        for index, type in enumerate(self.list):
            if self.type == type:
                self.index = index

    @discord.ui.button(label="All time", style=discord.ButtonStyle.blurple)
    async def all(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the all time stats

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        self.view = "all"
        datas, title, currency = self.get_all_data()
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Monthly", style=discord.ButtonStyle.green)
    async def month(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the monthly stats

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        self.view = "month"
        datas, title, currency = self.get_month_data()
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next stat", style=discord.ButtonStyle.red)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the current selected stats and show the next stat option

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        self.index = (self.index + 1) % len(self.list)
        self.type = self.list[self.index]
        button.label = self.list[(self.index + 1) % len(self.list)].capitalize()

        if self.view == "all":
            datas, title, currency = self.get_all_data()
        elif self.view == "month":
            datas, title, currency = self.get_month_data()
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

    def get_all_data(self):
        """
        Get data for view all

        Returns
        -------
        datas : list
            Data containing the users information
        title : str
            Title of the embed
        currency : str
            Unit of the data
        """
        try:
            title = f"Top users (all time) in {self.type}"
            if self.type == "credit":
                self.cur.execute("""
                                 SELECT id, credits FROM player
                                 ORDER BY credits DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "credits"
            elif self.type == "xp":
                self.cur.execute("""
                                 SELECT id, xp FROM player
                                 ORDER BY xp DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "xp"
            elif self.type == "current streak":
                self.cur.execute("""
                                 SELECT id, current_streak FROM player
                                 ORDER BY current_streak DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "days"
            elif self.type == "games played":
                self.cur.execute("""
                                 SELECT person, COUNT(*) FROM game
                                 GROUP BY person
                                 ORDER BY COUNT(*) DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "games"
            elif self.type == "games won":
                self.cur.execute("""
                                 SELECT person, COUNT(*) FROM game
                                 WHERE guesses != "X"
                                 GROUP BY person
                                 ORDER BY COUNT(*) DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "games"
            elif self.type == "average guesses":
                self.cur.execute("""
                                 SELECT person, AVG(guesses) FROM game
                                 GROUP BY person
                                 ORDER BY AVG(guesses) DESC
                                 """)
                datas = self.cur.fetchall()
                currency = "guesses"
            return datas, title, currency
        except Exception as e:
            print(e)

    def get_month_data(self):
        """
        Get data for view month

        Returns
        -------
        datas : list
            Data containing the users information
        title : str
            Title of the embed
        currency : str
            Unit of the data
        """
        try:
            title = f"Top users (monthly) in {self.type}"
            if self.type == "credit":
                self.cur.execute("""
                                    SELECT game.person, SUM(game.credits_gained) FROM game
                                    WHERE game.id IN (
                                    SELECT woordle_games.id FROM woordle_games
                                    WHERE strftime("%m", woordle_games.date) = ?
                                        AND strftime("%Y", woordle_games.date) = ?
                                    )
                                    GROUP BY game.person
                                    ORDER BY SUM(game.credits_gained) DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "credits"
            elif self.type == "xp":
                self.cur.execute("""
                                    SELECT game.person, SUM(game.xp_gained) FROM game
                                    WHERE game.id IN (
                                    SELECT woordle_games.id FROM woordle_games
                                    WHERE strftime("%m", woordle_games.date) = ?
                                        AND strftime("%Y", woordle_games.date) = ?
                                    )
                                    GROUP BY game.person
                                    ORDER BY SUM(game.xp_gained) DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "xp"
            elif self.type == "current streak":
                self.cur.execute("""
                                    SELECT id, current_streak FROM player
                                    ORDER BY current_streak DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "days"
            elif self.type == "games played":
                self.cur.execute("""
                                    SELECT person, COUNT(*) FROM game
                                    WHERE game.id IN (
                                    SELECT woordle_games.id FROM woordle_games
                                    WHERE strftime("%m", woordle_games.date) = ?
                                        AND strftime("%Y", woordle_games.date) = ?
                                    )
                                    GROUP BY person
                                    ORDER BY COUNT(*) DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "games"
            elif self.type == "games won":
                self.cur.execute("""
                                    SELECT person, COUNT(*) FROM game
                                    WHERE guesses != "X" AND
                                    game.id IN (
                                    SELECT woordle_games.id FROM woordle_games
                                    WHERE strftime("%m", woordle_games.date) = ?
                                        AND strftime("%Y", woordle_games.date) = ?
                                    )
                                    GROUP BY person
                                    ORDER BY COUNT(*) DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "games"
            elif self.type == "average guesses":
                self.cur.execute("""
                                    SELECT person, AVG(guesses) FROM game
                                    WHERE game.id IN (
                                    SELECT woordle_games.id FROM woordle_games
                                    WHERE strftime("%m", woordle_games.date) = ?
                                        AND strftime("%Y", woordle_games.date) = ?
                                    )
                                    GROUP BY person
                                    ORDER BY AVG(guesses) DESC
                                    """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
                datas = self.cur.fetchall()
                currency = "guesses"
            return datas, title, currency
        except Exception as e:
            print(e)

    async def make_embed(self, datas: list, title: str, currency: str):
        """
        Make embed for requested stats

        Parameters
        ----------
        datas : list
            Data containing the users information
        title : str
            Title of the embed
        currency : str
            Unit of the data

        Returns
        -------
        embed : discord.Embed
            Embed with ranking
        """
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
                    message += f"{rank}: **{user.display_name}**: {str(data[1])} {currency}\n"
                else:
                    message += f"{rank}: {user.display_name}: {str(data[1])} {currency}\n"
        except Exception as e:
            print(e)
        embed = discord.Embed(title=title, description=message)
        return embed


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Database(client))
