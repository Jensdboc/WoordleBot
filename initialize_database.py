import sqlite3
import random
from datetime import datetime


# Add word to woordle_game if not in the database already
def pick_word() -> str:
    """
    Pick a random word from "woorden.txt" for the next woordle game

    Returns
    -------
    word : str
        Word for the next WoordleGame
    """
    with open("data/woorden.txt", 'r') as all_words:
        words = all_words.read().splitlines()
        word = random.choice(words)
    return word


def get_db_and_cur() -> (sqlite3.Connection, sqlite3.Cursor):
    try:
        db = sqlite3.connect("woordle.db")
        cur = db.cursor()
        return db, cur
    except Exception as e:
        print(f"Exception in get_db_and_cur: {e}")


def create_database() -> None:
    """
    Create all the tables for woordle.db
    """
    db, cur = get_db_and_cur()
    # Create table for woordlegames if it does not exist
    # This contains the general information for a daily game
    # Date has to be unique
    try:
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
                        person integer,
                        guesses integer NOT NULL,
                        time timestamp NOT NULL,
                        id integer,
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
                        id integer,
                        credits integer NOT NULL,
                        xp integer NOT NULL,
                        current_streak integer NOT NULL,
                        highest_streak integer NOT NULL,
                        PRIMARY KEY (id)
                        )
                    """)

        # Create table for achievement if it does not exist
        # This contains the information about each achievement
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS achievements (
                        name text,
                        description text NOT NULL,
                        rarity text NOT NULL,
                        PRIMARY KEY (name)
                        )
                    """)

        # Create table for skins if it does not exist
        # This contains the information about each skin
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS skins (
                        name text,
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
                        name text,
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
                        name text,
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
                        name text,
                        id integer,
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
                        name text,
                        id integer,
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
                        name text,
                        id integer,
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
                        name text,
                        id integer,
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
        cur.close()
    except Exception as e:
        print(f"Exception in create_database: {e}")


def fill_database() -> None:
    """
    Fill woordle.db with achievements, skins, items, ...
    Rarities:
        - Common
        - Rare
        - Epic
        - Legendary
        - Unique
    """
    db, cur = get_db_and_cur()
    try:
        achievements = [
                            # Amount of games achievements
                            ["Beginner", "Play 1 Woordlegame", "common"],
                            ["Getting started", "Play 10 Woordlegames", "common"],
                            ["Getting there", "Play 50 Woordlegames", "common"],
                            ["Getting addicted?", "Play 100 Woordlegames", "common"],
                            ["Addicted", "Play 500 Woordlegames", "rare"],
                            ["Time to stop", "Play 1000 Woordlegames", "epic"],

                            # Monthly achievements
                            ["That's a start", "Get top 3 in a monthly ranking", "common"],
                            ["The best category", "Get first place in average guesses (monthly)", "epic"],
                            ["MVP", "Get first place in all the monthly rankings", "legendary"],
                            ["Starting a collection", "Collect 10 medals from monthly rankings", "legendary"],

                            # Special achievements
                            ["It's called skill", "Win a Woordle in 1 guess", "legendary"],
                            ["That was the last chance", "Win a Woordle in 6 guesses", "common"],
                            ["Whoops, my finger slipped", "Have over 100 wrong guesses in a single game", "epic"],
                            ["I don't like yellow", "Win a game with only green pieces but not in the first try", "epic"],
                            ["They said it couldn't be done", "Win a game where the only green pieces are in the answer", "legendary"],
                            ["Mr. Clean", "Win a game without making a wrong guess", "epic"],
                            ["Haaa, poor!", "Try to buy an item but do not have the required credits", "rare"],

                            # General stat achievements
                            ["Learning from mistakes", "Have 100 wrong guesses", "epic"],

                            # Timed achievements
                            ["Merry Christmas!", "Win a Woordle on Christmas", "rare"],
                            ["Jokes on you", "Play a game on the 1st of April", "rare"],
                            ["Early bird", "Complete a game before 8 o'clock", "rare"],
                            ["Definitely past your bedtime", "Complete a game after 11 pm", "epic"],
                            ["I'm fast as F boi", "Win a game under 10 seconds", "epic"],
                            ["Were you even playing?", "Spend more than 1 hour on a game", "rare"],
                            ["That was on purpose", "Spend more than 10 hours on a game", "legendary"],

                            # Shop achievements
                            ["Thank you, come again", "Spend your first credits", "common"],
                            ["Look how fancy", "Buy a skin", "common"],
                            ["Cold as ice", "Buy max freeze streaks", "rare"],

                            # Credit achievements
                            ["Time to spend", "Get 500 credits", "rare"],
                            ["What are you saving them for?", "Get 10,000 credits", "epic"]
                        ]

        for achievement in achievements:
            cur.execute("""
                        INSERT OR IGNORE INTO achievements (name, description, rarity)
                        VALUES (?, ?, ?)
                        """, achievement)

        skins = [
                    # Basic skins
                    ["Default", "Green and Yellow", "0", "common"],
                    ["Chess", "Black and white", "250", "common"],
                    ["Colorblind", "Blue and orange", "250", "common"],

                    # Emoji skins
                    ["Hearts", "Heartshaped", "250", "common"],
                    ["I like balls", "Circles", "250", "common"],
                    ["Moooons", "Moons with smiles", "250", "common"],
                    ["Fruit", "Lemon and green apple", "250", "common"],
                    ["Fruit 2.0", "Banana and pear", "250", "common"],
                    ["Fruit (tropical edition)", "Pineapple and avocado", "500", "common"],

                    # Themed skins
                    ["Santa", "Trees, gift, santa", "500", "rare"],
                    ["Spooky", "Jack 'o lantern, ghost", "500", "rare"],
                    ["Summer Time", "Sun, palmtree", "500", "rare"],
                    ["Dipping time", "Cookie, milk", "750", "epic"],

                    # Special skins
                    ["Random", "Random letters", "750", "epic"]
                ]

        for skin in skins:
            cur.execute("""
                        INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                        VALUES (?, ?, ?, ?)
                        """, skin)

        items = [
                    # Streak items
                    ["Freeze streak", "Keep your streak when missing a day", "250", "rare", "2"],
                    ["Loss streak", "Keep your streak when losing a game", "150", "common", "2"]
                ]

        for item in items:
            cur.execute("""
                        INSERT OR IGNORE INTO items (name, description, cost, rarity, max)
                        VALUES (?, ?, ?, ?, ?)
                        """, item)

        colors = [
                    # Default colors
                    ["Black", "Black", "0", "common"],
                    ["Red", "Red", "150", "common"],
                    ["Green", "Green", "150", "common"],
                    ["Yellow", "Yellow", "150", "common"],
                    ["Orange", "Orange", "150", "common"],
                    ["Blue", "Blue", "150", "common"],
                    ["Purple", "Purple", "150", "common"],
                    ["Pink", "Pink", "150", "common"],
                    ["White", "White", "150", "common"],

                    # Special colors
                    ["Your color", "Your color", "250", "rare"],
                    ["Random", "Random", "1000", "legendary"]
                 ]

        for color in colors:
            cur.execute("""
                        INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                        VALUES (?, ?, ?, ?)
                        """, color)

        # Make sure transaction is ended and changes have been made final
        db.commit()
        cur.close()
    except Exception as e:
        print(f"Exception in fill_database: {e}")


def set_word_of_today() -> None:
    """
    Create new woordle game if it does not exist already
    If there is a game for the current date already, ignore the new word
    """
    db, cur = get_db_and_cur()
    try:
        cur.execute("""
                    INSERT OR IGNORE INTO woordle_games (date, number_of_people, word)
                    VALUES (?,?,?)
                    """, [datetime.now().strftime("%F"), 0, pick_word()])

        # Make sure transaction is ended and changes have been made final
        db.commit()
        cur.close()
    except Exception as e:
        print(f"Exception in set_word_of_today: {e}")
