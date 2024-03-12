import discord
import sqlite3

from typing import Tuple, List
from datetime import datetime, timedelta
from woordle_game import WoordleGame
from constants import COLOR_MAP, CHANNEL_IDS, DATABASE


def debug(message):
    with open("prints.txt", "a") as out:
        out.write(message + "\n")


def get_db_and_cur() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    return db, cur


def get_credits(id: int) -> int:
    db, cur = get_db_and_cur()
    try:
        datas = cur.execute("""
                            SELECT credits FROM player
                            WHERE id = ?
                            """, (id,)).fetchall()
        cur.close()
        if datas == []:
            amount = 0
        else:
            amount = datas[0][0]
        return amount
    except Exception as e:
        print("Exception in get_credits: ", e)
    return 0


def get_amount_of_games(id: int) -> int:
    db, cur = get_db_and_cur()
    try:
        datas = cur.execute("""
                            SELECT COUNT(*) FROM game
                            WHERE person = ?
                            """, (id,)).fetchall()
        cur.close()
        if datas == []:
            amount = 0
        else:
            amount = datas[0][0]
        return amount
    except Exception as e:
        print("Exception in get_amount_of_games: ", e)
    return 0


def get_current_streak(id: int, monthly: bool = False) -> int:
    db, cur = get_db_and_cur()
    try:
        # Check if game was not lost
        # FREEZE and LOSS is fine
        current_game_id = cur.execute("""
                                      SELECT MAX(id) from woordle_games
                                      """).fetchall()[0][0]
        if monthly:
            games_data = cur.execute("""
                                     SELECT * from game
                                     WHERE person = ? AND guesses != "X"
                                     AND game.id IN (
                                        SELECT woordle_games.id FROM woordle_games
                                        WHERE strftime("%m", woordle_games.date) = ?
                                            AND strftime("%Y", woordle_games.date) = ?
                                        )
                                     """, (id, datetime.now().strftime("%m"), datetime.now().strftime("%Y"))).fetchall()
        else:
            games_data = cur.execute("""
                                     SELECT * from game
                                     WHERE person = ? AND guesses != "X"
                                     """, (id,)).fetchall()
        ids_games = sorted([game_data[3] for game_data in games_data], reverse=True)
        if len(ids_games) == 0:
            return 0

        current_streak = 0
        for id in ids_games:
            if id == current_game_id - current_streak:
                current_streak += 1
            else:
                break
        return current_streak
    except Exception as e:
        print("Exception in get_current_streak: ", e)


def get_max_streak(id: int, monthly: bool = False) -> int:
    db, cur = get_db_and_cur()
    try:
        # Check if game was not lost
        # FREEZE and LOSS is fine
        if monthly:
            games_data = cur.execute("""
                                     SELECT * from game
                                     WHERE person = ? AND guesses != "X"
                                     AND game.id IN (
                                        SELECT woordle_games.id FROM woordle_games
                                        WHERE strftime("%m", woordle_games.date) = ?
                                            AND strftime("%Y", woordle_games.date) = ?
                                        )
                                     """, (id, datetime.now().strftime("%m"), datetime.now().strftime("%Y"))).fetchall()
        else:
            games_data = cur.execute("""
                                     SELECT * from game
                                     WHERE person = ? AND guesses != "X"
                                     """, (id,)).fetchall()
        ids_games = sorted([game_data[3] for game_data in games_data], reverse=True)
        if len(ids_games) == 0:
            return 0

        current_id = ids_games[0]
        current_streak = 0
        highest_streak = 0
        for id in ids_games:
            if id == current_id - current_streak:
                current_streak += 1
            else:
                if current_streak > highest_streak:
                    highest_streak = current_streak
                current_streak = 1
                current_id = id
        if current_streak > highest_streak:
            highest_streak = current_streak
        return highest_streak
    except Exception as e:
        print("Exception in get_current_streak: ", e)


def get_amount_of_credits(id: int) -> int:
    db, cur = get_db_and_cur()
    try:
        cur.execute("""
                    SELECT credits FROM player
                    WHERE id = ?
                    """, (id,))
        datas = cur.fetchall()
        cur.close()
        if datas == []:
            credits = 0
        else:
            credits = datas[0][0]
        return credits
    except Exception as e:
        print("Exception in get_amount_of_credits: ", e)


