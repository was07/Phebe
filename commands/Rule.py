from base import *


rules = [
    "Be respectful, civil, and welcoming to others in the server.",

    "The language of this server is English, Use English to the best of your ability."
    "Be polite if someone speaks English imperfectly.",

    "Do not misuse or spam/troll in any of the channels, Do not attempt to bypass any blocked words.",

    "Do not advertise anything without permission. No Discord server invite links or codes.",

    "Controversial topics such as religion or politics are not allowed (even in off topic).",

    "ping someone only when there is legitimate reasoning behind them.",

    "Follow the Discord Community Guidelines and Terms of Service.",
]


rules_channel = "https://discord.com/channels/929705391691030548/929707061195968542"


class Rule(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
    
    @commands.command()
    async def rule(self, ctx: Context, number: int):
        if not 0 < number < len(rules)+1:
            return

        await ctx.send(embed=disnake.Embed(
                title=f'Rule {number}',
                url=rules_channel,
                description=rules[number - 1]
            )
        )
    
    @commands.command()
    async def rules(self, ctx: Context):
        return
