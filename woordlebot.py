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
client.activity = discord.Game(name="Join https://discord.gg/wD6TYZFk")

# Connect to db and make cursor
db = sqlite3.connect("woordle.db")
cur = db.cursor()


def create_database():
    """
    Create all the tables for woordle.db
    """
    # Create table for woordlegames if it does not exist
    # This contains the general information for a daily game
    # Date has to be unique
    cur.execute("""
                CREATE TABLE IF NOT EXISTS woordle_games (
                    id integer PRIMARY KEY AUTOINCREMENT,
                    date date UNIQUE NOT NULL,
                    number_of_people integer NOT NULL,
                    word text NOT NULL
                    )
                """)

    # Create table for games if it does not exist
    # This contains the information per person for each game
    cur.execute("""
                CREATE TABLE IF NOT EXISTS game (
                    person integer NOT NULL,
                    guesses integer NOT NULL,
                    time timestamp NOT NULL,
                    id integer NOT NULL,
                    wordstring text NOT NULL,
                    wrong_guesses integer NOT NULL,
                    credits_gained integer NOT NULL,
                    xp_gained integer NOT NULL,
                    PRIMARY KEY (person, id),
                    FOREIGN KEY (id)
                        REFERENCES woordle_games (id)
                    )
                """)

    # Create table for players if it does not exist
    # This contains the information about each player
    cur.execute("""
                CREATE TABLE IF NOT EXISTS player (
                    id integer NOT NULL,
                    credits integer NOT NULL,
                    xp integer NOT NULL,
                    current_streak integer NOT NULL,
                    PRIMARY KEY (id)
                    )
                """)

    # Create table for achievement if it does not exist
    # This contains the information about each achievement
    cur.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    name text NOT NULL,
                    description text NOT NULL,
                    rarity text NOT NULL,
                    PRIMARY KEY (name)
                    )
                """)

    # Create table for skins if it does not exist
    # This contains the information about each skin
    cur.execute("""
                CREATE TABLE IF NOT EXISTS skins (
                    name text NOT NULL,
                    description text NOT NULL,
                    cost integer NOT NULL,
                    rarity text NOT NULL,
                    PRIMARY KEY (name)
                    )
                """)

    # Create table for items if it does not exist
    # This contains the information about each item
    cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    name text NOT NULL,
                    description text NOT NULL,
                    cost integer NOT NULL,
                    rarity text NOT NULL,
                    max integer NOT NULL,
                    PRIMARY KEY (name)
                    )
                """)

    # Create table for colors if it does not exist
    # This contains the information about each color
    cur.execute("""
                CREATE TABLE IF NOT EXISTS colors (
                    name text NOT NULL,
                    description text NOT NULL,
                    cost integer NOT NULL,
                    rarity text NOT NULL,
                    PRIMARY KEY (name)
                    )
                """)

    # Create table for achievements_player if it does not exist
    # This links information between achievements and players
    cur.execute("""
                CREATE TABLE IF NOT EXISTS achievements_player (
                    name text NOT NULL,
                    id integer NOT NULL,
                    PRIMARY KEY (name, id),
                    FOREIGN KEY (id)
                        REFERENCES player (id)
                    FOREIGN KEY (name)
                        REFERENCES achievements (name)
                    )
                """)

    # Create table for skins_player if it does not exist
    # This links information between skins and players
    cur.execute("""
                CREATE TABLE IF NOT EXISTS skins_player (
                    name text NOT NULL,
                    id integer NOT NULL,
                    selected bool NOT NULL,
                    PRIMARY KEY (name, id),
                    FOREIGN KEY (id)
                        REFERENCES player (id)
                    FOREIGN KEY (name)
                        REFERENCES skins (name)
                    )
                """)

    # Create table for items_player if it does not exist
    # This links information between items and players
    cur.execute("""
                CREATE TABLE IF NOT EXISTS items_player (
                    name text NOT NULL,
                    id integer NOT NULL,
                    amount integer NOT NULL,
                    PRIMARY KEY (name, id),
                    FOREIGN KEY (id)
                        REFERENCES player (id)
                    FOREIGN KEY (name)
                        REFERENCES items (name)
                    )
                """)

    # Create table for colors_player if it does not exist
    # This links information between colors and players
    cur.execute("""
                CREATE TABLE IF NOT EXISTS colors_player (
                    name text NOT NULL,
                    id integer NOT NULL,
                    selected bool NOT NULL,
                    PRIMARY KEY (name, id),
                    FOREIGN KEY (id)
                        REFERENCES player (id)
                    FOREIGN KEY (name)
                        REFERENCES colors (name)
                    )
                """)

    # Make sure transaction is ended and changes have been made final
    db.commit()


