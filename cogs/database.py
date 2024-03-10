import discord
import sqlite3

from datetime import datetime
from discord.ext import commands, tasks

import access_database
from admincheck import admin_check
from constants import PREFIX

ELEMENTS_ON_PAGE = 5


def debug(message):
    with open("prints.txt", "a") as out:
        out.write(message + "\n")


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

    @commands.command(usage=f"{PREFIX}streak [id] [monthly]",
                      description="""
                                  Show the streak of a user given their id.
                                  For normal usage leave out the arguments.
                                  If no member is provided, show the author itself.
                                  Monthly should be 0/1 or False/True.
                                  """)
    async def streak(self, ctx: commands.Context, id: int = None, monthly: bool = False) -> None:
        """
        Show the streak for a user

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        id : int
            The id of the requested user
        monthly : bool
            True if monthly stats, else all stats
        """
        if id is None:
            id = ctx.author.id
        current_streak = access_database.get_current_streak(id, monthly)
        embed = discord.Embed(title="Current streak", description=f"Your current streak is {current_streak}")
        await ctx.reply(embed=embed)

    @commands.command(usage=f"{PREFIX}maxstreak [id] [monthly]",
                      description="""
                                  Show the maxstreak of a user given their id.
                                  For normal usage leave out the arguments.
                                  If no member is provided, show the author itself.
                                  Monthly should be 0/1 or False/True.
                                  """)
    async def maxstreak(self, ctx: commands.Context, id: int = None, monthly: bool = True) -> None:
        """
        Show the max streak for a user

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        id : int
            The id of the requested user
        monthly : bool
            True if monthly stats, else all stats
        """
        if id is None:
            id = ctx.author.id
        max_streak = access_database.get_max_streak(id, monthly)
        embed = discord.Embed(title="Max streak", description=f"Your max streak is {max_streak}")
        await ctx.reply(embed=embed)

    @commands.command(usage="=freeze",
                      description="Test the freeze streak embed")
    @commands.check(admin_check)
    async def freeze(self, ctx: commands.Context) -> None:
        """
        Test the freeze streak

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        test_counter = 10
        view = UseFreezeStreak(ctx.author.id, test_counter, self.db, self.cur, self.client)
        color = access_database.get_user_color(self.client, ctx.author.id)
        try:
            embed = discord.Embed(title="Oh ow, you missed a day!", description="Do you want to use a freeze streak?", color=color)
            await ctx.reply(embed=embed, view=view)
        except Exception as e:
            print("Exception in sending UseFreezeStreak after a game: ", e)

    @commands.command(usage=f"{PREFIX}medals [member]",
                      description="""
                                  Show the amount of medals.
                                  If no member is provided, show the author itself.
                                  """)
    async def medals(self, ctx: commands.Context, user: discord.User = None) -> None:
        """
        Show the amount of medals for a user

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        user : discord.User
            The requested user
        """
        if user is None:
            id = ctx.author.id
            name = ctx.author.name
        else:
            id = user.id
            name = user.name
        places = [":first_place:", ":second_place:", ":third_place:"]
        medals = await access_database.get_medals(id)
        description = ""
        for place, medal in zip(places, medals):
            description += f"{place}: {medal}\n"
        embed = discord.Embed(title=f"Medals of {name}:", description=description, color=access_database.get_user_color(self.client, id))
        await ctx.reply(embed=embed)

    @commands.command(usage=f"{PREFIX}shop",
                      description="Show which items the user can buy",
                      aliases=['shopping'])
    async def shop(self, ctx: commands.Context):
        """
        Show the shop of a member

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        credits = access_database.get_amount_of_credits(ctx.author.id)
        view = Shop(ctx.author.id, credits, self.db, self.cur, self.client)
        await ctx.reply(view=view)

    @commands.command(usage=f"{PREFIX}rank <type> <member>",
                      description="""
                                  Show the ranking.
                                  If no member is provided, show the author itself.
                                  """,
                      aliases=["ranking"])
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
    @commands.check(admin_check)
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
    @commands.check(admin_check)
    async def query(self, ctx: commands.Context, query: str):
        try:
            self.cur.execute(query)
            datas = self.cur.fetchall()
            self.db.commit()
            if datas != []:
                await ctx.send(datas)
            await ctx.message.add_reaction("✔️")
        except Exception as e:
            await ctx.send(e)
            await ctx.message.add_reaction("❌")

    @commands.command()
    @commands.check(admin_check)
    async def addmedals(self, ctx: commands.Context):
        types = ["xp", "games played", "games won", "average guesses"]
        places = [":first_place:", ":second_place:", ":third_place:"]
        for t in types:
            datas, title, currency = access_database.get_all_data(t)
            try:
                for rank, data in enumerate(datas[:3]):
                    await access_database.add_medal(self.client, rank, data[0], t)
                    user = await self.client.fetch_user(data[0])
                    embed = discord.Embed(title="Montly results", description=f"Congratulations, you got a {places[rank + 1]} in the category: **{t}**")
                    await user.send(embed=embed)
            except Exception as e:
                print(e)

    @tasks.loop(hours=24)
    async def DateChecker(self):
        """
        Check if it is the first day of the month and reward monthly medals
        """
        types = ["xp", "games played", "games won", "average guesses"]
        places = [":first_place:", ":second_place:", ":third_place:"]
        if datetime.now().day == 1:
            for t in types:
                datas, title, currency = access_database.get_all_data(t)
                try:
                    for rank, data in enumerate(datas[:3]):
                        await access_database.add_medal(self.client, rank, data[0], t)
                        user = await self.client.fetch_user(data[0])
                        embed = discord.Embed(title="Montly results", description=f"Congratulations, you got a {places[rank + 1]} in the category: **{t}**")
                        await user.send(embed=embed)
                except Exception as e:
                    print(e)


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
        self.color = access_database.get_user_color(self.client, self.id)

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
        feedback = await self.buy_item(self.page * ELEMENTS_ON_PAGE)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 2", style=discord.ButtonStyle.blurple, row=2)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = await self.buy_item(self.page * ELEMENTS_ON_PAGE + 1)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 3", style=discord.ButtonStyle.blurple, row=2)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = await self.buy_item(self.page * ELEMENTS_ON_PAGE + 2)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 4", style=discord.ButtonStyle.blurple, row=2)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = await self.buy_item(self.page * ELEMENTS_ON_PAGE + 3)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Buy/Select 5", style=discord.ButtonStyle.blurple, row=2)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        feedback = await self.buy_item(self.page * ELEMENTS_ON_PAGE + 4)
        embed = self.make_embed(self.view, feedback)
        await interaction.response.edit_message(embed=embed, view=self)

    async def buy_item(self, index: int) -> str:
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
            if index >= len(datas):
                return "No such item available!"
            item_to_buy = datas[index]

            if item_to_buy[2] == -1:
                return "No such item available!"

            # Check if item is already present or reached max
            self.cur.execute("""
                             SELECT * FROM {}
                             WHERE name = ? AND id = ?
                             """.format(f"{self.view}_player"), (item_to_buy[0], self.id))
            old_player_data = self.cur.fetchall()

            if old_player_data != []:
                if self.view == "items" and old_player_data[0][2] >= item_to_buy[4]:
                    if item_to_buy[0] == "Freeze streak":
                        """-----ACHIEVEMENT CHECK-----"""
                        await access_database.add_achievement(self.client, "Cold as ice", self.id)
                        """-----ACHIEVEMENT CHECK-----"""
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
                    self.db.commit()
                    if self.view == "skins":
                        """-----ACHIEVEMENT CHECK-----"""
                        await access_database.add_achievement(self.client, "Look how fancy", self.id)
                        """-----ACHIEVEMENT CHECK-----"""
                    return f"You selected **{item_to_buy[0]}**!"

            # Check if player has enough credits
            if (self.credits - item_to_buy[2] < 0):
                """-----ACHIEVEMENT CHECK-----"""
                await access_database.add_achievement(self.client, "Haaa, poor!", self.id)
                """-----ACHIEVEMENT CHECK-----"""
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

            """-----ACHIEVEMENT CHECK-----"""
            await access_database.add_achievement(self.client, "Thank you, come again", self.id)
            """-----ACHIEVEMENT CHECK-----"""
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
            player_data_dict = {item[0]: item[2] for item in player_datas}

            # Set the page number if necessary
            if self.page > len(datas) // ELEMENTS_ON_PAGE:
                self.page = len(datas) // ELEMENTS_ON_PAGE
            for i, data in enumerate(datas):
                # Check for not displaying items with cost -1
                if data[2] != -1 and i >= self.page * ELEMENTS_ON_PAGE and i < (self.page + 1) * ELEMENTS_ON_PAGE:
                    rank = i + 1 - self.page * ELEMENTS_ON_PAGE
                    if selected == data[0]:
                        message += "*__"
                    message += f"{rank}: {data[0]} **[{data[3]}]**: {data[2]} credits"
                    if data[0] in inventory:
                        # Print amount of checkmarks in case of item
                        if type == "items":
                            for _ in range(player_data_dict[data[0]]):
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
        embed = discord.Embed(title=title, description=message, color=self.color)
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
        self.list = ["credit", "xp", "current streak", "highest streak", "games played", "games won", "average guesses"]
        for index, type in enumerate(self.list):
            if self.type == type:
                self.index = index
        self.color = access_database.get_user_color(self.client, self.id)

    @discord.ui.button(label="<", style=discord.ButtonStyle.red, custom_id="<")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show to UI for the current selected stats and show the previous stat option

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        self.index = (self.index - 1) % len(self.list)
        self.type = self.list[self.index]
        button.label = self.list[(self.index - 1) % len(self.list)].capitalize()
        next_button = [x for x in self.children if x.custom_id == ">"][0]
        next_button.label = self.list[(self.index + 1) % len(self.list)].capitalize()

        if self.view == "all":
            datas, title, currency = access_database.get_all_data(self.type)
        elif self.view == "month":
            datas, title, currency = access_database.get_month_data(self.type)
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

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
        datas, title, currency = access_database.get_all_data(self.type)
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
        datas, title, currency = access_database.get_month_data(self.type)
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.red, custom_id=">")
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

        previous_button = [x for x in self.children if x.custom_id == "<"][0]
        previous_button.label = self.list[(self.index - 1) % len(self.list)].capitalize()

        if self.view == "all":
            datas, title, currency = access_database.get_all_data(self.type)
        elif self.view == "month":
            datas, title, currency = access_database.get_month_data(self.type)
        embed = await self.make_embed(datas, title, currency)
        await interaction.response.edit_message(embed=embed, view=self)

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
        embed = discord.Embed(title=title, description=message, color=self.color)
        return embed


