from base import *


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
                        value=f"⚪ {offline_members} 🟢 {online_members}")

        await ctx.send(embed=embed)
