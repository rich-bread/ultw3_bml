import datetime

class TimeModule():
    def __init__(self) -> None:
        self.format = r'%Y/%m/%d %H:%M:%S'

    def dt2str(self, dt:datetime.datetime) -> str:
        tstr = dt.strftime(self.format)
        return tstr

    def str2dt(self, tstr:str) -> datetime.datetime:
        dt = datetime.datetime.strptime(tstr, self.format)
        return dt
    
    def change_timezone(self, dt:datetime.datetime) -> datetime.datetime:
        ndt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        return ndt