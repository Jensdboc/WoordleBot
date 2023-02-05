import discord
import sqlite3
import collections 

from discord.ext import commands

#**********************#
#Database test commands#
#**********************#

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
    async def stats(self, ctx, member : discord.Member):
        def convert_str_to_time(str):
            str_split = str.split(":")
            return float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

        def longest_streak(ids):
            sorted(ids)
            streaks = []
            start_id = ids[0]
            streak = 1
            streaks = []
            for id in ids[1:]:
                if id == start_id + 1:
                    streak += 1
                else:
                    streaks.append(streak)
                    streak = 1
                start_id = id
            streaks.append(streak)
            return max(streaks)

        if member is None:
            embed = discord.Embed(title="Woordle stats", description="You have to provide a member!", color=ctx.author.color)             
            await ctx.send(embed = embed)
            return 
        self.cur.execute('''
            SELECT * from game WHERE person = ?
        ''', (member.id,))
        datas = self.cur.fetchall()
        game_count = len(datas)
        if game_count == 0:
            embed = discord.Embed(title="Woordle stats from "+member.display_name, description="This user hasn't played any games so far!", color=ctx.author.color)             
            await ctx.send(embed = embed)
            return
        guess_count = 0
        total_time = 0
        all_words = ""
        wrong_guess_count = 0
        fastest_time = None
        ids = []
        for data in datas:
            guess_count += data[1]
            game_time = convert_str_to_time(data[2])
            total_time += game_time
            if fastest_time == None:
                fastest_time = total_time
            elif fastest_time > game_time:
                fastest_time = game_time
            ids.append(data[3])
            all_words += data[4]
            wrong_guess_count += data[5]
        
        message = "Total games: " + str(game_count) + "\n"
        message += "Average number of guesses: " + str(round(guess_count/game_count,3)) + "\n"
        message += "Average time of guesses: " + str(round(total_time/game_count,3)) + " seconds\n"
        message += "Highest streak: " + str(longest_streak(ids)) + "\n"
        message += "Fastest time: " + str(fastest_time) + " seconds \n"
        message += "Total wrong guesses: " + str(wrong_guess_count) + "\n"
        message += "Favourite letter: " + str(collections.Counter(all_words).most_common(1)[0][0]) + "\n"
        embed = discord.Embed(title="Woordle stats "+member.display_name, description=message, color=ctx.author.color)             
        await ctx.send(embed = embed)


#Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Database(client))
