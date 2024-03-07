import discord
from discord.ext import commands

from admincheck import admin_check
from constants import CHANNEL_IDS

OWNER_ID = 656916865364525067


class Administration(commands.Cog):
    """Class for general administration commands"""

    def __init__(self, client: discord.client) -> None:
        """
        Initialize the Administration cog

        Parameters
        ----------
        client : discord.Client
            Discord Woordle bot
        """
        self.client = client

    @commands.command()
    @commands.check(admin_check)
    async def admin(self, ctx: commands.Context) -> None:
        """
        Confirm if user is an admin

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        """
        await ctx.reply("Yup")

    @commands.command(usage="=announce <message>",
                      description="Announce a message to the subscribed channels")
    @commands.check(admin_check)
    async def announce(self, ctx: commands.Context, *, message: str) -> None:
        """
        Announce a message in the dedicated Woordle channels in different guilds

        Parameters
        ----------
        ctx : commands.Context
            Context the command is represented in
        message : str
            Message to announce
        """
        for ch_id in CHANNEL_IDS:
            try:
                channel = self.client.get_channel(ch_id)
                embed = discord.Embed(title="Woordle announcement", description=message, color=ctx.author.color)
                await channel.send(embed=embed)
            except Exception:
                embed = discord.Embed(title="Woordle announcement", description=f"Channel with {ch_id} not found!", color=ctx.author.color)
                await ctx.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
