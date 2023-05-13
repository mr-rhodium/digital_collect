
import json
import aiofiles
import aiohttp
import asyncio
from typing import AsyncIterator

URL = "https://www.digitalocean.com"
FILENEME = "subject.json"
HEADERS = {
    "Accept": "*/*",
}


class ParamData:
    en: str = "en"
    content: str = "tutorial"
    sort: str = "newest"
    range: str = "all"


class Param:
    def __init__(self, param_data: ParamData) -> None:
        self.param_data = param_data

    _search: str = "search?query="
    _content: str = "type="
    _lang: str = "language="
    _sort: str = "sort_by="
    _time: str = "time_range="
    _page: str = "page="
    _hits: str = "hits_per_page="
    _separator: str = "&"

    def search(self, name: str) -> str:
        return f"{self._search}{name}"

    def content(self) -> str:
        return f"{self._content}{self.param_data.content}"

    def lang(self) -> str:
        return f"{self._lang}{self.param_data.en}"

    def time(self) -> str:
        return f"{self._time}{self.param_data.range}"

    def hits(self, number: int) -> str:
        return f"{self._hits}{number}"

    def sort(self) -> str:
        return f"{self._sort}{self.param_data.sort}"

    def page(self, number: int) -> str:
        return f"{self._page}{number}"

    def hints(self, number: int) -> str:
        return f"{self._hits}{number}"

    @property
    def sep(self) -> str:
        return self._separator


async def get_url(url: str) -> list:
    conn = aiohttp.TCPConnector(limit=8, limit_per_host=8)
    async with aiohttp.ClientSession(connector=conn) as session:
        resp = await session.get(url=url, headers=HEADERS)
        return await resp.json()


async def total_page(content: dict) -> str | None:
    return content.get("total")


async def async_iterator(data: list) -> AsyncIterator[dict]:
    for item in data:
        yield item


async def wfile(data: list, filename: str) -> None:
    async with aiofiles.open(filename, mode="a") as fp:
        await fp.write(json.dumps(data))


async def main():
    subjects = []
    url_api = f"{URL}/api/static-content/v1/tags/"
    tegs = await get_url(url_api)
    prm = Param(ParamData)
    sep = prm.sep
    async for item in async_iterator(tegs):
        slug = item.get("slug")
        name = item.get("name")
        page_url = f"{URL}/api/static-content/v1/{prm.search(name)}{sep}{prm.content()}{sep}{prm.lang()}{sep}{prm.sort()}{sep}{prm.time()}{sep}{prm.page(1)}"
        page = await get_url(page_url)
        total = await total_page(page)
        if total:
            promt = f"{URL}/api/static-content/v1/{prm.search(name)}{sep}{prm.content()}{sep}{prm.lang()}{sep}{prm.sort()}{sep}{prm.time()}{sep}{prm.hints(total)}"
            print(promt)
            page = await get_url(promt)

            hits = page.get("hits")
            if hits:
                subjects.append({slug: hits})
    await wfile(subjects, FILENEME)


if __name__ == "__main__":
    asyncio.run(main())
