"""
Phebe
A discord bot for the Python Experts Server
"""
import disnake
from disnake import Activity, ActivityType, Game
from disnake.ext import commands

import logging, sys

l = logging.getLogger("disnake.client")
l.setLevel(logging.INFO)
logging.root.setLevel(logging.INFO)
# logging.root.addHandler(logging.StreamHandler(sys.stderr))

from pathlib import Path
import os
import random
from threading import Thread
import asyncio
import StayAlive
from colorama import Fore
from init import Config
from base import *

banned_words = ["@everyone", "@here"]

hlp = {
    "Python": {
        "d": ("(symbol)", "Get the Python documentation for a given symble"),
        "e": ("(code)", "Evaluate or run Python code and see output"),
        "pypi": ("(name)", "Get the description of a pip module")
    },
    "Server": {
        "rule": ("(number)", "Get a specific rule of the server"),
        "serverinfo": ("", "Get some information about the server")
    },
    "More": {
        "wiki": ("(subject)", "Get the Wikipedia page of a subject")
    }
}


class Phebe(commands.Cog):
    """
    Official bot for the Pythonic Hangout server
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """show message when bot gets online"""
        print(Fore.BLUE +
              f'[+] Bot is running! \n[+] Ping: {self.bot.latency*1000} ms')
        self.bot.loop.create_task(self.status_task())
    
    ## XXX TODO: Migrate to commands.WordFilter
    @commands.Cog.listener()
    async def on_message(self, message):
        author: Member = member_for(message.author)
        if author.bot:
            return
        roles_by_name: dict[str,Role] = role_names(author)
        if "Moderation-Team" in roles_by_name:
            return
        for word in banned_words:
            if word in message.content.lower():
                await message.delete()
                await message.author.send(
                    embed=disnake.Embed(
                        title='Warning',
                        description=f"**{author.mention}: Your message got deleted by saying** *{word}* __that is a banned word.__")
                    )
    
    ## XXX TODO: Migrate to commands.Status
    async def status_task(self):
        if Config.prefix == ".":
            return    
        for activity in (
            Game(name=".help"),
            Activity(
                type=ActivityType.watching,
                name="Members in Servers"
            ),
            Activity(
                type=ActivityType.listening,
                name="Moderation team command."
            )
        ):
            await self.bot.change_presence(activity=activity)
            await asyncio.sleep(30)
    
    ## XXX TODO: Migrate to commands.Ping
    @commands.command()
    async def ping(self, ctx):
        """Show latency in mili seconds"""
        await ctx.send(embed=disnake.Embed(
            title='Pong!',
            description=f"🟢 **Bot is active**\n\n🕑 **Latency: **{round(self.bot.latency*1000, 3)} ms"),
            color=""
        )

    ## XXX TODO: Migrate to commands.Warn
    @commands.command()
    async def warn(self, ctx, member: disnake.Member):
        """Warn a User"""
        await ctx.send(f"{member: disnake.Member} has been warned")

    ## XXX TODO: Migrate to commands.Timeout
    @commands.command()
    async def timeout(self, ctx, time, member: disnake.Member = None):
        """Timeout a User"""
        await member.timeout(duration=time)
    
    ## XXX TODO: Migrate to commands.PFP
    @commands.command()
    async def pfp(self, ctx, member: disnake.Member = None):
        """Show profile picture of a user, or see yours"""

        embed = disnake.Embed(
            title=
            f'Profile Picture of {ctx.author.display_name if member is None else member.display_name}'
        )

        embed.set_image(
            url=ctx.author.avatar if member is None else member.avatar)
        await ctx.send(embed=embed)

    ## XXX TODO: Migrate to commands.Flip
    @commands.command()
    async def flip(self, ctx):
        """Flip a vertual coin and get the result"""
        heads_url = "https://cdn-icons.flaticon.com/png/512/5700/premium/5700963.png?token=exp=1643128433~hmac=831aba311ab86e1ef73059e55178e712"
        tails_url = "https://cdn-icons.flaticon.com/png/512/2173/premium/2173470.png?token=exp=1643127144~hmac=a622b3080fe202709c7745ac894df97b"

        res = random.randint(1, 2)

        embed = disnake.Embed(
            title='Flipped a coin',
            description=f"**{('Heads' if res == 1 else 'Tails')}**",
        )

        embed.set_thumbnail(heads_url if res == 1 else tails_url)

        await ctx.reply(embed=embed)

    ## XXX TODO: Migrate to commands.Roll
    @commands.command()
    async def roll(self, ctx):
        """roll a virtual dice and get the result"""
        comp = random.randint(1,6)

        await ctx.reply(embed=disnake.Embed(
            title="Rolled a dice", description=f"Result is {comp}"
        ))
    
    ## XXX TODO: Migrate to commands.Format
    @commands.command()
    async def format(self, ctx):
        await ctx.send(embed=disnake.Embed(title='Code formatting',
                                           ddescription="""
		To properly format Python code in Discord, write your code like this:

\\`\\`\\`py
print("Hello world")\n\\`\\`\\`\n\n    **These are backticks, not quotes**. They are often under the Escape (esc) key on most keyboard orientations, they could be towards the right side of the keyboard if you are using eastern european/balkan language keyboards.
"""))


class Globals:
  intents = disnake.Intents.none()  
  intents.messages = True
  intents.guilds = True
  intents.members = True
  intents.presences = True
  bot: commands.Bot = commands.Bot(
            command_prefix=Config.prefix,
            description=Phebe.__doc__,
            intents=intents,
  )
  cogs = {}
  commands = {}
  @classmethod
  def load_cogs(cls):
    phebe: Phebe = Phebe(cls.bot)
    cls.cogs[type(phebe).__name__] = phebe
    cls.bot.add_cog(phebe)
    cls.commands.update({
      c.name: c
      for c in phebe.get_commands()
    })
    
    dir: Path = Path("commands")
    for item in dir.iterdir():
        if item.name.endswith(".py"):
            name = f'{item.parent.name}.{item.stem}'
            print(f"Loading extension: {name}")
            before = set(cls.bot._CommonBotBase__cogs)
            ext = cls.bot.load_extension(name)
            for k in (
             set(cls.bot._CommonBotBase__cogs) - before
            ):
              newcog = cls.bot._CommonBotBase__cogs[k]
              cls.cogs[k] = newcog
              cls.commands.update({
                c.name: c
                for c in newcog.get_commands()
              })
              print(f"Loaded cog '{k}' ({newcog})")

  @classmethod
  def start_threads(cls):
    cls.stay_alive_thread = t = Thread(
      target=StayAlive.start_server
    )
    t.start()
    
    cls.bot_thread = t2 = Thread(target=cls.run_bot)
    t2.start()
  
  @classmethod
  def run_bot(cls):
    bot.run(Config.token)

Globals.load_cogs()
import asyncio
login_rs = asyncio.run(Globals.bot.http.static_login(Config.token))
print(login_rs)

t = Thread(target=lambda: asyncio.run(
    Globals.bot.start(Config.token)
))
t.start()

