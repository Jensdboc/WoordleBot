import discord
from discord.ext import commands


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

    @commands.command(usage="=announce <message>",
                      description="Announce a message to the subscribed channels")
    async def announce(self, ctx: commands.Context, *, message: str):
        """
        Announce a message in the dedicated Woordle channels in different guilds

        Parameters
        ----------
        ctx: commands.Context
            Context the command is represented in
        message : str
            Message to announce
        """
        if ctx.author.id == 656916865364525067:
            channel_ids = [878308113604812880, 1039877136179277864, 1054342112474316810]
            for id in channel_ids:
                try:
                    channel = self.client.get_channel(id)
                    embed = discord.Embed(title="Woordle announcement", description=message, color=ctx.author.color)
                    await channel.send(embed=embed)
                except Exception:
                    print(f"Channel with {id} not found!")


# Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
