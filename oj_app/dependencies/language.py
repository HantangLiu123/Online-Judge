import asyncio
import aiofiles
import json
import os
from fastapi import Request

async def get_language(path: str) -> dict:

    """get the language config according to the path"""

    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
    language = json.loads(content)
    return language

async def init_language() -> dict[str, dict]:

    """init language settings according to jsons in the languages folder"""

    LANGUAGE_FOLDER = os.path.join(os.curdir, 'languages')
    lan_files = os.listdir(LANGUAGE_FOLDER)
    get_lan_tasks = [get_language(os.path.join(LANGUAGE_FOLDER, file)) for file in lan_files]
    lan_dicts = await asyncio.gather(*get_lan_tasks)
    lan_names = [language['name'] for language in lan_dicts]
    languages = dict(zip(lan_names, lan_dicts))
    return languages

def update_language(lan_info: dict, request: Request):

    """update the language to the app.state"""

    lan_name = lan_info['name']
    request.app.state.languages[lan_name] = lan_info
