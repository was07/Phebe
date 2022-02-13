from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.ext.commands.core import Context
from disnake.member import Member
from disnake.guild import Guild
from disnake.embeds import Embed
from disnake.channel import ChannelType
from disnake.message import Message
from disnake import Role
from disnake.user import User
from typing import Union
import disnake
import sys
# for replit
disnake
commands
Bot
Context
Member
Guild
Embed
ChannelType
Message
User


def member_for(user: Union[User, Member]) -> Member:
    "Return the full Member object corresponding to `user`."
    if isinstance(user, Member):
        return user
    from __main__ import bot
    return [m for m in bot.guilds[0].members if m.id == user.id][0] # XXX: FIXME Need bot.


def role_names(user: Union[User, Member]) -> dict[str, Role]:
    "Return a dict mapping role names to Role objects."
    return {r.name: r for r in member_for(user).roles}


def setup(bot: commands.Bot):
    """
    Needed for dynamic modules to work with load_extension
    without requiring each to have a boilerplate setup()
    function
    """
    import builtins
    if bot and "bot" not in vars(builtins):
        builtins.bot = bot
    
    module_name = [k for k in sys.modules.keys() if k.startswith("commands")][-1]
    class_name = module_name.split(".")[-1]
    module = sys.modules.get(module_name)
    cog_cls = getattr(module, class_name)
    cog_obj = cog_cls(bot)
    print(f"Loading extension comand: {class_name} ...", end="")
    bot.add_cog(cog_obj)
    print(f"OK: {cog_obj}")