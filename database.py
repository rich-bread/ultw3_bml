import os
import io
import json
import requests
import aiohttp
import discord
from typing import Union

class Database():
    def __init__(self) -> None:
        self.url = os.getenv('GAS_PROJECT_URL')+'?'

    #DBへのPOST処理
    async def post_db(self, name:str, data:dict, **kwargs) -> requests.Response:
        base = {'name':name}
        payload = base|kwargs
        response = requests.post(url=self.url, params=payload, data=json.dumps(data))
        return response
    
    #DBへのGET処理
    async def get_db(self, name:str, **kwargs) -> Union[dict,list]:
        base = {'name':name}
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url, params=base|kwargs) as response:
                resj = await response.json()
                return resj
            
    
class DiscordDatabase():
    def __init__(self) -> None:
        pass

    async def post_image(self, channel:discord.TextChannel, image:discord.Attachment, filename:str, content:str=None) -> str:
        imgby = await image.read() #bytes型でファイルを取得
        imgbyio = io.BytesIO(imgby) #BytesIO型に変換
        file = discord.File(fp=imgbyio, filename=filename) #discord.File型で添付ファイルを作成
        message = await channel.send(content=content,file=file) #添付ファイルを送信
        url = message.attachments[0].url #discord.Messageのattachmentsから先頭の添付ファイルのURLを取得
        return url