class UseFreezeStreak(discord.ui.View):
    def __init__(self, id: int, counter: int, db: sqlite3.Connection, cur: sqlite3.Cursor, client: discord.Client):
        """
        Initialize the UseFreezeStreak UI

        Parameters
        ----------
        id : int
            Id of the requested user
        counter : int
            Id of current WoordleGame
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
        self.counter = counter
        self.db = db
        self.cur = cur
        self.client = client
        try:
            datas = self.cur.execute("""
                                     SELECT amount FROM items_player
                                     WHERE name = "Freeze streak" AND id = ?
                                     """, (self.id,)).fetchall()
            if datas == []:
                self.amount_of_freeze = 0
            else:
                self.amount_of_freeze = datas[0][0]
        except Exception as e:
            print("Exception in UseFreezeStreak: ", e)
        self.buttons_disabled = False
        self.color = access_database.get_user_color(self.client, self.id)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Use a freezestreak

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        if not self.buttons_disabled:
            # descrease amount of freeze streaks
            try:
                self.cur.execute("""
                                 UPDATE items_player
                                 SET amount = amount - 1
                                 WHERE name = "Freeze streak" AND id = ?
                                 """, (self.id, ))
                self.db.commit()
                self.amount_of_freeze -= 1
            except Exception as e:
                print("Exception in lowering amount of freeze streaks: ", e)
            # Add fake freeze game with guesses field equal to FREEZE
            try:
                self.cur.execute("""
                                 INSERT INTO game (person, guesses, time, id, wordstring, wrong_guesses, credits_gained, xp_gained)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                 """, (self.id, "FREEZE", "99:99:99.999", self.counter - 1, "", 0, 0, 0))
                self.db.commit()
            except Exception as e:
                print("Exception in adding freeze game: ", e)

            if self.amount_of_freeze == 1:
                embed = discord.Embed(title="Freeze streak", description=f"Freeze streak has been used. {self.amount_of_freeze} freeze streak left.", color=self.color)
            else:
                embed = discord.Embed(title="Freeze streak", description=f"Freeze streak has been used. {self.amount_of_freeze} freeze streaks left.", color=self.color)
            await interaction.response.edit_message(embed=embed, view=self)
            self.buttons_disabled = True

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Do not use a freezestreak

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        if not self.buttons_disabled:
            if self.amount_of_freeze == 1:
                embed = discord.Embed(title="Freeze streak", description=f"Freeze streak has not been used. {self.amount_of_freeze} freeze streak left.", color=self.color)
            else:
                embed = discord.Embed(title="Freeze streak", description=f"Freeze streak has not been used. {self.amount_of_freeze} freeze streaks left.", color=self.color)
            await interaction.response.edit_message(embed=embed, view=self)
            self.buttons_disabled = True


class UseLossStreak(discord.ui.View):
    def __init__(self, id: int, counter: int, word: str,
                 db: sqlite3.Connection, cur: sqlite3.Cursor, client: discord.Client):
        """
        Initialize the UseFreezeStreak UI

        Parameters
        ----------
        id : int
            Id of the requested user
        counter : str
            Counter to be inserted
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
        self.counter = counter
        self.word = word
        self.db = db
        self.cur = cur
        self.client = client
        try:
            datas = self.cur.execute("""
                                     SELECT amount FROM items_player
                                     WHERE name = "Loss streak" AND id = ?
                                     """, (self.id,)).fetchall()
            if datas == []:
                self.amount_of_loss = 0
            else:
                self.amount_of_loss = datas[0][0]
        except Exception as e:
            print("Exception in UseLossStreak: ", e)
        self.buttons_disabled = False
        self.color = access_database.get_user_color(self.client, self.id)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Use a lossstreak

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        if not self.buttons_disabled:
            # descrease amount of freeze streaks
            try:
                self.cur.execute("""
                                 UPDATE items_player
                                 SET amount = amount - 1
                                 WHERE name = "Loss streak" AND id = ?
                                 """, (self.id, ))
                self.db.commit()
                self.amount_of_loss -= 1
            except Exception as e:
                print("Exception in lowering amount of loss streaks: ", e)
            # Change guess field to LOSS
            try:
                self.cur.execute("""
                                 UPDATE game
                                 SET guesses = "LOSS"
                                 WHERE person = ? and id = ?
                                 """, (self.id, self.counter))
                self.db.commit()
            except Exception as e:
                print("Exception in adding loss game: ", e)

            if self.amount_of_loss == 1:
                embed = discord.Embed(title=f"Better luck next time, the word was {self.word}!", description=f"Loss streak has been used. {self.amount_of_loss} loss streak left.")
            else:
                embed = discord.Embed(title=f"Better luck next time, the word was {self.word}!", description=f"Loss streak has been used. {self.amount_of_loss} loss streaks left.")
            await interaction.response.edit_message(embed=embed, view=self)
            self.buttons_disabled = True

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Do not use a lossstreak

        Parameters
        ----------
        interaction : discord.Interaction
            Used to handle button interaction
        button : discord.ui.Button
            Button object
        """
        if not self.buttons_disabled:
            if self.amount_of_loss == 1:
                embed = discord.Embed(title=f"Better luck next time, the word was {self.word}!",
                                      description=f"Loss streak has not been used. {self.amount_of_loss} loss streak left.", color=self.color)
            else:
                embed = discord.Embed(title=f"Better luck next time, the word was {self.word}!",
                                      description=f"Loss streak has not been used. {self.amount_of_loss} loss streaks left.", color=self.color)
            await interaction.response.edit_message(embed=embed, view=self)
            self.buttons_disabled = True


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Database(client))
