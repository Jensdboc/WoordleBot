import asyncio
import discord
import os
import sqlite3
import random
from datetime import datetime
from discord.ext import commands

from help import CustomHelpCommand

# Initialize client
intents = discord.Intents.all()
client = commands.Bot(command_prefix="=", help_command=CustomHelpCommand(),
                      case_insensitive=True, intents=intents)
client.mute_message = None
client.activity = discord.Game(name="=help")

# Connect to db and make cursor
db = sqlite3.connect("woordle.db")
cur = db.cursor()

# Create table for woordlegames if it does not exist
# This contains the general information for a daily game
# Date has to be unique
cur.execute("""
            CREATE TABLE IF NOT EXISTS woordle_games (
                id integer PRIMARY KEY AUTOINCREMENT,
                date text UNIQUE NOT NULL,
                number_of_people integer NOT NULL,
                word text NOT NULL
                )
            """)

# Create table for a game if it does not exist
# This contains the information per person for each game
cur.execute("""
            CREATE TABLE IF NOT EXISTS game (
                person integer NOT NULL,
                guesses integer NOT NULL,
                time timestamp NOT NULL,
                id integer NOT NULL,
                wordstring NOT NULL,
                wrong_guesses NOT NULL,
                PRIMARY KEY (person, id),
                FOREIGN KEY (id)
                    REFERENCES woordle_games (id)
                )
            """)

# Create table for a player if it does not exist
# This contains the information about each player
cur.execute("""
            CREATE TABLE IF NOT EXISTS player (
                id integer NOT NULL,
                credits integer NOT NULL,
                xp integer NOT NULL,
                PRIMARY KEY (id)
                )
            """)

# Make sure transaction is ended and changes have been made final
db.commit()


# Add word to woordle_game if not in the database already
def pick_word() -> str:
    """
    Pick a random word from "woorden.txt" for the next woordle game

    Returns
    -------
    word : str
        Word for the next WoordleGame
    """
    with open("woorden.txt", 'r') as all_words:
        words = all_words.read().splitlines()
        word = random.choice(words)
    return word


# Create new woordle game if it does not exist already
# If there is a game for the current date already, ignore the new word
cur.execute("""
            INSERT OR IGNORE INTO woordle_games (date, number_of_people, word)
            VALUES (?,?,?)
            """, [datetime.now().strftime("%D"), 0, pick_word()])

# Make sure transaction is ended and changes have been made final
db.commit()

# # Loads extension
# @client.command()
# @commands.check(admin_check)
# async def load(ctx, extension):
#     await client.load_extension(f'cogs.{extension}')
#     await ctx.send("Succesfully loaded `" + extension + '`')


# # Unloads extension
# @client.command()
# @commands.check(admin_check)
# async def unload(ctx, extension):
#     await client.unload_extension(f'cogs.{extension}')
#     await ctx.send("Succesfully unloaded `" + extension + '`')


# # Reloads extension
# @client.command()
# @commands.check(admin_check)
# async def reload(ctx, extension):
#     await client.unload_extension(f'cogs.{extension}')
#     await client.load_extension(f'cogs.{extension}')
#     await ctx.send("Succesfully reloaded `" + extension + '`')


# Loads every extensions in cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


async def main():
    with open('token_test.txt', 'r') as file:
        token = file.readline()
        print("Reading token...")
    await load_extensions()
    await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())
