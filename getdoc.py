import aiohttp
import asyncio
import nest_asyncio
nest_asyncio.apply()

import re
import requests
import functools
from itertools import islice
from typing import Optional, TypeVar
from init import Formatted
from sphobjinv.inventory import Inventory
from sphobjinv.data import DataObjStr
from bs4 import BeautifulSoup as BS
from bs4.element import Tag

HtmlStr = TypeVar("HtmlStr", bound = str)
Url = TypeVar("Url", bound = str)
invs = {}

async def get_all_invs():
  mapping = {
    "python": "https://docs.python.org/3/",
    "python-dev": "https://docs.python.org/dev/",
    "pyspark": "https://spark.apache.org/docs/latest/api/python/",
    "disnake": "https://docs.disnake.dev/en/latest/",
    "requests": "https://docs.python-requests.org/en/latest/",
    "requests-2": "http://requests.readthedocs.org/en/latest/",
    "numpy": "https://numpydoc.readthedocs.io/en/latest/",
    "dpy": "https://discordpy.readthedocs.org/en/latest/",
  }
  coros = [get_inv(url) for ns, url in mapping.items()]
  results = await asyncio.gather(*coros)
  return dict(results)

async def get_inv(url):
  print(f"Loading {url.rstrip('/')}/objects.inv")
  async with aiohttp.ClientSession() as session:
    async with session.get(f"{url.rstrip('/')}/objects.inv") as resp:
      inv = Inventory()
      inv._try_import(inv._import_zlib_bytes, await resp.read(), [])
      return (url, inv)

@functools.lru_cache(maxsize=0)
def getinv() -> Inventory:
  global invs
  if invs:
    return invs
  invs.update(asyncio.run(get_all_invs()))
  for url, inv in invs.items():
    lines = inv.data_file().splitlines()
    pts = [
       ln.replace(".$","").replace("-$","").split()
       for ln in map(bytes.decode, lines)
    ]
    lookup = {
        p[0]: DataObjStr(*[*p[:1], *p[1].split(":"), *(p[2:4] + [p[0]]), p[0]])
        for p in pts if len(p) > 1 and p[0] != "#"
    }
    lookup.update({ p.name: p for p in inv.objects })
    inv.objects.clear()
    inv.objects.extend(list(lookup.values()))
    invs[url] = inv
  return invs

@functools.lru_cache(maxsize=0)
def gethtml(url: Url) -> str:
    # haha i know its so bad
  for _ in range(4):
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
  for url, inv in getinv().items():
    items = (o for o in inv.objects if symbol == o.name)
    for item in items: return (url,item)
  
  for url, inv in getinv().items():
    items = (
        o for o in inv.objects
        if symbol.split(".")[0] == o.name.split(".")[0]
    )
    for item in items: return (url,item)
  
  for url, inv in getinv().items():
    items = (
        o for o in inv.objects 
        if symbol in o.name.split(".")
    )
    for item in items: return (url,item)
  return None,None


def geturl(url, item: Optional[DataObjStr]) -> Optional[Url]:
  if not item:
      return None
  uri = item.uri
  uri = uri.replace("-$","")
  uri = uri.replace("#$", "")
  uri = uri.replace(".$", "")
  uri = uri.strip("#").strip(".").strip("-")
  if item.name not in re.split("[^a-zA-Z_0-9]+", uri):
    uri = f"{uri}#{item.name}"

  print(repr(item))
  return (
      f"{url}/{uri}"
  )

def getdoc(
    symbol: str,
    nparas: int=1
) -> tuple[str, Formatted, Url]:
    url, item = getitem(symbol)
    url: Optional[Url] = geturl(url, item)
    id_or_href = item.uri.split("#")[-1].replace("$", item.name)
    html: HtmlStr = gethtml(url) if url else None
    doc: BS = BS(html or "")
    elems: list[Tag] = doc.select(f"[id=\"{id_or_href}\"], [href=\"#{id_or_href}\"]")
    if not elems:
        return (
            symbol,
            Formatted("", ["No documentation available"]),
            url
        )
    
    elem: Tag = elems[0]
    dt, dd = (
        elem.parent.select("dt, a.reference span.pre")[0],
        elem.parent.select("dd, a.reference")[0],
    )
    dd_text = dd.text
    dt_text = dt.text
    if dt_text in dd_text:
      dd_text = dd_text[len(dt_text):]
      dd = dt.parent.parent.parent.parent.parent
      
    clean_text = (
        dt_text.replace("\xB6","").strip()
    ).replace("\x0A", "<nl>")
    fixed_part = f"```py\n{clean_text}```"
    
    # fixed-width text (inline code / identifiers)
    for fwe in dd.select("span.pre, tt"):
        fwe.replace_with(doc.new_string(
            "`{}`".format(fwe.text.strip())
        ))

    # remove excess spann
    for span in dd.select("span"):
       pass #span.replace_with_children()
    
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
        "\n".join(e.text for e in (dd.children or dd))
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
        para5 = para4.replace("<nl>", "\x0A").replace("\xB6","").strip()
        
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
	
