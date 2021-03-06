# Imports 
from pydoc import cli
import sched
import discord
from discord.ext import commands, tasks 
import numpy as np # Extra for othello   
import os # Import for cogs

# Database
import sqlite3
from datetime import datetime

# Create files
from pathlib import Path

from sqlalchemy import DATE

# Import for files
from Help import CustomHelpCommand

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

# Create table for woordle game if it does not exist
cur.execute('''
CREATE TABLE IF NOT EXISTS woordle_game (
    id integer PRIMARY KEY AUTOINCREMENT,
    date text NOT NULL, 
    number_of_people text NOT NULL
    )
''')

#ADD WORD TO WOORDLE_GAME

# Create new woordle game-entry with current date and number of people equal to 0
cur.execute('''
INSERT INTO woordle_game (date, number_of_people) 
    VALUES (?,?)
''',[datetime.now().strftime("%D"), "0"])

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
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully loaded `" + extension + '`')

#Unloads extension
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send("Succesfully unloaded `" + extension + '`')

#Reloads extension
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send("Succesfully reloaded `" + extension + '`')

#Loads every extensions in cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

with open('token.txt', 'r') as file:
    token = file.readline()
    print("Reading token...")
    client.run(token)