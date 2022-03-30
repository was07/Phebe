from disnake import Color
from base import *
from factgen import random_fact



class Fact(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def fact(self, ctx):
        text, source = random_fact()

        embed = Embed(
            title="Random Fact",
            description=text,
            url=source,
            color=Color.yellow(),
        )
        embed.set_footer(text=f"Source: {source}")
        await ctx.reply("Here's your random fact!", embed=embed)
