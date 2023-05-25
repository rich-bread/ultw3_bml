import json

class TeamFunc():
    def __init__(self) -> None:
        pass

    #チームの平均XP計算
    def cal_averagexp(self, *xp:int):
        xpld = sorted(xp, reverse=True) #XP降順リスト
        xpavg = int(sum(xpld[:4])/len(xpld[:4])) #平均XP算出
        return xpavg
    
    #指定リーグへの参加確認
    def check_league_entry(self, league:str, xpavg:int) -> bool:
        j = open(f'ULTRA/data/league.json','r',encoding='utf-8')
        lgj = json.load(j)
        if lgj[league] < xpavg: b = False
        else: b = True
        return b