def fill_database():
    """
    Fill woordle.db with achievements, skins, items, ...
    """

    # Rarities:
    #   - Common
    #   - Rare
    #   - Epic
    #   - Legendary
    #   - Unique

    # Amount of games achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Beginner", "Play 1 Woordlegame", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Getting started", "Play 10 Woordlegames", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Getting there", "Play 50 Woordlegames", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Getting addicted?", "Play 100 Woordlegames", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Addicted", "Play 500 Woordlegames", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Time to stop", "Play 1000 Woordlegames", "epic"))

    # Monthly achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("That's a start", "Get top 3 in a monthly ranking", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("The best category", "Get first place in average guesses (monthly)", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("MVP", "Get first place in all the monthly rankings", "legendary"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Starting a collection", "Collect 10 medals from monthly rankings", "legendary"))

    # Special achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("It's called skill", "Win a Woordle in 1 guess", "legendary"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("That was the last chance", "Win a Woordle in 6 guesses", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Whoops, my finger slipped", "Have over 100 wrong guesses in a single game", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("I don't like yellow", "Win a game with only green pieces", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("They said it couldn't be done", "Win a game where the only green pieces are in the answer", "legendary"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Mr. Clean", "Win a game without making a wrong guess", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Haaa, poor!", "Try to buy an item but do not have the required credits", "rare"))

    # General stat achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Learning from mistakes", "Have 100 wrong guesses", "epic"))

    # Timed achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Merry Christmas!", "Win a Woordle on Christmas", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Jokes on you", "Play a game on the 1st of april", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Early bird", "Complete a game before 8 o'clock", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Definitely past your bedtime", "Complete a game after 11pm", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("I'm fast as F boi", "Win a game under 10 seconds", "epic"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Were you even playing?", "Spend more than 1 hour on a game", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("That was on purpose", "Spend more than 10 hours on a game", "legendary"))

    # Shop achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Thank you, come again", "Spend your first credits", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Look how fancy", "Buy a skin", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Cold as ice", "Buy max freeze streaks", "rare"))

    # Credit achievements
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("Time to spend", "Get 500 credits", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO achievements (name, description, rarity)
                VALUES (?, ?, ?)
                """, ("What are you saving them for?", "Get 10.000 credits", "epic"))

    # Basic skins
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Chess", "Black and white", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Colorblind", "Blue and orange", "250", "common"))

    # Emoji skins
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Hearts", "Heartshaped", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("I like balls", "Circles", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Moooons", "Moons with smiles", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Fruit", "Lemon and green apple", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Fruit 2.0", "Banana and pear", "250", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Fruit (tropical edition)", "Pineapple and avocado", "500", "common"))

    # Themed skins
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Santa", "Trees, gift, santa", "500", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Spooky", "Jack 'o lantern, ghost", "500", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Summer Time", "Sun, palmtree", "500", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Dipping time", "Cookie, milk", "750", "epic"))

    # Special skins
    cur.execute("""
                INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Random", "Random letters", "750", "epic"))

    # Items
    cur.execute("""
                INSERT OR IGNORE INTO items (name, description, cost, rarity, max)
                VALUES (?, ?, ?, ?, ?)
                """, ("Freeze streak", "Keep your streak when missing a day", "250", "common", "2"))

    # Colors
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Red", "Red", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Green", "Green", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Yellow", "Yellow", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Orange", "Orange", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Blue", "Blue", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Purple", "Purple", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Pink", "Pink", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("White", "White", "150", "common"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Your color", "Your color", "250", "rare"))
    cur.execute("""
                INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                VALUES (?, ?, ?, ?)
                """, ("Random", "Random", "250", "epic"))

    # Make sure transaction is ended and changes have been made final
    db.commit()


create_database()
fill_database()


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
            """, [datetime.now().strftime("%F"), 0, pick_word()])

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
