import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help overview", description="Use =help <category> for more information.")
        for cog in mapping:
            if cog:
                # TODO alles hieronder kan je vervangen door:
                '''
                command_name_list = []
                for command in cog.get_commands():
                    command_name_list.append(command.name)
                embed.add_field(name=cog.qualified_name, value=', '.join(command_name_list))
                '''
                list = ""
                for command in cog.get_commands():
                    list += f"{command.name}, "
                embed.add_field(name=cog.qualified_name, value=list[:-2])
        # get_destination: Calls destination a.k.a. where you want to send the command
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        if cog:
            embed = discord.Embed(title="Help " + cog.qualified_name, description="Use =help <command> for more information.")
            list = ""
            for command in cog.get_commands():
                list += command.usage
                for alias in command.aliases:
                    list += f", [!{alias}]"
                list += f": {command.description}\n"
            embed.add_field(name=cog.qualified_name, value=list[:-2])
            await self.get_destination().send(embed=embed)
        else:
            await self.get_destination().send("This is not a valid cog.")

    async def send_command_help(self, command):
        title = command.name.capitalize()
        for alias in command.aliases:
            title += f", [!{alias}]"
        embed = discord.Embed(title=title, description=command.description)
        if command.usage != '':
            embed.add_field(name="Syntax:", value=command.usage, inline=False)
        if command.help != '':
            embed.add_field(name="Extra:", value=command.help, inline=False)
        await self.get_destination().send(embed=embed)
