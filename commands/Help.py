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

    @override
    async def send_pages(self):
        destination = self.get_destination()
        log.info("send_pages: destination=%s", destination)
        for page in self.paginator.pages:
            page = page.strip().strip("```")
            log.info("page=%s", page)
            emby = Embed(description=page)
            await destination.send(embed=emby)


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
