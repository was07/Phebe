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
        return (
            f'{self.clean_prefix}'
            f'{command.qualified_name} '
            f'{command.signature}'
        )

class Help(commands.Cog):
    @override
    def __init__(self, bot: Bot):
        log.info("loading {} cog", type(self).__name__)
        log.info("original help cmd: {}", bot.help_command)
        self._original_help_command = bot.help_command
        new_help_command = MyHelpCommand(prefix=Config.prefix)
        log.info("new help cmd: {}", new_help_command)
        bot.help_command = new_help_command
        bot.help_command.cog = self
    
    @override
    def cog_unload(self):
        self.bot.help_command = self._original_help_command

