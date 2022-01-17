from base import *
import bs4, re, requests
from bs4 import BeautifulSoup as BS, Tag, TemplateString
from bs4.builder import FAST, HTMLParserTreeBuilder
from functools import lru_cache
from typing import Any, Optional, Union
from urllib.parse import ParseResult, urljoin, urlparse

class HtmlToDiscord:
    url: str
    doc: Union[BS, Tag]
    html: str
    thumbnail: str
    title: str
    
    format_map = {
        "b,strong": "**{text}**",
        "i,em": "*{text}*",
        "u": "__{text}__",
        "a": "[{text}]({href})",
        "p": "\x0A{html}\x0A",
        "sup": "",
    }
    
    def __init__(
        self,
        html: Union[str, bytes, BS, Tag],
        url: Optional[str]=None,
    ):
        self._url = url
        self._doc = None
        self._title = None
        self._thumbnail = None
        self.html = None
        if isinstance(html, bytes):
            self.html = html.decode("utf-8")
        elif isinstance(html, str):
            self.html = html
        elif isinstance(html, BS):
            self._doc = html
        elif isinstance(html, Tag):
            self._doc = html
        else:
            raise ValueError(f"html must be one of: {type(self).__init__.__annotations__}")
    
    @staticmethod
    @lru_cache(maxsize=0)
    def parse(html: str) -> BS:
        builder = HTMLParserTreeBuilder(FAST)
        builder.preserve_whitespace_tags |= {
            'p', 'span', 'div', 'tt', 'code'
        }
        return BS(html) # , features=builder.features)

    @property
    def doc(self) -> Union[BS, Tag]:
        if self._doc is None:
            self._doc = HtmlToDiscord.parse(self.html)
        return self._doc
    
    @property
    def title(self) -> str:
        if not self._title:
            for title in self.doc.select("title"):
                text = title.text.strip()
                text = text.replace("\u2014", " - ")
                text = text.replace("\u2013", " - ")
                if " - " in text:
                    self._title = text.split(" - ")[0]
                else:
                    self._title = text
            else:
                for h1 in self.doc.select("h1"):
                    text = h1.text.strip()
                    text = text.strip("\u00b6")
                    text = text.strip()
                    self._title = text
        return self._title
    
    @property
    def url(self) -> str:
        if self._url is not None:
            return self._url
        canons = self.doc.select('link[rel="canonical"]')
        for canon in canons:
            self._url = canon.attrs["href"]
            return self._url
        return "//."
    
    @staticmethod
    def abs_url(base_url: Union[str,ParseResult], href: str) -> str:
        resolve_from = None
        if isinstance(base_url, str):
            resolve_from = urlparse(base_url)
        else:
            resolve_from = base_url
        target_url = urljoin(resolve_from.geturl(), href)
        return target_url
    
    @staticmethod
    def size_and_src(img: Tag) -> tuple[int, str]:
        
        size = 0
        src = img.attrs.get("src")
        for attr in ("data-image-width", "data-width", "width", "data-image-height", "data-height", "height"):
            val = img.attrs.get(attr)
            if not val: continue
            size = int(val)
            break
        if not src:
            for k, v in img.attrs.items():
                urlm = re.search("(?=^|\s|,)((?:https?:)//(\S+))", v)
                if urlm:
                    src = urlm.group(1)
                    break
        return size, src
   
    @property
    def thumbnail(self) -> str:
        if self._thumbnail is None:
            img_tags = self.doc.select('img.thumbnail')
            if not img_tags:
                img_tags = self.doc.select(
                            'img'
                           )
            if img_tags:
                ordered = sorted(list(
                    map(HtmlToDiscord.size_and_src, img_tags)
                ), key=lambda i:i[0])
                size, src = ordered[-1]
                url = HtmlToDiscord.abs_url(self.url, src)
                self._thumbnail = url
            else:
                self._thumbnail = ""
        return self._thumbnail
        
    def to_discord(self, elem: Tag):
        for anchor in elem.select("a[href], link[href]"):
            href = anchor.attrs["href"]
            abs_href = HtmlToDiscord.abs_url(self.url, href)
            anchor.attrs["href"] = abs_href
        
        for selector, tmpl in self.format_map.items():
            template = TemplateString(tmpl)
            for el in elem.select(selector):
                el.replace_with(
                    template.format_map({
                        "text": el.text,
                        "html": str(el),
                        **el.attrs 
                    })
                )

class Wiki(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.command()
    async def wiki(self, ctx, *, name=""):
        await ctx.send(embed=self._do_wiki(name))
    
    def _url_from_search(self, name) -> str:
        result_page = HtmlToDiscord(
            requests.get(
                f"https://en.m.wikipedia.org/w/index.php?search={name.replace(' ', '+')}&title=Special%3ASearch&profile=default&fulltext=1&ns0=1boost-template=1&prefer-recent=1"
            ).content
        )
        wiki_url = HtmlToDiscord.abs_url(
            result_page.url,
            result_page.doc.select(
                'a[data-serp-pos]'
            )[0].attrs["href"]
        )
        return wiki_url
    
    def _do_wiki(self, name) -> Embed:
        attempts = 0
        while (attempts:=attempts+1) < 3:
            print(f"{name=}")
            url = self._url_from_search(name)
            print(f"{name=} -> wiki {url=}")
            newurl = url.replace(" ", "+")
            print(newurl)
    
            response = requests.get(newurl)
            if b"may refer to" in response.content:
              conv = HtmlToDiscord(response.content.decode())
              links = conv.doc.select('ul > li a[title]')
              print(links)
              rel_url = links[0].attrs["href"]
              url = HtmlToDiscord.abs_url(conv.url, rel_url)
              response = requests.get(url)
              break
            else:
              break
        html = response.content
        odx = html.find(b"mf-section-0")
        if odx != -1:
            html = html[0 : odx + 8000]
        
        conv = HtmlToDiscord(html)
        
        paras = conv.doc.select(
            "#mf-section-0 > p:not(.mw-empty-elt)"
        )
        if not paras:
            paras = conv.doc.select("p:not(.mw-empty-elt)")
        if not paras:
            paras = [conv.doc]
        para = paras[0]
        conv.to_discord(para)
        embed = Embed(
            title=conv.title,
            color=0xFFFFFF,
            description=para.text,
            url=conv.url,
        )
        embed.set_footer(
            text="wikipedia",
            icon_url="https://upload.wikimedia.org/wikipedia"
                "/commons/thumb/2/2c"
                "/Tango_style_Wikipedia_Icon.svg"
                "/1200px-Tango_style_Wikipedia_Icon.svg.png",
        ) # icon can be the icon of wikipedia
        if conv.thumbnail: # this sets image
            embed.set_thumbnail(url=conv.thumbnail)
        return embed


