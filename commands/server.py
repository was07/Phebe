import socket
from functools import lru_cache
from os import uname
from typing import Union

import disnake

from base import Bot, commands, Context, Embed
from init import Config

# Was this copied from PyDis?
rules = [
    "Be respectful, civil, and welcoming to others in the server.",
    "The language of this server is English, Use English to the best of your ability."
    "Be polite if someone speaks English imperfectly.",
    (
        "Do not misuse or spam/troll in any of the channels, Do not attempt to bypass"
        + " any blocked words."
    ),
    (
        "Do not advertise anything without permission. No Discord server invite links"
        + " or codes."
    ),
    (
        "Controversial topics such as religion or politics are not allowed (even in off"
        + " topic)."
    ),
    "Ping someone only when there is legitimate reasoning behind them.",
    "Follow the Discord Community Guidelines and Terms of Service.",
]


rules_channel = "https://discord.com/channels/929705391691030548/929707061195968542"


@lru_cache(maxsize=1)
def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def safe_limit(s: Union[str, bytes]) -> str:
    if isinstance(s, bytes):
        s = s.decode()
    if len(s) >= 255:
        trailer = " ..."
        return s[:255] + trailer
    if len(s) == 0:
        s = "\u200B"
    return s


class Server(commands.Cog):
    """The cog for the Pythonic Hangout server related things."""

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.command()
    async def rule(self, ctx: Context, number: int) -> None:
        """Shows you the specified rule with that index."""

        if not 0 < number < len(rules) + 1:
            return

        await ctx.send(
            embed=disnake.Embed(
                title=f"Rule {number}", url=rules_channel, description=rules[number - 1]
            )
        )

    @commands.command()
    async def rules(self, ctx: Context) -> None:
        """Shows you all of the rules."""

        await ctx.send(
            embed=disnake.Embed(
                title="Rules",
                url=rules_channel,
            )
        )
        return

    @commands.command(help="Get information about server", aliases=["serverinfo"])
    async def server(self, ctx: Context) -> None:
        """Shows you information about this server."""

        guild = ctx.guild

        offline_members = 0
        online_members = 0

        sysname, _, _, _, arch = uname()

        for member in guild.members:
            if member.status == disnake.Status.offline:
                offline_members += 1
            else:
                online_members += 1

        embed = Embed(
            title=guild.name,
            colour=disnake.Colour.brand_green(),
        )
        embed.set_thumbnail(guild.icon)
        embed.add_field(name="Total Members", value=guild.member_count, inline=False)
        embed.add_field(
            name="Members Status",
            value=f"⚪ {offline_members} 🟢 {online_members}",
            inline=False,
        )
        embed.add_field(name="Prefix", value=Config.prefix, inline=True)
        embed.set_footer(text=f"Server: {sysname} on {arch}")
        await ctx.send(embed=embed)
