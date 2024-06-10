PREFIX = "="
SERVER_ID = 1161256907521146881
CHANNEL_IDS = [1161262990989991936]  # Real channel
# CHANNEL_IDS = [1216431080698150942]  # Test channel
DATABASE = "woordle.db"
# DATABASE = "server_woordle.db"

COLOR_MAP = {
    "Red": 0xFF0000,
    "Green": 0x00FF00,
    "Yellow": 0xFFFF00,
    "Orange": 0xFF8800,
    "Blue": 0x0000FF,
    "Purple": 0x800080,
    "Pink": 0xFFC0CB,
    "White": 0xFFFFFF,
    "Black": 0x000000
}

SKIN_MAP = {
    "Default": {"green": "🟩", "yellow": "🟨", "gray": "⬛"},
    "Chess": {"green": "🔳", "yellow": "🔲", "gray": "⬛"},
    "Colorblind": {"green": "🟧", "yellow": "🟦", "gray": "⬛"},
    "Hearts": {"green": "💚", "yellow": "💛", "gray": "🖤"},
    "I like balls": {"green": "🟢", "yellow": "🟡", "gray": "⚫"},
    "Moooons": {"green": "🌚", "yellow": "🌝", "gray": "🌕"},
    "Fruit": {"green": "🍏", "yellow": "🍋", "gray": "⬛"},
    "Fruit 2.0": {"green": "🍐", "yellow": "🍌", "gray": "⬛"},
    "Fruit (tropical edition)": {"green": "🍈", "yellow": "🍍", "gray": "⬛"},
    "Santa": {"green": "🌲", "yellow": "🎅", "gray": "🎁"},
    "Spooky": {"green": "🎃", "yellow": "👻", "gray": "⬛"},
    "Valentine": {"green": "❤️", "yellow": "💗", "gray": "🤍"},
    "Summer Time": {"green": "🌴", "yellow": "☀️", "gray": "⬛"},
    "Dipping time": {"green": "🥛", "yellow": "🍪", "gray": "⬛"},
    "Random": "Random"
}

LETTER_MAP = {"a": ":regional_indicator_a:", "b": ":regional_indicator_b:", "c": ":regional_indicator_c:",
              "d": ":regional_indicator_d:", "e": ":regional_indicator_e:", "f": ":regional_indicator_f:",
              "g": ":regional_indicator_g:", "h": ":regional_indicator_h:", "i": ":regional_indicator_i:",
              "j": ":regional_indicator_j:", "k": ":regional_indicator_k:", "l": ":regional_indicator_l:",
              "m": ":regional_indicator_m:", "n": ":regional_indicator_n:", "o": ":regional_indicator_o:",
              "p": ":regional_indicator_p:", "q": ":regional_indicator_q:", "r": ":regional_indicator_r:",
              "s": ":regional_indicator_s:", "t": ":regional_indicator_t:", "u": ":regional_indicator_u:",
              "v": ":regional_indicator_v:", "w": ":regional_indicator_w:", "x": ":regional_indicator_x:",
              "y": ":regional_indicator_y:", "z": ":regional_indicator_z:"}

ACHIEVEMENTS = [
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
                    ["Whoops, my finger slipped", "Have over 100 non existent guesses in a single game", "epic"],
                    ["I don't like yellow", "Win a game with only green pieces but not in the first try", "epic"],
                    ["They said it couldn't be done", "Win a game where the only green pieces are in the answer", "legendary"],
                    ["Mr. Clean", "Win a game without making a non existent guess", "epic"],
                    ["Haaa, poor!", "Try to buy an item but do not have the required credits", "rare"],

                    # General stat achievements
                    ["Learning from mistakes", "Have 100 non existent guesses", "epic"],

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

SKINS = [
            # Basic skins
            ["Default", "Green and Yellow", "0", "common"],
            ["Chess", "Black and white", "200", "common"],
            ["Colorblind", "Blue and orange", "200", "common"],

            # Emoji skins
            ["Hearts", "Heartshaped", "200", "common"],
            ["I like balls", "Circles", "200", "common"],
            ["Moooons", "Moons with smiles", "200", "common"],
            ["Fruit", "Lemon and green apple", "200", "common"],
            ["Fruit 2.0", "Banana and pear", "200", "common"],
            ["Fruit (tropical edition)", "Pineapple and avocado", "500", "rare"],

            # Themed skins
            ["Santa", "Trees, gift, santa", "500", "rare"],
            ["Spooky", "Jack 'o lantern, ghost", "500", "rare"],
            ["Valentine", "Red heart, pink heart, white heart", "500", "rare"],
            ["Summer Time", "Sun, palmtree", "500", "rare"],
            ["Dipping time", "Cookie, milk", "750", "epic"],

            # Special skins
            ["Random", "Random letters", "750", "epic"]
        ]

ITEMS = [
            # Streak items
            ["Freeze streak", "Keep your streak when missing a day", "250", "rare", "2"],
            ["Loss streak", "Keep your streak when losing a game", "150", "common", "2"],

            # Medal items
            ["First place medals", "Amount of first places in monthly competitions", "-1", "legendary", "-1"],
            ["Second place medals", "Amount of first places in monthly competitions", "-1", "epic", "-1"],
            ["Third place medals", "Amount of first places in monthly competitions", "-1", "rare", "-1"]
        ]

COLORS = [
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
            ["Your color", "Your color", "500", "rare"],
            ["Random", "Random", "1000", "legendary"]
        ]

ROLES = [
            ["Broke", "Broke", "150", "common", "Black", 1249644832465621043],
            ["Cheater", "Cheater", "500", "rare", "Red", 1249644997675057243],
            [" ", "Empty", "750", "epic", "Discord", 1249645491478859807],
            # ["Choose your role", "Choose your role", "1000", "legendary", "Own color", "0"]
        ]
