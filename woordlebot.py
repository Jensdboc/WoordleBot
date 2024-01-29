import asyncio
import discord
import os
from discord.ext import commands

from help import CustomHelpCommand
from initialize_database import create_database, fill_database, set_word_of_today

# Initialize client
intents = discord.Intents.all()
client = commands.Bot(command_prefix="=", help_command=CustomHelpCommand(),
                      case_insensitive=True, intents=intents)
client.mute_message = None
client.activity = discord.Game(name="Join https://discord.gg/wD6TYZFk")

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
    print("Initializing database...")
    create_database()
    fill_database()
    set_word_of_today()

    print("Reading token...")
    with open('data/token_test.txt', 'r') as file:
        token = file.readline()
    await load_extensions()
    await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())
