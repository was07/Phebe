from base import *


class ServerInfo(commands.Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    # serverinfo
    @commands.command()
    async def serverinfo(self, ctx: Context) -> None:
        guild = ctx.guild
        embed = Embed(title=guild.name)
        embed.set_thumbnail(guild.icon)
        offline_members = 0
        online_members = 0

        print(len(guild.members))
        print(repr(guild))
        for member in guild.members:
            print("member=", repr(member), "status=", repr(member.status))
            if member.status == disnake.Status.offline:
                offline_members += 1
            else:
                online_members += 1

        embed.add_field(name='Total Members',
                        value=guild.member_count,
                        inline=False)
        embed.add_field(name='Members Status',
                        value=f"⚪ {offline_members} 🟢 {online_members}")

        await ctx.send(embed=embed)

    # serverinfo
    @commands.command()
    async def serverinfo_(self, ctx: Context) -> None:
        guild = ctx.guild
        embed = Embed(title=guild.name)
        embed.set_thumbnail(guild.icon)
        offline_members = 0
        online_members = 0

        print(len(guild.members))
        print(repr(guild))
        for member in guild.members:
            print("member=", repr(member), "status=", repr(member.status))
            import inspect
            for k, v in inspect.getmembers(member):
                if callable(v) or k.startswith("__") or "None" in repr(v) or "guild" in k:
                    continue
                print(f"  {k}={v!r} / {v!s}")
            if member.status == disnake.Status.offline:
                offline_members += 1
            else:
                online_members += 1

        embed.add_field(name='Total Members',
                        value=guild.member_count,
                        inline=False)
        embed.add_field(name='Members Status',
                        value=f"⚪ {offline_members} 🟢 {online_members}")
        import inspect
        for k, v in inspect.getmembers(self.bot):
                if callable(v) or k.startswith("__") or "None" in repr(v) or "guild" in k:
                    continue
                print(f"  {k}={v!r} / {v!s}")
                
        await ctx.send(embed=embed)
