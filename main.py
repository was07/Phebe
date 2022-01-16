"""
Phebe
A discord bot for the Python Experts Server
"""
import disnake 
from disnake.ext import commands

from pathlib import Path
import os 
from threading import Thread
import requests
from init import Formatted
import asyncio
import StayAlive
import getdoc


class Phebe(commands.Cog):
    """
    Official bot for the Pythonic Hangout server
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """show message when bot gets online"""
        print('+ Bot is running!')
    
    ## ping and ban-warn-timeout

    @commands.command()
    async def ping(self, ctx):
        """show latency in mili seconds"""
        latency = self.bot.latency * 1000
        await ctx.send(
            embed=disnake.Embed(title='Pong!', description=f"{latency} ms"))
    
    @commands.command()
    async def warn(self, ctx, member: disnake.Member):
        """warn a User"""
        await ctx.send(f"{member: disnake.Member} has been warned")
	
    @commands.command()
    async def timeout(self, ctx, time, member: disnake.Member=None):
        """timeout a User"""
        await member.timeout(duration=time)

    # meeting command
    # @commands.command()
    # @commands.has_role("Moderation Team")
    # async def meeting(self, ctx: commands.Context, *topic: str):
    #     """Call a Moderation Team Meeting"""
    #     channel = self.bot.get_channel(927262021496471563)
    #     embed = disnake.Embed(
    #         title='Moderator Team Meeting')
    #     if topic:
    #         embed.add_field(name="topic", value=' '.join(topic))
    #     embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

    #     await channel.send("<@&927259243302776912>", embed=embed)
    
    @commands.command()
    async def pfp(self, ctx, member: disnake.Member = None):
        """show pfp of user"""
        
        embed=disnake.Embed(title=f'Profile Picture of {ctx.author.display_name if member is None else member.display_name}')
        
        embed.set_image(url=ctx.author.avatar if member is None else member.avatar)
        await ctx.send(embed=embed)

    @commands.command()
    async def format(self, ctx):
	    await ctx.send(embed=disnake.Embed(title='Code formatting',description="""
		To properly format Python code in Discord, write your code like this:

\\`\\`\\`py
print("Hello world")\n\\`\\`\\`\n\n    **These are backticks, not quotes**. They are often under the Escape (esc) key on most keyboard orientations, they could be towards the right side of the keyboard if you are using eastern european/balkan language keyboards.

This will result in proper syntax highlighting which makes it easier to see your code."""))

async def runserver():
  while True:
    StayAlive.start_server()
    await asyncio.sleep(8000)
    break
  
if __name__ == "__main__":
    intents = disnake.Intents.none()
    intents.messages = True
    intents.guilds = True
    intents.members = True
    try:
        intents.presences = True
        bot: commands.Bot = commands.Bot(
            command_prefix=".",
            description=Phebe.__doc__,
            intents=intents,
        )
    except:
        intents.presences = False
        bot: commands.Bot = commands.Bot(
            command_prefix=".",
            description=Phebe.__doc__,
            intents=intents,
        )
    bot.add_cog(Phebe(bot))
    dir: Path = Path("commands")
    for item in dir.iterdir():
        if item.name.endswith(".py"):
            name = f'{item.parent.name}.{item.stem}'
            print(f"Loading extension: {name}")
            bot.load_extension(name)

    t = Thread(target=StayAlive.start_server)
    t.start()
    
    while True:
        bot.run(
            os.getenv("Token") or 
            __import__("dotenv").get_key(dotenv_path=".env", key_to_get="Token")
        )
