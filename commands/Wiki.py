from base import *
import bs4, requests


class Wiki(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot
   
    @commands.command()
    async def wiki(self, ctx, *, name=""):
        print(f"{name=}")
        import re, bs4, requests;
        response = requests.get(
            "https://en.m.wikipedia.org/w/index.php",
            params={
                "search":name,
                "title":"Special:Search"    
            }
        )
        html = response.content
        odx = html.find(b"mf-section-0")
        if odx != -1:
            html = html[0:odx + 6000]

        doc2 = bs4.BeautifulSoup(html); import urllib; 
        title = doc2.select("h1")[0].text
        base_url = urllib.parse.urlparse(doc2.select("link[rel=\"canonical\"]")[0].attrs["href"]); 
        thumbnail = ""; img_tags = sorted(((int(e.attrs.get("width", e.attrs.get("data-file-width")) or "0"), e) for e in doc2.select("img[alt]:not([src*=\".svg\"])")), key=lambda i:i[0], reverse=True);
        if img_tags: img_tag = img_tags[0][1]; thumbnail = urllib.parse.urljoin(base_url.geturl(), img_tag.attrs["src"]);
        paras = doc2.select("#mf-section-0 > p:not(.mw-empty-elt)")
        para = paras[0]
        format_map = {
            "b,strong": "**{text}**",
            "i,em":"*{text}*",
            "u":"__{text}__",
            "a":"({href})[{text}]",
            "p":"\x0A{html}\x0A",
            "sup":"" 
        }
        [
            [
            el.replace_with(
                bs4.TemplateString(tmpl).format_map(
                {
                    "text": el.text,
                    "html": str(el),
                    **el.attrs  
                }
                )
            )
            for el in para.select(selector)
            ] for selector, tmpl in format_map.items()
        ]
        description = re.subn(r'\((/wiki/(?:\w|\[|\]|[()_.+~,:/\'-])*)\)\[([^]]+)\]', r'[\2](https://en.m.wikipedia.org\1)', para.text)[0]
        embed = Embed(
            title=title,
            color=0xFFFFFF,
            description=description,
            url=base_url.geturl(),
        ) # oh good call  # k
        embed.set_footer(text="wikipedia", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Tango_style_Wikipedia_Icon.svg/1200px-Tango_style_Wikipedia_Icon.svg.png")  # icon can be the icon of wikipedia?
        
        if thumbnail: embed.set_thumbnail(url=thumbnail)  # this sets image
        await ctx.send(embed=embed)
