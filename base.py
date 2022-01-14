from disnake.ext import commands
from disnake.ext.commands import Bot
from disnake.ext.commands.core import Context
from disnake.member import Member
from disnake.guild import Guild
from disnake.embeds import Embed
from disnake.channel import ChannelType
from disnake.message import Message
import disnake
import sys
disnake; commands; Bot; Context; Member; Guild; Embed; ChannelType; Message


def setup(bot: commands.Bot):
    """
    Needed for dynamic modules to work with load_extension
    without requiring each to have a boilerplate setup()
    function
    """
    module_name = [k for k in sys.modules.keys() if k.startswith("commands")][-1]
    class_name = module_name.split(".")[-1]
    module = sys.modules.get(module_name)
    cog_cls = getattr(module, class_name)
    cog_obj = cog_cls(bot)
    print(f"Loading extension comand: {class_name} ...", end="")
    bot.add_cog(cog_obj)
    print(f"OK: {cog_obj}")
    