def get_amount_of_wrong_guesses(id: int) -> int:
    try:
        db, cur = get_db_and_cur()
        datas = cur.execute("""
                            SELECT SUM(wrong_guesses) FROM game
                            WHERE person = ?
                            """, (id,)).fetchall()
        cur.close()
        if datas == []:
            amount = 0
        else:
            amount = datas[0][0]
        return amount
    except Exception as e:
        print("Exception in get_amount_of_wrong_guesses:", e)


def get_game_from_today(id: int) -> list:
    db, cur = get_db_and_cur()
    try:
        game = cur.execute("""
                           SELECT * FROM game
                           WHERE person = ? and id = (
                               SELECT MAX(id) FROM game
                               WHERE person = ?
                           );
                           """, (id, id)).fetchall()[0]
        cur.close()
        return game
    except Exception as e:
        print("Exception in get_game_from_today: ", e)


async def add_achievement(client: discord.Client, name: str, id: int) -> None:
    db, cur = get_db_and_cur()
    user = client.get_user(id)
    try:
        cur.execute("""
                    INSERT OR IGNORE INTO achievements_player (name, id)
                    VALUES(?, ?)
                    """, (name, id))
        db.commit()
        if cur.rowcount > 0:
            description = cur.execute("""
                                      SELECT description FROM achievements
                                      WHERE name = ?
                                      """, (name,)).fetchall()[0][0]
            embed = discord.Embed(title=f"{user.display_name} unlocked: ***{name}***", description=description)
            for ch_id in CHANNEL_IDS:
                channel = client.get_channel(ch_id)
                await channel.send(embed=embed)

        cur.close()
    except Exception as e:
        print("Exception in add_achievement: ", e)


async def add_medal(client: discord.Client, rank: int, id: int, medal_type: str) -> None:
    db, cur = get_db_and_cur()
    medal_dict = {0: "First place medals", 1: "Second place medals", 2: "Third place medals"}
    try:
        # Check if the combination of medal and player already exists
        cur.execute("""
                    SELECT * FROM items_player
                    WHERE name = ? AND id = ?
                    """, (medal_dict[rank], id))
        old_player_data = cur.fetchall()

        if old_player_data != []:
            cur.execute("""
                        UPDATE items_player
                        SET amount = amount + 1
                        WHERE name = ? AND id = ?
                        """, (medal_dict[rank], id))
        else:
            cur.execute("""
                        INSERT INTO items_player (name, id, amount)
                        VALUES (?, ?, ?)
                        """, (medal_dict[rank], id, 1))
        db.commit()

        await add_achievement(client, "That's a start", id)

        if rank == 0 and medal_type == "average guesses":
            await add_achievement(client, "The best category", id)

        amount_of_medals = 0
        for medal in medal_dict.values():
            cur.execute("""
                        SELECT amount from items_player
                        WHERE name = ? AND id = ?
                        """, (medal, id))
            datas = cur.fetchall()
            if datas != []:
                amount_of_medals += datas[0][0]
        if amount_of_medals >= 10:
            await add_achievement(client, "Starting a collection", id)

        cur.close()
    except Exception as e:
        print("Exception in add_medal: ", e)


async def get_medals(id: int) -> List[int]:
    db, cur = get_db_and_cur()
    medal_dict = {0: "First place medals", 1: "Second place medals", 2: "Third place medals"}
    medals = []
    try:
        for place in medal_dict.values():
            cur.execute("""
                        SELECT amount FROM items_player
                        WHERE name = ? AND id = ?
                        """, (place, id))
            datas = cur.fetchall()
            if datas != []:
                medals.append(datas[0][0])

        cur.close()
    except Exception as e:
        print("Exception in get_medal: ", e)
    return medals


