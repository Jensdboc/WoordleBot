import discord
import sqlite3
import collections

from discord.ext import commands


class Database(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.db = sqlite3.connect("woordle.db")
        self.cur = self.db.cursor()

    @commands.command()
    async def get_games(self, ctx):
        self.cur.execute('''
            SELECT * from woordle_games
        ''')
        print("Fetching")
        print(self.cur.fetchall())
        self.cur.close

    @commands.command()
    async def get_game(self, ctx):
        self.cur.execute('''
            SELECT * from game
        ''')
        print("Fetching")
        print(self.cur.fetchall())
        self.cur.close

    @commands.command()
    async def stats(self, ctx, member: discord.Member):
        def convert_str_to_time(str):
            str_split = str.split(":")
            return float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

        def game_won(id):
            self.cur.execute('''
                SELECT guesses from game
                WHERE id = ?
            ''', (id,))
            guess = self.cur.fetchall()[0][0]
            return guess != "failed"

        def longest_streak(ids):
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

        def longest_win_streak(ids):
            sorted(ids)
            streaks = []
            first = True
            streak = 0
            start_id = -1
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
        self.cur.execute('''
            SELECT * from game WHERE person = ?
        ''', (member.id,))
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
            guess_count += data[1] if data[1] != 'failed' else 6
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


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Database(client))
