import discord
from discord.ext import commands

from boggle_game import BoggleGame
from boggle_games import BoggleGames
from constants import BOGGLE_STATE


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

    @commands.command(aliases=["cb"])
    async def createboggle(self, ctx: commands.Context):
        self.games.remove_old_games()
        view = BoggleWaitingRoom(ctx, self.client, self.games)
        await ctx.reply(view=view)

    @commands.command(aliases=["sb"])
    async def startboggle(self, ctx: commands.Context, game_id: int = 0):
        results = await self.games.get_game(game_id).start()

        channel_embed_description = ""
        sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)
        for player, result in sorted_results:
            channel_embed_description += f"{player.name}: {result}\n"
        channel_embed = discord.Embed(title="Boggle Results", description=channel_embed_description)
        await ctx.send(embed=channel_embed)

    @commands.command(aliases=["b"])
    async def boggle(self, ctx: commands.Context, guess: str):
        if ctx.channel.type == discord.ChannelType.private:
            for game in self.games.games:
                if game.state == BOGGLE_STATE[1] and ctx.author.id in [player.id for player in game.players]:
                    game.add_guess(ctx.author, guess)


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
