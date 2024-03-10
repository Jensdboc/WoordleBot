import discord
from discord.ext import commands

from constants import PREFIX


class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help overview", description="Use =help <category> for more information. Category has to be **capitalized**!")
        for cog in mapping:
            if cog:
                command_name_list = []
                for command in cog.get_commands():
                    if not any(check.__qualname__ == 'admin_check' for check in command.checks):
                        command_name_list.append(command.name)
                if command_name_list != []:
                    embed.add_field(name=cog.qualified_name, value=', '.join(command_name_list), inline=False)
        # get_destination: Calls destination a.k.a. where you want to send the command
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        if cog:
            embed = discord.Embed(title="Help " + cog.qualified_name, description=f"Use {PREFIX}help <command> for more information.")
            list = ""
            for command in cog.get_commands():
                if not any(check.__qualname__ == 'admin_check' for check in command.checks):
                    list += command.usage if command.usage else "No usage defined"
                    for alias in command.aliases:
                        list += f", {PREFIX}{alias}"
                    list += f": {command.help if command.help else 'No description defined'}\n"
            if list != "":
                embed.add_field(name=cog.qualified_name, value=list.rstrip("\n"))
                await self.get_destination().send(embed=embed)
            else:
                await self.get_destination().send("Wow, how did you find this? Have a :cookie:!")
        else:
            await self.get_destination().send("This is not a valid cog.")

    async def send_command_help(self, command):
        if not any(check.__qualname__ == 'admin_check' for check in command.checks):
            title = f"{PREFIX}{command.name}"
            for alias in command.aliases:
                title += f", {PREFIX}{alias}"
            embed = discord.Embed(title=title, description=command.description)
            if command.usage != '':
                embed.add_field(name="Syntax:", value=command.usage, inline=False)
            await self.get_destination().send(embed=embed)
        else:
            await self.get_destination().send("How did you find this command? Admin access only!")
