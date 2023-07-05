from .Common import *
import time


class BaseTime(Serializer):
    def get_time_tuple(self):
        return time.localtime(self.timestamp)

    def __repr__(self):
        time_tuple = self.get_time_tuple()
        date_str = f'{time_tuple.tm_year}/{time_tuple.tm_mon}/{time_tuple.tm_mday}'
        time_str = f'{time_tuple.tm_hour}:{time_tuple.tm_min}:{time_tuple.tm_sec}'
        return f'{self.__class__.__name__}{{{date_str} {time_str}}}'


class Time64(BaseTime):
    timestamp: QWORD


class Time32(BaseTime):
    timestamp: DWORD
