from pathlib import Path
from datetime import datetime

import asyncio
import discord
import numpy as np # Extra for othello
import os # Import for cogs
import random # Import for choosing word

from discord.ext import commands
from pydoc import cli

# Database
import sqlite3

# Import for files
from Help import CustomHelpCommand
from admincheck import admin_check

# Intents
intents = discord.Intents.all()

#*******#
#Startup#
#*******#

client = commands.Bot(command_prefix="=", help_command=CustomHelpCommand(), case_insensitive=True, intents=intents)
client.mute_message = None
client.activity = discord.Game(name="=help")

# Database test: https://www.youtube.com/watch?v=H09U2E2v8eg&t=35s&ab_channel=DevXplaining
# Connect to db and make cursor
db = sqlite3.connect("woordle.db")
cur = db.cursor()

# Create table for woordlegames if it does not exist
cur.execute('''
CREATE TABLE IF NOT EXISTS woordle_games (
    id integer PRIMARY KEY AUTOINCREMENT,
    date text NOT NULL, 
    number_of_people integer NOT NULL,
    word text NOT NULL
    )
''')

# Create table for a game if it does not exist
cur.execute('''
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
''')

#ADD WORD TO WOORDLE_GAME
def pick_word():
    with open("woorden.txt", 'r') as all_words:
        words = all_words.read().splitlines()
        word = random.choice(words)
    print("The word has been changed to "+word)
    return word

# Create new woordle game-entry with current date and number of people equal to 0 and a new word
cur.execute('''
INSERT INTO woordle_games (date, number_of_people, word) 
    VALUES (?,?,?)
''',[datetime.now().strftime("%D"), 0, pick_word()])

# Make sure transaction is ended and changes have been made final
db.commit()

@client.event
async def on_ready():
    print('Bot = ready')

# Create file if it doesn't exist
def file_exist(name):
    file = Path(name)
    file.touch(exist_ok=True)

#*************#
#Cogs commands#
#*************#

#Loads extension
@client.command(admin_check)
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')

#Unloads extension
@client.command(admin_check)
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')

#Reloads extension
@client.command(admin_check)
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')

#Loads every extensions in cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    with open('token.txt', 'r') as file:
        token = file.readline()
        print("Reading token...")
    await load_extensions()
    await client.start(token)

asyncio.run(main())