async def check_achievements_after_game(client: discord.Client, id: int, woordlegame: WoordleGame) -> None:
    # Amount of games achievements
    amount_of_games = get_amount_of_games(id)

    if amount_of_games >= 1:
        await add_achievement(client, "Beginner", id)
    if amount_of_games >= 10:
        await add_achievement(client, "Getting started", id)
    if amount_of_games >= 50:
        await add_achievement(client, "Getting there", id)
    if amount_of_games >= 100:
        await add_achievement(client, "Getting addicted?", id)
    if amount_of_games >= 500:
        await add_achievement(client, "Addicted", id)
    if amount_of_games >= 1000:
        await add_achievement(client, "Time to stop", id)

    # TODO: Monthly achievements

    # Special achievements
    if woordlegame.row == 1:
        await add_achievement(client, "It's called skill", id)
    if woordlegame.row == 6 and not woordlegame.failed:
        await add_achievement(client, "That was the last chance", id)

    if woordlegame.wrong_guesses >= 100:
        await add_achievement(client, "Whoops, my finger slipped", id)

    words_in_game = [woordlegame.wordstring[i:i+5] for i in range(0, len(woordlegame.wordstring), 5)]
    yellow_count = 0
    green_count = 0
    for word in words_in_game:
        for index, letter in enumerate(word):
            if letter.upper() == woordlegame.word[index].upper():
                green_count += 1
            elif letter.upper() in woordlegame.word.upper():
                yellow_count += 1
    if not yellow_count and woordlegame.row > 1 and not woordlegame.failed:
        await add_achievement(client, "I don't like yellow", id)
    if green_count == 5 and not woordlegame.failed:
        await add_achievement(client, "They said it couldn't be done", id)

    if woordlegame.wrong_guesses == 0 and not woordlegame.failed:
        await add_achievement(client, "Mr. Clean", id)

    # General stat achievements
    amount_of_wrong_guesses = get_amount_of_wrong_guesses(id)
    if amount_of_wrong_guesses > 100:
        await add_achievement("Learning from mistakes", id)

    # Timed achievements
    if datetime.now().month == 12 and datetime.now().day == 25 and not woordlegame.failed:
        await add_achievement(client, "Merry Christmas!", id)
    elif datetime.now().month == 4 and datetime.now().day == 1:
        await add_achievement(client, "Jokes on you", id)
    if datetime.now().hour < 7:
        await add_achievement(client, "Early bird", id)
    elif datetime.now().hour >= 23:
        await add_achievement(client, "Definitely past your bedtime", id)
    if woordlegame.time < timedelta(seconds=10) and not woordlegame.failed:
        await add_achievement(client, "I'm fast as F boi", id)
    if woordlegame.time > timedelta(hours=1):
        await add_achievement("Were you even playing?", id)
    if woordlegame.time > timedelta(hours=10):
        await add_achievement(client, "That was on purpose", id)

    # Credit achievements
    amount_of_credits = get_amount_of_credits(id)

    if amount_of_credits > 500:
        await add_achievement(client, "Time to spend", id)
    if amount_of_credits > 10000:
        await add_achievement(client, "What are you saving them for?", id)


def get_user_color(client: discord.Client, id: int) -> int:
    db, cur = get_db_and_cur()
    # Set color of author
    datas = cur.execute("""
                        SELECT * FROM colors_player
                        WHERE id = ? AND selected = ?
                        """, (id, True)).fetchall()
    # First time the user has ever played a game
    if datas == []:
        cur.execute("""
                    INSERT OR IGNORE INTO colors_player (name, id, selected)
                    VALUES (?, ?, ?)
                    """, ("Black", id, True))
        db.commit()
        color = COLOR_MAP["Black"]
    else:
        # Handle special colors
        if datas[0][0] == "Your color":
            user = client.get_user(id)
            color = user.color
        elif datas[0][0] == "Random":
            color = discord.Colour.random()
        else:
            color = COLOR_MAP[datas[0][0]]
    return color


def get_user_skin(id: int) -> int:
    db, cur = get_db_and_cur()
    # Set color of author
    datas = cur.execute("""
                        SELECT * FROM skins_player
                        WHERE id = ? AND selected = ?
                        """, (id, True)).fetchall()
    # First time the user has ever played a game
    if datas == []:
        cur.execute("""
                    INSERT OR IGNORE INTO skins_player (name, id, selected)
                    VALUES (?, ?, ?)
                    """, ("Default", id, True))
        db.commit()
        skin = "Default"
    else:
        skin = datas[0][0]
    return skin


