from base import *
import re
import requests


class PyPi(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
    
    @commands.command(alias="pypi")
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
