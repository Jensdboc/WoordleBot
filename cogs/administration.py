import discord
import asyncio

from discord.ext import commands, tasks

class Administration(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(usage="=announce <message>", 
                      description="Announce a message to the subscribed channels")
    async def announce(self, ctx, *, message):
        if ctx.author.id == 656916865364525067:
            channel_ids = [878308113604812880, 1039877136179277864, 1054342112474316810]
            for id in channel_ids:
                channel = self.client.get_channel(id)
                embed = discord.Embed(title="Woordle announcement", description=message, color=ctx.author.color)        
                await channel.send(embed=embed)

#Allows to connect cog to bot
async def setup(client):
    await client.add_cog(Administration(client))
