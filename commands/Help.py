from base import *
def override(func): return func
from logging import getLogger
from init import Config
from disnake.ext.commands.help import Paginator
log = getLogger(__name__)

class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        self.clean_prefix = options.pop("prefix")
        self.width = options.pop("width", 80)
        self.indent = options.pop("indent", 2)
        self.sort_commands = options.pop("sort_commands", False)
        self.commands_heading = options.pop("commands_heading", "Commands:")
        self.no_category = options.pop("no_category", "Python")
        self.paginator = options.pop("paginator", Paginator())
        super().__init__(**options)
        self.context.bot = bot

    @override
    def get_command_signature(self, command):
        return f"{self.clean_prefix}" f"{command.qualified_name} " f"{command.signature}"

    # @override
    # async def send_pages(self):
    #     destination = self.get_destination()
    #     log.info("send_pages: destination=%s", destination)
    #     for page in self.paginator.pages:
    #         page = page.strip().strip("```")
    #         log.info("page=%s", page)
    #         emby = Embed(description=page)
    #         await destination.send(embed=emby)

    async def send_bot_help(self, mapping):
        embed = disnake.Embed(title='help')
        
        for cog, commands in mapping.items():
            commands = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                txt = ''
                for c in commands:
                    txt += '\n`'+self.get_command_signature(c)+'`'
                embed.add_field(name=cog_name, value=txt)
        
        await self.context.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = disnake.Embed(title=self.get_command_signature(command))
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        cmds = self.get_bot_mapping()
        
        embed = Embed(
            title=group,
        )
        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    @override
    def __init__(self, bot: Bot):
        log.info("loading %s cog", type(self).__name__)
        log.info("original help cmd: %s", bot.help_command)
        self._original_help_command = bot.help_command
        new_help_command = MyHelpCommand(prefix=Config.prefix)
        log.info("new help cmd: %s", new_help_command)
        bot.help_command = new_help_command
        bot.help_command.cog = self

    @override
    def cog_unload(self):
        self.bot.help_command = self._original_help_command
