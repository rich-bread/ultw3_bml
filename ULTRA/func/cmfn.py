import json

class CommonFunc():
    def __init__(self) -> None:
        pass
    
    #送信用データ作成
    def create_postdata(self, name:str, org_data:list, **kwargs) -> dict:
        j = open(f'ULTRA/data/db_{name}.json','r',encoding='utf-8')
        udj = json.load(j)
        pd = dict()
        for i,u in enumerate(udj):
            if i == 0: continue
            try: d = kwargs[u]
            except: pd[u] = org_data[udj[u]]
            else:
                if d == None: pd[u] = org_data[udj[u]]
                else: pd[u] = d
        return pd
    
    #チームの平均XP計算
    def cal_averagexp(self, *xp:int):
        xpld = sorted(xp, reverse=True) #XP降順リスト
        xpavg = int(sum(xpld[:4])/len(xpld[:4])) #平均XP算出
        return xpavg
    