"""
模块名：`DataType`

为序列器提供一些基本数据类型以便解析。

使用方式：
    `from DataType import *`

包含类型：
    - `BYTE`: 1字节的无符号数
    - `WORD`: 2字节的无符号数
    - `DWORD`: 4字节的无符号数
    - `QWORD`: 8字节的无符号数
    - `CHAR`: 1字节的有符号数
    - `SHORT`: 2字节的有符号数
    - `LONG`: 4字节的有符号数
    - `LLONG`: 8字节的有符号数
    - `DATA`: n字节的字节流
    - `ARRAY`: n大小的type类型数组
"""
from typing import NewType

BYTE = NewType('BYTE', int)
WORD = NewType('WORD', int)
DWORD = NewType('DWORD', int)
QWORD = NewType('QWORD', int)
CHAR = NewType('CHAR', int)
SHORT = NewType('SHORT', int)
LONG = NewType('LONG', int)
LLONG = NewType('LLONG', int)


def DATA(n: int = 1):
    """
    字节流数据

    参数：
        - n: 数据大小，负数代表所有
    返回值：
        对应数据大小的类型
    """
    t = NewType('DATA', bytes)
    t.n = n
    return t


def ARRAY(_type: object, n: int):
    """
    定类型数组

    参数：
        - _type: 定类型
        - n: 数组大小，负数代表循环读取
    返回值：
        对应数据大小的类型
    """
    t = NewType('ARRAY', list)
    t.type = _type
    t.n = n
    return t


BASIC_TYPE_SIZE = {
    BYTE.__name__: 1,
    WORD.__name__: 2,
    DWORD.__name__: 4,
    QWORD.__name__: 8,
    CHAR.__name__: 1,
    SHORT.__name__: 2,
    LONG.__name__: 4,
    LLONG.__name__: 8,
}
"""
基本类型的大小字典
"""

DATA_TYPE_NAMES = (
    BYTE.__name__,
    WORD.__name__,
    DWORD.__name__,
    QWORD.__name__,
    CHAR.__name__,
    SHORT.__name__,
    LONG.__name__,
    LLONG.__name__,
    DATA.__name__,
    ARRAY.__name__,
)
"""
`DataType`中所有类型的名字
"""

BIG_ENDIAN = 'big'
"""
大端序

用法：
`__endian__: BIG_ENDIAN`
"""
LITTLE_ENDIAN = 'little'
"""
小端序

用法：
`__endian__: LITTLE_ENDIAN`
"""
