#this one is in construction
from base import *



#starting
## TODO: Use CamelCase name for file and class
class money(commands.Cog):

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def money(self, ctx):
        await ctx.send("You have no money")
