import re
import json

class UserFunc():
    def __init__(self) -> None:
        pass

    #入力されたフレンドコード(SW)の確認
    def check_friendcode(self, friend_code:str) -> bool:
        r = re.search(r"^\d{4}-\d{4}-\d{4}$",friend_code)
        return bool(r)
    
    #入力されたTwitterIDの確認
    def check_twitterid(self, twitter_id:str) -> bool:
        r = re.search(r"^[0-9a-zA-Z_]{1,15}$",twitter_id)
        return bool(r)