"""
模块名：`dzfile`

提供解析功能的模块，可以通过注解描述一个文件结构。

作者：qingsiduzou
"""
from .Common import *
from typing import Callable, Any

handler_type = Callable[[FileReader], Any]
parse_handlers: dict[str, handler_type] = {}
"""
一组解析函数的回调处理器，用于根据文件的扩展名调用不同的解析函数来解析文件内容。
"""


def register_parse_handler(file_extension: str, parse_handler: handler_type):
    """
    注册解析函数，用于解析指定扩展名的文件，后缀名总会是大小写匹配。

    参数：
        - file_extension: 要注册的文件扩展名
        - parse_handler: 解析函数的回调处理器，用于解析该扩展名的文件内容

    返回值：
        无
    """
    global parse_handlers
    parse_handlers[file_extension.upper()] = parse_handler


def parse(file_path: str, file_extension: str = None):
    """
    根据文件的扩展名调用不同的解析函数来解析这个文件，后缀名是大小写匹配的

    参数：
        - file_path: 要解析的文件路径，包含扩展名
        - file_extension: 可以指定扩展名，大小写匹配

    返回值：
        无
    """
    if file_extension is None:
        # 获取文件扩展名
        file_extension = file_path.rsplit('.', 1)[-1]
    # 获取对应的解析函数回调处理器
    parse_handler = parse_handlers.get(
        file_extension.upper(), DefaultSerializer.parse)
    stream = FileReader(file_path)
    # 调用解析函数的回调处理器解析文件内容
    parse_result = parse_handler(stream)
    stream.close()
    return parse_result


# 初始化扩展序列器
from . import BMPSerializer
register_parse_handler('BMP', BMPSerializer.parse)
from . import DHTSerializer
register_parse_handler('ARIA2DHT', DHTSerializer.parse)
