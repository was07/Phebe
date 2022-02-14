from base import *
from contextlib import redirect_stderr, redirect_stdout
from disnake import Color
from io import StringIO
from re import subn, DOTALL
from tempfile import NamedTemporaryFile
from traceback import print_exc 
from types import CodeType
import getdoc
from init import Formatted
import re
import requests


class Python(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
        type(self).__cog_name__ = "Python"


    @commands.command(help='Run/Evaluate Python code', aliases=['eval'])
    async def  e(self, ctx, *, source: str=""):
        if ctx.author.id == 883987539961192508:  # 00001H
            await ctx.reply("Sorry, Eval is not available, **for you.**")
            return
        
        result: Any
        code: CodeType
        color: Color 
        source = source.strip()
        source = subn(
          r"(^|\n)``?`?(?:py|)", "\\1",
          source, DOTALL       )[0]
        source = source.strip()
        source = source.strip("`")
        import sandbox
        rs, stdout, stderr = sandbox.run(source)
        if rs is not None:
            color = disnake.Colour.green() if rs == 0 else disnake.Colour.red()
            output = []

            output_limit = 1950
            stdout_truncated = stdout[:output_limit] + ('' if len(stdout) < output_limit else '... (output truncated)')
            stderr_truncated = stderr[:output_limit] + ('' if len(stderr) < output_limit else '... (output truncated)')
          
            if stderr:
                output.append("\n".join((
                  "_Standard Error_ (" 
                  f"{len(stderr)} characters):",
                  f"```\n{stderr_truncated}\n```"
                )))
            if stdout:
                output.append("\n".join((
                  "_Standard Output_ (" 
                  f"{len(stdout)} characters):",
                  f"```\n{stdout_truncated}\n```"
                )))
            outcome = "successfully" if rs == 0 else "unsuccessfully" 
            if not stderr and not stdout:
                output.append(f"Program {outcome} completed with exit status {rs} and produced no output.")
            else:
                output.append(f"Program {outcome} completed with exit status {rs}.")
            description = "\n".join(output)
        await ctx.reply(embed=disnake.Embed(
            title = "Output",
            description=description,
            color=color,
        ))


    @commands.command(help='Get the Documentation of a python object' , aliases=['doc'])
    def d(self, ctx, symbol: str='', nparas: int=1):
        """Get the Documentation of a python object"""
        symbol = symbol.strip('`')
        if symbol == 'Creds':
            await ctx.send(embed=disnake.Embed(title='Credits',description="Made by `Greyblue92`, `Was'` and `Pancake`, `sz_skill`"))
        elif symbol:
            doc: Formatted
            item, doc, url = getdoc.getdoc(symbol, nparas)
            await ctx.send(embed=disnake.Embed(
                title = symbol,
                url=url,
                description = str(doc),
                color=disnake.Color.blue()
            ))

    
    @commands.command(help='Get the documentation of a python object', alias="pypi")
    async def pypi(self, ctx, name=None):
        if name is None:
            await ctx.send('Package name required.')
            return

        resp = requests.get(f'https://pypi.org/pypi/{name}/json')
        if resp.status_code == 404:
            await ctx.send(embed=disnake.Embed(title=f"Could not find {name}"))
            return

        data = resp.json()
        info = data['info']
        url = info['project_url']

        rawdescr = info['description']
        text = format(rawdescr)
        await ctx.send(embed=disnake.Embed(
            title=name, 
            url=url,
            description=text,
            color=disnake.Color.blue(),
        ))



def format(text, lines=6):
    res = ""
    text = re.compile(
      r'\s*</?(?:(?!\n[\n\r#]).)*>\s*',
      re.DOTALL
    ).subn('\n\n', text)[0]
    text = text.replace('```python', '__start_py')
    l = 0
    for line in text.splitlines():
        line = line.strip()
        l += 1
        if line.startswith('##'):
            res += f"*{line.lstrip('##').strip()}*"
        elif line.startswith('#'):
            res += f"**{line.lstrip('#').strip()}**"
        elif line.startswith(':'):
            res += f"**{line.lstrip(':').strip()}**"
        elif line.startswith('*'):
            res += f'__{line.strip("*").strip()}__'
        elif line.startswith('|'):
            res += f"**{line.lstrip('|').strip()}**"
        elif line.startswith('||'):
            res += f"**{line.lstrip('||').strip()}**"
        elif line.startswith('. ...'):
            res += f"**{line.lstrip('. ...').strip()}**"
        else:
            res += line
        res += '\n'
        if l >= lines and '__start_py' in res and '```' not in res:
            res += '```'
            break 

    res = res.replace('__start_py', '```py')
    return res.rstrip() + ' ...'
