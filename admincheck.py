from discord.ext import commands
from pathlib import Path


def file_exist(name: str) -> None:
    """
    Create file if it doesn't exist

    :param name: Name of file
    """
    file = Path(name)
    file.touch(exist_ok=True)


def admin_check(ctx: commands.Context) -> bool:
    """
    Check if user has admin priveledges

    :param ctx: The context.

    :return: True if admin, else False.
    """
    file_exist('data/admin.txt')
    with open('data/admin.txt', 'r') as admin_file:
        for admin in admin_file.readlines():
            if str(ctx.message.author.id) == admin.rstrip("\n") or ctx.message.author.id == 268805544444166144:
                return True
        return False
