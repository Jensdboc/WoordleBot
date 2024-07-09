import discord
from discord.ext import commands

from boggle_game import BoggleGame
from boggle_games import BoggleGames
from constants import BOGGLE_STATE, COLOR_MAP, PREFIX


class Boggle(commands.Cog):
    """Class for Woordle commands"""

    def __init__(self, client: discord.Client) -> None:
        """
        Initialize the Boggle cog

        Parameters
        ----------
        client : discord.Client
            Discord Woordle bot
        """
        self.client = client
        self.games = BoggleGames()

    @commands.command(usage=f"{PREFIX}createboggle",
                      description="""
                                  Create a new boggle lobby.
                                  """,
                      aliases=["cb"])
    async def createboggle(self, ctx: commands.Context):
        """
        Create a new boggle lobby

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        try:
            view = BoggleWaitingRoom(ctx, self.client, self.games)
            await ctx.reply(view=view)
        except Exception as e:
            print(e)
            await ctx.send(e)

    @commands.command(usage=f"{PREFIX}startboggle <game_id>",
                      description="""
                                  Start the boggle game with game_id.
                                  """,
                      aliases=["sb"])
    async def startboggle(self, ctx: commands.Context, game_id: int = 0):
        """
        Start the boggle game with game_id

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        game_id : int
            The id of the game to start
        """
        game = self.games.get_game(game_id)

        if game is None:
            fail_embed = discord.Embed(title=f"No game with id {game_id} found!", description="Create a boggle game with =createboggle or =cb first.", color=COLOR_MAP["Red"])
            await ctx.reply(embed=fail_embed)
            return
        elif ctx.author != game.players[0]:
            fail_embed = discord.Embed(title="No permission!", description=f"You are not the creator of this game!\n{game.players[0].name} should start this game.", color=COLOR_MAP["Red"])
            await ctx.reply(embed=fail_embed)
            return
        elif game.state != BOGGLE_STATE[0]:
            fail_embed = discord.Embed(title="Cannot be started!", description=f"Game with id {game_id} is currently {game.state}!", color=COLOR_MAP["Red"])
            await ctx.reply(embed=fail_embed)
            return

        results = await game.start()
        channel_embed_description = ""
        sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        for player, result in sorted_results:
            channel_embed_description += f"{player.name}: {result}\n"
        channel_embed = discord.Embed(title="Boggle Results", description=channel_embed_description)
        self.games.remove_game(game)
        await ctx.send(embed=channel_embed)

    @commands.command(usage=f"{PREFIX}boggle <guess>",
                      description="""
                                  Play one guess in a BoggleGame.
                                  """,
                      aliases=["b"])
    async def boggle(self, ctx: commands.Context, guess: str):
        """
        Play one guess in a BoggleGame

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        guess : str
            The guess to play
        """
        if ctx.channel.type == discord.ChannelType.private:
            for game in self.games.games:
                if game.state == BOGGLE_STATE[1] and ctx.author.id in [player.id for player in game.players]:
                    valid = game.add_guess(ctx.author, guess)
                    if not valid:
                        await ctx.message.add_reaction("❌")
                    else:
                        await ctx.message.add_reaction("✅")


class BoggleWaitingRoom(discord.ui.View):
    def __init__(self, ctx: commands.Context, client: discord.Client, games: BoggleGames):
        super().__init__()
        self.client = client
        self.games = games
        if self.games.games == []:
            self.game_id = 0
        else:
            self.game_id = max([game.game_id for game in self.games.games]) + 1
        self.game = BoggleGame([ctx.author], self.client, self.game_id)
        self.games.add_game(self.game)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.game.players:
            self.game.players.append(interaction.user)
        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.game.players:
            self.game.players.remove(interaction.user)
        embed = await self.make_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def make_embed(self):
        names = "\n".join([str(player.name) for player in self.game.players])
        embed = discord.Embed(title=f"Boggle waiting room {self.game_id}", description=f"Current players:\n{names}")
        return embed


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Boggle(client))
