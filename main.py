"""
Phebe
A discord bot for the Python Experts Server
"""
import logging
import sys
import disnake
import asyncio
import os
import random
import threading
import traceback
from pathlib import Path
from threading import Thread

from disnake import Activity, ActivityType, Game

import StayAlive
from base import Member, commands
from init import Config

logging.root.setLevel(logging.WARNING)
logging.root.addHandler(logging.StreamHandler(sys.stderr))
log = logging.getLogger(__name__)
banned_words = ["@everyone", "@here"]


class Phebe(commands.Cog):
    """
    Official bot for the Pythonic Hangout server
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Shows a message when the bot gets online."""
        print(
            "\u001b[34m"
            + f"[+] Bot is running! \n[+] Ping: {self.bot.latency*1000} ms"
            + "\u001b[0m"
        )
        self.bot.loop.create_task(self.status_task())

    # XXX TODO: Migrate to commands.WordFilter
    @commands.Cog.listener()
    async def on_message(self, message):
        author: Member = message.author
        if author.bot:
            return

        roles_by_name = [role.name for role in author.roles]

        if "Moderation Team" in roles_by_name:
            return

        for word in banned_words:
            if word in message.content.lower():
                await message.delete()
                await message.author.send(
                    embed=disnake.Embed(
                        title="Warning",
                        description=(
                            f"**{author.mention}: Your message got deleted by saying**"
                            + f" *{word}* __that is a banned word.__",
                        ),
                    )
                )

    # XXX TODO: Migrate to commands.Status
    async def status_task(self):
        if Config.prefix == ".":
            return
        for activity in (
            Game(name=".help"),
            Activity(type=ActivityType.watching, name="Members in Servers"),
            Activity(type=ActivityType.listening, name="Moderation team command."),
        ):
            await self.bot.change_presence(activity=activity)
            await asyncio.sleep(30)

    # XXX TODO: Migrate to commands.Ping
    @commands.command()
    async def ping(self, ctx):
        """Show latency in milliseconds"""

        await ctx.send(
            embed=disnake.Embed(
                title="Pong!",
                description=(
                    "🟢 **Bot is active**\n\n🕑 **Latency:** "
                    + f"{round(self.bot.latency*1000, 3)} ms"
                ),
            )
        )

    # XXX TODO: Migrate to commands.Warn
    @commands.command()
    async def warn(self, ctx, member: disnake.Member):
        """Warns a member."""
        await ctx.send(f"{member: disnake.Member} has been warned")

    # XXX TODO: Migrate to commands.Timeout
    @commands.command()
    async def timeout(self, ctx, time, member: disnake.Member = None):
        """Timeouts a member."""
        await member.timeout(duration=time)

    # XXX TODO: Migrate to commands.PFP
    @commands.command()
    async def pfp(self, ctx, member: disnake.Member = None):
        """Shows the profile picture of a user, or yours"""

        embed = disnake.Embed(
            title=(
                "Profile Picture of"
                + f"{ctx.author.display_name if not member else member.display_name}"
            ),
        )

        embed.set_image(url=ctx.author.avatar if member is None else member.avatar)
        await ctx.send(embed=embed)

    # XXX TODO: Migrate to commands.Flip
    @commands.command()
    async def flip(self, ctx):
        """Flips a virtual coin and gets the result."""

        heads_url = (
            "https://cdn-icons.flaticon.com/png/512/5700/premium/5700963.png?token=exp="
            + "1643128433~hmac=831aba311ab86e1ef73059e55178e712"
        )
        tails_url = (
            "https://cdn-icons.flaticon.com/png/512/2173/premium/2173470.png?token=exp="
            + "1643127144~hmac=a622b3080fe202709c7745ac894df97b"
        )

        res = random.randint(1, 2)

        embed = disnake.Embed(
            title="Flipped a coin",
            description=f"**{('Heads' if res == 1 else 'Tails')}**",
        )

        embed.set_thumbnail(heads_url if res == 1 else tails_url)

        await ctx.reply(embed=embed)

    # XXX TODO: Migrate to commands.Roll
    @commands.command()
    async def roll(self, ctx):
        """roll a virtual dice and get the result"""
        comp = random.randint(1, 6)

        await ctx.reply(
            embed=disnake.Embed(title="Rolled a dice", description=f"Result is {comp}")
        )

    # XXX TODO: Migrate to commands.Format
    @commands.command()
    async def format(self, ctx):
        await ctx.send(
            embed=disnake.Embed(
                title="Code formatting",
                ddescription="""
To properly format Python code in Discord, write your code like this:

\\`\\`\\`py
print("Hello world")\n\\`\\`\\`\n\n    **These are backticks, not quotes**. They are of-
ten under the Escape (esc) key on most keyboard orientations, they could be towards the-
right side of the keyboard if you are using eastern european/balkan language keyboards.
""",
            )
        )


if __name__ == "__main__":
    intents = disnake.Intents.none()
    intents.messages = True
    intents.guilds = True
    intents.members = True
    try:
        intents.presences = True
        bot: commands.Bot = commands.Bot(
            command_prefix=Config.prefix,
            description=Phebe.__doc__,
            intents=intents,
            help_command=None,
        )
    except Exception:
        intents.presences = False
        bot: commands.Bot = commands.Bot(
            command_prefix=Config.prefix,
            description=Phebe.__doc__,
            intents=intents,
            help_command=None,
        )
    bot.add_cog(Phebe(bot))

    dir: Path = Path("commands")
    for item in dir.iterdir():
        if item.name.endswith(".py"):
            name = f"{item.parent.name}.{item.stem}"
            print(f"Loading extension: {name}")
            try:
                bot.load_extension(name)
            except BaseException as exc:
                print(
                    "\x0a".join(
                        traceback.format_exception(type(exc), exc, exc.__traceback__)
                    ),
                    file=sys.stderr,
                )

    t = Thread(target=StayAlive.start_server)
    t.start()

    while True:
        try:
            bot.run(Config.token)
        except disnake.errors.HTTPException:
            traceback.print_exc(999, sys.stderr, True)
            try:
                threading.shutdown()
            finally:
                os._exit(255)
