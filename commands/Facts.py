from replit import db
from base import *
from random import randint

# overnotice:just tring to make something that i am not even sure

# gives and tell facts about something that user is asking for
class Facts(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def facts(self, ctx):
        p = (1, 100)
        await ctx.send(p)
        await ctx.send("whales are big")
        await ctx.send("what do you wanna know")
        m = await self.bot.wait_for(
            "message", check=lambda m: m.author.id == ctx.author.id
        )
