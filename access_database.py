import discord
import sqlite3

from datetime import datetime, timedelta
from woordle_game import WoordleGame


def get_db_and_cur() -> (sqlite3.Connection, sqlite3.Cursor):
    db = sqlite3.connect("woordle.db")
    cur = db.cursor()
    return db, cur


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
            embed = discord.Embed(title=f"{user.global_name} unlocked: ***{name}***", description=description)
            with open("data/channels.txt", "r") as file:
                lines = file.readlines()
                for id in [int(line[:-1]) for line in lines]:
                    channel = client.get_channel(id)
                    await channel.send(embed=embed)
        cur.close()
    except Exception as e:
        print("Exception in add_achievement: ", e)


async def check_achievements_after_game(client: discord.Client, id: int, woordlegame: WoordleGame):
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
    if woordlegame.row == 6:
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
