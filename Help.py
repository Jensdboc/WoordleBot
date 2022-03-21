import discord
from discord.ext import commands
from sqlalchemy import true
from tables import Description

class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help overview", description="Use !help <category> for more information. **First letter has to be capitilized!**")
        for cog in mapping:
            if cog:
                list = ""
                for command in cog.get_commands():
                    list += command.name + ', '
                embed.add_field(name = cog.qualified_name, value = list[:-2])
        await self.get_destination().send(embed=embed) # get_destination: Calls destination a.k.a. where you want to send the command
                
    async def send_cog_help(self, cog):
        if cog:
            embed = discord.Embed(title="Help " + cog.qualified_name, description="Use !help <command> for more information.")
            list = ""
            for command in cog.get_commands():
                list += command.usage
                for alias in command.aliases:
                    list += ', [!' + alias + ']'
                list += ': ' + command.description + "\n"
            embed.add_field(name = cog.qualified_name, value = list[:-2])
            await self.get_destination().send(embed=embed)
        else:
            await self.get_destination().send("This is not a valid cog.")

    async def send_group_help(self, group):
        #await self.get_destination().send(f'{group.name}: {[command.name for index, command in enumerate(group.commands)]}')
        await self.get_destination().send('This is not implemented yet but you can use !help <command>')
    
    async def send_command_help(self, command):
        title = command.name.capitalize()
        for alias in command.aliases:
            title += ', [!' + alias + ']'
        embed = discord.Embed(title=title, description=command.description)
        if command.usage != '':
            embed.add_field(name="Syntax:", value=command.usage, inline=False)
        if command.help != '':
            embed.add_field(name="Extra:", value=command.help, inline=False)
        await self.get_destination().send(embed=embed)