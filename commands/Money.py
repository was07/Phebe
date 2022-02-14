#this one is in construction
from base import *



#starting
## TODO: Use CamelCase name for file and class
class Money(commands.Cog):

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        await ctx.send("You have freaking money")
