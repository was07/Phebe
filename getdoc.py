import re
import requests
import functools
from init import Formatted
from itertools import islice
from typing import Optional, TypeVar
from sphobjinv.inventory import Inventory
from sphobjinv.data import DataObjStr
from bs4 import BeautifulSoup as BS
from bs4.element import Tag

inv: Inventory = Inventory("objects.inv")
HtmlStr = TypeVar("HtmlStr", bound = str)
Url = TypeVar("UrlStr", bound = str)

def getinv() -> Inventory:
    return inv

@functools.lru_cache(maxsize=0)
def gethtml(url: Url) -> str:
    # haha i know its so bad
    for i in range(0, 4):
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                raise SystemError(resp.status_code)
            return resp.content
        except SystemError:
            continue
    return ""

@functools.lru_cache(maxsize=0)
def getitem(symbol: str) -> Optional[DataObjStr]:
    inv = getinv()
    items = (o for o in inv.objects if symbol == o.name)
    for item in items: return item
    items = (
        o for o in inv.objects 
        if symbol in o.name.split(".")
    )
    for item in items: return item
    items = (
        o for o in inv.objects
        if symbol.split(".")[0] == o.name.split(".")[0]
    )
    for item in items: return item
    return None


def geturl(item: Optional[DataObjStr]) -> Optional[Url]:
    if not item:
        return None
    return (
        f"https://docs.python.org/3/{item.uri}#{item.name}"
    )

def getdoc(
    symbol: str,
    nparas: int=1
) -> tuple[str, Formatted, Url]:
    item: Optional[DataObjStr] = getitem(symbol)
    url: Optional[Url] = geturl(item)
    html: HtmlStr = gethtml(url) if url else None
    doc: BS = BS(html or "", features="html5lib")
    elems: list[Tag] = doc.select(f"[id=\"{item.name}\"]")
    if not elems:
        return (
            symbol,
            Formatted("", ["No documentation available"]),
            url
        )
    
    elem: Tag = elems[0]
    dt, dd = (
        elem.parent.select("dt")[0],
        elem.parent.select("dd")[0]
    )
    
    clean_text = (
        dt.text.replace("\xB6","").strip()
    ).replace("\x0A", "<nl>")
    fixed_part = f"```py\n{clean_text}```"
    
    # fixed-width text (inline code / identifiers)
    for fwe in dd.select("span.pre, tt"):
        fwe.replace_with(doc.new_string(
            "`{}`".format(fwe.text.strip())
        ))
    
    # remove excess spans
    for span in dd.select("span"):
        span.replace_with_children()
    
    # italicized text (parameter names)
    for eme in dd.select("em, .em, .i"):
        eme.replace_with(doc.new_string(
            "__**{}**__".format(eme.text.strip())
        ))
    
    # other code blocks
    for blk in dd.select("pre"):
        blk.replace_with(doc.new_string(
            "```py\x0A{}```".format(
                blk.text.strip()
            ).replace("\x0A", "<nl>")
        ))
    
    text = (
        "\n".join(e.text for e in dd.children)
    )
    paras = islice(
        text.split("\n\n\n\n"),
        0, nparas
    )
    formatted_paras = []
    for para in paras:
        para2 = re.subn(
            "\\s*\\n\\s*\\n", "<break>",
            para, re.DOTALL
        )[0]
        para3 = para2.replace("\x0A", " ")
        para4 = para3.replace("<break>", "\n\n")
        para5 = para4.replace("<nl>", "\x0A")
        
        formatted_paras.append(para5.strip())
    return (
        symbol,
        Formatted(
            fixed_part.replace("<nl>", "\x0A"),
            formatted_paras,
            elem
        ),
        url
  )
