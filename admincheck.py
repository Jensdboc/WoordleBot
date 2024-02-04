from discord.ext import commands
from pathlib import Path

ADMIN_ID = 656916865364525067


def file_exist(name: str) -> None:
    """
    Create file if it doesn't exist

    name: str
        Name of file
    """
    file = Path(name)
    file.touch(exist_ok=True)


def admin_check(ctx: commands.Context) -> bool:
    """
    Check if user has admin priveledges

    Parameters
    ----------
    ctx : commands
        Context the command is represented in
    Returns
    -------
    is_admin : bool
        True if admin, else False.
    """
    return ctx.message.author.id == ADMIN_ID
