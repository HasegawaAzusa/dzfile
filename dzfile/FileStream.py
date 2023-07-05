"""
模块名：`FileStream`

为序列器提供输入输出文件流接口。

使用方式：
    `from FileStream import FileReader, FileWriter`

包含类：
    - `FileReader`: 输入文件流
    - `FileWriter`: 输出文件流
"""
from .DataType import *
from typing import Literal


class FileReader:
    """
    输入文件流
    """

    def __init__(self, filename: str, byteorder: Literal['little', 'big'] = 'little'):
        assert byteorder in ('little', 'big'), "端序必须是'little'或者'big'"
        self.file = open(filename, 'rb')
        self.byteorder = byteorder

    def BYTE(self) -> BYTE:
        """
        获取无符号一字节整数
        """
        return int.from_bytes(self.file.read(1), self.byteorder)

    def WORD(self) -> WORD:
        """
        获取无符号两字节整数
        """
        return int.from_bytes(self.file.read(2), self.byteorder)

    def DWORD(self) -> DWORD:
        """
        获取无符号四字节整数
        """
        return int.from_bytes(self.file.read(4), self.byteorder)

    def QWORD(self) -> QWORD:
        """
        获取无符号八字节整数
        """
        return int.from_bytes(self.file.read(8), self.byteorder)

    def CHAR(self) -> CHAR:
        """
        获取有符号一字节整数
        """
        return int.from_bytes(self.file.read(1), self.byteorder, signed=True)

    def SHORT(self) -> SHORT:
        """
        获取有符号两字节整数
        """
        return int.from_bytes(self.file.read(2), self.byteorder, signed=True)

    def LONG(self) -> LONG:
        """
        获取有符号四字节整数
        """
        return int.from_bytes(self.file.read(4), self.byteorder, signed=True)

    def LLONG(self) -> LLONG:
        """
        获取有符号八字节整数
        """
        return int.from_bytes(self.file.read(8), self.byteorder, signed=True)

    def DATA(self, n: int = 1) -> DATA:
        """
        获取n个字节
        """
        return self.file.read(n)
    
    def endian(self, byteorder: Literal['little', 'big']):
        """
        修改文件流读入的端序
        """
        assert byteorder in ('little', 'big'), "端序必须是'little'或者'big'"
        self.byteorder = byteorder

    def seek(self, _offset: int):
        self.file.seek(_offset)
    
    def peek(self, __size: int = 0):
        return self.file.peek(__size)

    def tell(self):
        return self.file.tell()

    def close(self):
        self.file.close()

    def __del__(self):
        self.close()


class FileWriter:
    """
    输出文件流
    """

    def __init__(self, filename: str, byteorder: Literal['little', 'big'] = 'little'):
        assert byteorder in ('little', 'big'), "端序必须是'little'或者'big'"
        self.file = open(filename, 'wb')
        self.byteorder = byteorder

    def BYTE(self, data: int) -> BYTE:
        """
        写入无符号一字节整数
        """
        self.file.write(int(data).to_bytes(1, self.byteorder))

    def WORD(self, data: int) -> WORD:
        """
        写入无符号两字节整数
        """
        self.file.write(int(data).to_bytes(2, self.byteorder))

    def DWORD(self, data: int) -> DWORD:
        """
        写入无符号四字节整数
        """
        self.file.write(int(data).to_bytes(4, self.byteorder))

    def QWORD(self, data: int) -> QWORD:
        """
        写入无符号八字节整数
        """
        self.file.write(int(data).to_bytes(8, self.byteorder))

    def CHAR(self, data: int) -> CHAR:
        """
        写入有符号一字节整数
        """
        self.file.write(int(data).to_bytes(1, self.byteorder, signed=True))

    def SHORT(self, data: int) -> SHORT:
        """
        写入有符号两字节整数
        """
        self.file.write(int(data).to_bytes(2, self.byteorder, signed=True))

    def LONG(self, data: int) -> LONG:
        """
        写入有符号四字节整数
        """
        self.file.write(int(data).to_bytes(4, self.byteorder, signed=True))

    def LLONG(self, data: int) -> LLONG:
        """
        写入有符号八字节整数
        """
        self.file.write(int(data).to_bytes(8, self.byteorder, signed=True))

    def DATA(self, data: bytes) -> DATA:
        """
        写入数据`data`
        """
        self.file.write(data)

    def endian(self, byteorder: Literal['little', 'big']):
        """
        修改文件流写入的端序
        """
        assert byteorder in ('little', 'big'), "端序必须是'little'或者'big'"
        self.byteorder = byteorder

    def seek(self, _offset: int):
        self.file.seek(_offset)

    def close(self):
        self.file.close()

    def __del__(self):
        self.close()
