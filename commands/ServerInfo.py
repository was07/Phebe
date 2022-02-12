from base import *
from init import Config
from functools import lru_cache
from os import getcwd, getenv, uname
from os.path import expanduser
from pathlib import Path
from shlex import join
from typing import Union
import socket

@lru_cache(maxsize=1)
def get_lan_ip():
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    lan_ip = s.getsockname()[0]
    return lan_ip

def safe_limit(s: Union[str,bytes]) -> str:
    if isinstance(s, bytes):
        s = s.decode()
    if len(s) >= 1024:
        trailer = " ..."
        return s[0: -len(trailer)] + trailer
    if len(s) == 0:
        s = "\u200B"
    return s

class ServerInfo(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot: Bot = bot

    # serverinfo
    @commands.command()
    async def serverinfo(self, ctx: Context) -> None:
        guild = ctx.guild
        
        offline_members = 0
        online_members = 0
        lan_ip = get_lan_ip()
        arch, nodename, sysname, release, version = uname()

        for member in guild.members:
            if member.status == disnake.Status.offline:
                offline_members += 1
            else:
                online_members += 1

        embed = Embed(title=guild.name)
        embed.set_thumbnail(guild.icon)
        embed.add_field(name='Total Members',
                        value=guild.member_count,
                        inline=False)
        embed.add_field(name='Members Status',
                        value=f"⚪ {offline_members} 🟢 {online_members}",
                        inline=False)
        embed.add_field(name="Prefix", value=Config.prefix, inline=True)
        embed.add_field(name="Architecture", value=arch, inline=True)
        embed.add_field(name="Hostname", value=nodename, inline=True)
        embed.add_field(name="LAN IP", value=lan_ip, inline=True)
        embed.add_field(name="OS Type", value=sysname, inline=True)
        embed.add_field(name="OS Release", value=release, inline=True)
        embed.add_field(name="Build Info", value=version, inline=True)
        embed.add_field(name="Home dir", value=expanduser("~"), inline=True)
        embed.add_field(name="PATH", value=expanduser(getenv("PATH", "/sbin:/bin:/usr/bin")), inline=True)
        embed.add_field(name="Current dir", value=expanduser(getcwd()), inline=True)
        embed.add_field(name="Previous dir", value=safe_limit(expanduser(getenv("OLDPWD", "~"))), inline=True)
        embed.add_field(name="Shell", value=safe_limit(expanduser(getenv("SHELL", "/bin/sh"))), inline=True)
        embed.add_field(name="Self",
            value=safe_limit(
                join(
                    map(
                        lambda i: i.decode("utf-8"),
                        Path("/proc/self/cmdline")
                            .read_bytes()
                            .split(b"\x00")
                    )
                )
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

#
#
        