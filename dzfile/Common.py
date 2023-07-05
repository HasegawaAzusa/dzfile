"""
模块名：`Common`

一些扩展序列器所需要的接口模块

使用方式：
    `from Common import *`
"""
from .DataType import *
from .FileStream import FileReader, FileWriter
from .Serializer import Serializer, DefaultSerializer, arg_parse, arg_dump, serializer_size
from .TimeType import Time64, Time32
