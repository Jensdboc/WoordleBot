import sqlite3
import random
from datetime import datetime
from typing import Tuple

from constants import DATABASE, ACHIEVEMENTS, SKINS, ITEMS, COLORS, ROLES


# Add word to woordle_game if not in the database already
def pick_word() -> str:
    """
    Pick a random word from "woorden.txt" for the next woordle game

    Returns
    -------
    word : str
        Word for the next WoordleGame
    """
    if datetime.now().month == 8 and datetime.now().day == 7:
        word = "SHREK"
    else:
        with open("data/woorden.txt", 'r') as all_words:
            words = all_words.read().splitlines()
            word = random.choice(words)
    return word


def get_db_and_cur() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    try:
        db = sqlite3.connect(DATABASE)
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
                        id integer PRIMARY KEY,
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
                        name text NOT NULL,
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

        # Create table for roles if it does not exist
        # This contains the information about each role
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        name text,
                        description text NOT NULL,
                        cost integer NOT NULL,
                        rarity text NOT NULL,
                        color text NOT NULL,
                        role_id integer NOT NULL,
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

        # Create table for roles_player if it does not exist
        # This links information between roles and players
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS roles_player (
                        name text,
                        id integer,
                        selected bool NOT NULL,
                        PRIMARY KEY (name, id),
                        FOREIGN KEY (id)
                            REFERENCES player (id)
                        FOREIGN KEY (name)
                            REFERENCES roles (name)
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
        for achievement in ACHIEVEMENTS:
            cur.execute("""
                        INSERT OR IGNORE INTO achievements (name, description, rarity)
                        VALUES (?, ?, ?)
                        """, achievement)

        for skin in SKINS:
            cur.execute("""
                        INSERT OR IGNORE INTO skins (name, description, cost, rarity)
                        VALUES (?, ?, ?, ?)
                        """, skin)

        for item in ITEMS:
            cur.execute("""
                        INSERT OR IGNORE INTO items (name, description, cost, rarity, max)
                        VALUES (?, ?, ?, ?, ?)
                        """, item)

        for color in COLORS:
            cur.execute("""
                        INSERT OR IGNORE INTO colors (name, description, cost, rarity)
                        VALUES (?, ?, ?, ?)
                        """, color)

        for role in ROLES:
            cur.execute("""
                        INSERT OR IGNORE INTO roles (name, description, cost, rarity, color, role_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, role)

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
