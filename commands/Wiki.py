from base import *
import bs4, re, requests
from bs4 import BeautifulSoup as BS, Tag, TemplateString
from bs4.builder import FAST, HTMLParserTreeBuilder
from functools import lru_cache
from typing import Any, Optional, Union
from urllib.parse import ParseResult, urljoin, urlparse, quote
from requests import get
from itertools import starmap
from typing import NamedTuple
from furl import furl as URL
from enum import Enum
from typing import Callable, TypeVar

TFunc = TypeVar("TFunc", bound=Callable)

def cache(func: TFunc) -> TFunc:
    return lru_cache(maxsize=0)(func)


class WikiProfile(Enum):
    """
    Search profile to use. 
      - `STRICT`: Strict profile with few punctuation
        characters removed but diacritics and stress marks
        are kept.
      - `NORMAL`: Few punctuation characters, some diacritics
        and stopwords removed.
      - `FUZZY`: Similar to normal with
        typo correction (two typos supported).
      - `FAST-FUZZY`: Experimental fuzzy profile (may be
        removed at any time)
      - `CLASSIC`: Classic prefix, few punctuation characters
        and some diacritics removed.
      - `ENGINE_AUTOSELECT`: Let the search engine decide on
        the best profile to use.
    Source: <http://wikipedia.org
            /w/api.php?action=help&modules=opensearch>
    """
    STRICT = "strict"
    NORMAL = "normal"
    FAST_FUZZY = "fast-fuzzy"
    CLASSIC = "classic"
    ENGINE_AUTOSELECT = "engine_autoselect"
    FUZZY = "fuzzy"
    
class WikiRedirectMode(Enum):
    """
    How to handle redirects.
      - `RETURN` - Return the redirect itself.
      - `RESOLVE` - Return the target page. May return fewer
         than limit results.
    """
    RETURN = "return"
    RESOLVE = "resolve"
    
class WikiSearchResult(NamedTuple):
    title: str
    url: URL

class WikiImageResult(NamedTuple):
    pageid: str
    ns: int
    title: str
    images: list[dict[str,Union[int,str]]]
    image_title: str
    href: URL
    scheme: str
    filename: str

@cache
def search_wiki(
    query: str,
    *,
    profile: WikiProfile=WikiProfile.NORMAL,
    redirects: WikiRedirectMode=WikiRedirectMode.RESOLVE,
    max_results: int=10,
) -> list[WikiSearchResult]:
    wiki_api_url: URL = URL(
        "http://en.wikipedia.org/w/api.php"
    )
    resp = get(
        wiki_api_url.url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; "
            "WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " 
            "Chrome/33.0.1750.154 Safari/537.36",
            "Referer": wiki_api_url.url,
            "Accept": "application/json",
        },
        params=dict(
            action="opensearch",
            format="json",
            limit=max_results,
            profile=profile.value,
            redirects=redirects.value,
            search=query,
        ),
    )
    if resp.status_code != 200:
        raise Exception()
    
    return [
        *starmap(
            lambda title, url: 
                WikiSearchResult(title, URL(url)),
            zip(*resp.json()[1::2]),
        )
    ]

@cache
def get_wiki_images(
    result: WikiSearchResult,
    *,
    min_results: int=1,
) -> list[WikiImageResult]:
    wiki_api_url: URL = URL(
        "http://en.wikipedia.org/w/api.php"
    )
    resp = get(
        wiki_api_url.url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; "
            "WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " 
            "Chrome/33.0.1750.154 Safari/537.36",
            "Referer": wiki_api_url.url,
            "Accept": "application/json",
        },
        params=dict(
            action="query",
            format="json",
            prop="images",
            titles=result.title,
        ),
    )
    if resp.status_code != 200:
        raise Exception()
    im_results = []

    for pid, page in resp.json()["query"]["pages"].items():
        pageid = page["pageid"]
        page_title = page["title"]
        del page["ns"]
        images: list[dict[str,Union[int,str]]] = (
            page["images"]
        )
        for image in images:
            ns = image["ns"]
            im_title = image["title"]
            del image["title"]
            scheme, _, filename = im_title.partition(":")
            href = None
            if scheme == "File":
                file_info_url = URL(
                    f"http://commons.wikimedia.org"
                    f"/wiki/{im_title}"
                )
                doc = BS(requests.get(file_info_url).content)
                for anchor in doc.select(
                  "div.fullMedia "
                  "a[href*=\"{filename}\"], "
                  "div.fullMedia "
                  "a[href*=\"{quote(filename)}\"], "
                  "div.fullMedia "
                  "a.internal[href]"
                ):
                    href = URL(anchor.attrs.get("href"))
                    break
            if href:
                im_results.append(
                    WikiImageResult(
                        **image,
                        **page,
                        image_title=im_title,
                        href=href,
                        scheme=scheme,
                        filename=filename,
                    )
                )
                if len(im_results) >= min_results:
                    break
    return im_results



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
    
    def _do_wiki(self, name) -> Embed:
        results: WikiSearchResult = search_wiki(name)
        if not results:
            return Embed(
                description=f"No results found for {name!r}"
            )
        best = [r for r in results if re.subn("[^a-z]+", "", r.title.split("(")[0].strip().lower())[0] == re.subn("[^a-z]+", "", name.split("(")[0].strip().lower())[0]]
        if best:
            result = best[0]
        else:
            result = results[0]
        title, url = result.title, result.url
        response = requests.get(url.url)
    
        if b"may refer to" in response.content:
          conv = HtmlToDiscord(response.content.decode())
          links = conv.doc.select('ul > li a[title]')
          rel_url = links[0].attrs["href"]
          url = HtmlToDiscord.abs_url(conv.url, rel_url)
          title = links[0].text.strip()
          response = requests.get(url)
        
        html = response.content
        odx = html.find(b"mf-section-0")
        if odx != -1:
            html = html[0 : odx + 3000]
        
        images = get_wiki_images(result)
        if images:
            thumbnail = images[0].href.url
        else:
            thumbnail =  (
                "https://upload.wikimedia.org"
                "/wikipedia/commons/thumb/d/de"
                "/Wikipedia_Logo_1.0.png"
                "/768px-Wikipedia_Logo_1.0.png"
            )
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
        embed.set_thumbnail(url=thumbnail)
        return embed

