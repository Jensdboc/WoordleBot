import discord
from discord.ext import commands

from admincheck import admin_check

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
        with open("data/channels.txt", "r") as file:
            lines = file.readlines()
            channel_ids = [int(line.rstrip()) for line in lines]

        for ch_id in channel_ids:
            try:
                channel = self.client.get_channel(ch_id)
                embed = discord.Embed(title="Woordle announcement", description=message, color=ctx.author.color)
                await channel.send(embed=embed)
            except Exception:
                embed = discord.Embed(title="Woordle announcement", description=f"Channel with {ch_id} not found!", color=ctx.author.color)
                await ctx.send(embed=embed)

    @commands.command(usage="=addchannel <channel_id>",
                      description="Add a channel to the channels that broadcast WoordleGames")
    @commands.check(admin_check)
    async def addchannel(self, ctx: commands.Context, ch_id: int) -> None:
        with open("data/channels.txt", "a+") as file:
            file.write(str(ch_id) + "\n")
        embed = discord.Embed(title="Woordle", description="The channel has been added successfully!", color=ctx.author.color)
        await ctx.send(embed=embed)


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
