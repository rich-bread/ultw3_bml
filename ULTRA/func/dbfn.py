import requests
import discord
import database
from typing import Union

class DatabaseFunc():
    def __init__(self) -> None:
        self.db = database.Database()
        self.dcdb = database.DiscordDatabase()

    #指定ユーザの情報取得
    async def get_userdata(self, user_id:Union[int,str]) -> list:
        ud = await self.db.get_db(name='read', table='user-master', column='discord_id', record=str(user_id))
        return ud
    
    #指定チームの情報取得
    async def get_teamdata(self, leader_id:Union[int,str]) -> list:
        td = await self.db.get_db(name='read', table='team-master', column='leader', record=str(leader_id))
        return td
    
    #指定ユーザの情報送信
    async def post_userdata(self, user_id:Union[int,str], post_data:dict, is_update:bool) -> requests.Response:
        r = await self.db.post_db(name='write', data=post_data, table='user-master', column='discord_id', record=str(user_id), is_update=is_update)
        return r

    #指定チームの情報送信
    async def post_teamdata(self, leader_id:Union[int,str], post_data:dict, is_update:bool) -> requests.Response:
        r = await self.db.post_db(name='write', data=post_data, table='team-master', column='leader', record=str(leader_id), is_update=is_update)
        return r
    
    #受付期間中シーズンの情報取得
    async def get_valid_season_data(self) -> list:
        sd = await self.db.get_db(name='get_seasondata', period='entry')
        return sd
    
    #受付期間中大会の情報取得 ※※非常設※※
    async def get_valid_tournament_data(self) -> list:
        td = await self.db.get_db(name='get_tournament_data', period='entry')
        return td
    
    #指定情報のログ作成
    def create_logdata(self, author_id:Union[int,str], post_data:dict, is_update:bool) -> dict:
        del post_data["created_at"]
        add_data = {"updated_by": str(author_id), "is_update": is_update}
        log_data = post_data|add_data
        return log_data
    
    #指定ユーザ情報をログ
    async def log_userdata(self, author_id:Union[int,str], post_data:dict, is_update:bool) -> requests.Response:
        log_data = self.create_logdata(author_id, post_data, is_update)
        r = await self.db.post_db(name='log', data=log_data, table='user-log')
        return r

    #指定チーム情報をログ
    async def log_teamdata(self, author_id:Union[int,str], post_data:dict, is_update:bool) -> requests.Response:
        log_data = self.create_logdata(author_id, post_data, is_update)
        r = await self.db.post_db(name='log', data=log_data, table='team-log')
        return r
    
    #シーズン参加申請をログ
    async def log_entry_season(self, entered_at:str, author_id:Union[int,str], season_name:str, season_id:str, team_name:str) -> requests.Response:
        log_data = {"entered_at":entered_at, "entered_by":str(author_id), "season_name":season_name, "season_id":season_id, "team_name":team_name}
        r = await self.db.post_db(name='log', data=log_data, table='entry-log')
        return r

    #ドラフト大会参加申請をログ ※※非常設※※
    async def log_entry_draft(self, entered_at:str, tournament_name:str, tournament_id:str, user_name:str, author_id:Union[int,str]) -> requests.Response:
        log_data = {"entered_at":entered_at, "tournament_name":tournament_name, "tournament_id":tournament_id, "user_name":user_name, "discord_id":str(author_id)}
        r = await self.db.post_db(name='log', data=log_data, table='draft-log')
        return r

    #ウデマエ画像を投稿
    async def post_xpimage(self, channel:discord.TextChannel, user:discord.Member, image:discord.Attachment):
        url = await self.dcdb.post_image(channel, image, image.filename, user.mention)
        return url