def get_all_data(type: str):
    """
    Get data for view all

    Parameters
    ----------
    type : str
        The type of ranking
    Returns
    -------
    datas : list
        Data containing the users information
    title : str
        Title of the embed
    currency : str
        Unit of the data
    """
    db, cur = get_db_and_cur()
    try:
        title = f"Top users (all time) in {type}"
        if type == "credit":
            cur.execute("""
                        SELECT id, credits FROM player
                        ORDER BY credits DESC
                        """)
            datas = cur.fetchall()
            currency = ["credit", "credits"]
        elif type == "xp":
            cur.execute("""
                        SELECT id, xp FROM player
                        ORDER BY xp DESC
                        """)
            datas = cur.fetchall()
            currency = ["xp", "xp"]
        elif type == "current streak":
            cur.execute("""
                        SELECT id, current_streak FROM player
                        ORDER BY current_streak DESC
                        """)
            datas = cur.fetchall()
            currency = ["day", "days"]
        elif type == "highest streak":
            cur.execute("""
                        SELECT id, highest_streak FROM player
                        ORDER BY highest_streak DESC
                        """)
            datas = cur.fetchall()
            currency = ["day", "days"]
        elif type == "games played":
            cur.execute("""
                        SELECT person, COUNT(*) FROM game
                        GROUP BY person
                        ORDER BY COUNT(*) DESC
                        """)
            datas = cur.fetchall()
            currency = ["game", "games"]
        elif type == "games won":
            cur.execute("""
                        SELECT person, COUNT(*) FROM game
                        WHERE guesses != "X"
                        GROUP BY person
                        ORDER BY COUNT(*) DESC
                        """)
            datas = cur.fetchall()
            currency = ["game", "games"]
        elif type == "average guesses":
            cur.execute("""
                        SELECT person, AVG(guesses) FROM game
                        GROUP BY person
                        ORDER BY AVG(guesses)
                        """)
            datas = cur.fetchall()
            currency = ["guess", "guesses"]
        return datas, title, currency
    except Exception as e:
        print(e)


def get_month_data(type: str):
    """
    Get data for view month
    Parameters
    ----------
    type : str
        The type of ranking
    Returns
    -------
    datas : list
        Data containing the users information
    title : str
        Title of the embed
    currency : str
        Unit of the data
    """
    db, cur = get_db_and_cur()
    try:
        title = f"Top users (monthly) in {type}"
        if type == "credit":
            cur.execute("""
                        SELECT game.person, SUM(game.credits_gained) FROM game
                        WHERE game.id IN (
                        SELECT woordle_games.id FROM woordle_games
                        WHERE strftime("%m", woordle_games.date) = ?
                            AND strftime("%Y", woordle_games.date) = ?
                        )
                        GROUP BY game.person
                        ORDER BY SUM(game.credits_gained) DESC
                        """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = cur.fetchall()
            currency = ["credit", "credits"]
        elif type == "xp":
            cur.execute("""
                        SELECT game.person, SUM(game.xp_gained) FROM game
                        WHERE game.id IN (
                        SELECT woordle_games.id FROM woordle_games
                        WHERE strftime("%m", woordle_games.date) = ?
                            AND strftime("%Y", woordle_games.date) = ?
                        )
                        GROUP BY game.person
                        ORDER BY SUM(game.xp_gained) DESC
                        """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = cur.fetchall()
            currency = ["xp", "xp"]
        elif type == "current streak":
            cur.execute("""
                        SELECT id, current_streak FROM player
                        ORDER BY current_streak DESC
                        """)
            datas = cur.fetchall()
            currency = ["day", "days"]
        elif type == "highest streak":
            cur.execute("""
                        SELECT id, highest_streak FROM player
                        ORDER BY highest_streak DESC
                        """)
            datas = cur.fetchall()
            currency = ["day", "days"]
        elif type == "games played":
            cur.execute("""
                        SELECT person, COUNT(*) FROM game
                        WHERE game.id IN (
                        SELECT woordle_games.id FROM woordle_games
                        WHERE strftime("%m", woordle_games.date) = ?
                            AND strftime("%Y", woordle_games.date) = ?
                        )
                        GROUP BY person
                        ORDER BY COUNT(*) DESC
                        """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = cur.fetchall()
            currency = ["game", "games"]
        elif type == "games won":
            cur.execute("""
                        SELECT person, COUNT(*) FROM game
                        WHERE guesses != "X" AND
                        game.id IN (
                        SELECT woordle_games.id FROM woordle_games
                        WHERE strftime("%m", woordle_games.date) = ?
                            AND strftime("%Y", woordle_games.date) = ?
                        )
                        GROUP BY person
                        ORDER BY COUNT(*) DESC
                        """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = cur.fetchall()
            currency = ["game", "games"]
        elif type == "average guesses":
            cur.execute("""
                        SELECT person, AVG(guesses) FROM game
                        WHERE guesses != "X" AND
                        game.id IN (
                        SELECT woordle_games.id FROM woordle_games
                        WHERE strftime("%m", woordle_games.date) = ?
                            AND strftime("%Y", woordle_games.date) = ?
                        )
                        GROUP BY person
                        ORDER BY AVG(guesses)
                        """, (datetime.now().strftime("%m"), datetime.now().strftime("%Y")))
            datas = cur.fetchall()
            currency = ["guess", "guesses"]
        return datas, title, currency
    except Exception as e:
        print(e)
