# Imports 
from pydoc import cli
import discord
from discord.ext import commands, tasks 
import numpy as np # Extra for othello   
import os # Import for cogs

# Create files
from pathlib import Path

# Import from files
from Help import CustomHelpCommand

# Intents
intents = discord.Intents.all()

#*******#
#Startup#
#*******#

client = commands.Bot(command_prefix="!", help_command=CustomHelpCommand(), case_insensitive=True, intents=intents)
client.mute_message = None
client.activity = discord.Game(name="Woordle")

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