"""
模块名：`Serializer`

序列器类，所有自定义序列器都需要继承其中定义的`Serializer`。

使用方式：
    `from Serializer import Serializer`

包含类：
    - `Serializer`: 序列器基类
    - `DefaultSerializer`: 默认序列器

包含方法：
    - `arg_parse`: 参数解析
    - `arg_dump`: 参数写入
    - `serializer_size`: 获取序列器大小
"""
import logging
from .DataType import *
from .FileStream import FileReader, FileWriter


check_logger = logging.getLogger('check_logger')
"""
Serializer的check函数使用的logger
"""


def arg_parse(arg_type, stream: FileReader):
    """
    给定参数类型，从`FileReader`中解析数据。如果类型无法解析那么抛出异常`AttributeError`。

    参数：
        - arg_type: 参数类型，例如`int`
        - stream: `FileReader`

    返回值：
        从`FileReader`中提取到的参数，然后返回结果
    """
    arg_result = None
    # 如果是自定义的`Serializer`类型必然有`parse`方法
    if hasattr(arg_type, 'parse'):
        arg_result = getattr(arg_type, 'parse')(stream)
    elif arg_type.__name__ == ARRAY.__name__:
        array_type = getattr(arg_type, 'type')   # 数组的元素类型
        array_n = getattr(arg_type, 'n')      # 数组的元素个数
        arg_result = []
        # 这里需要考虑array_n<0的情况，此时需要死循环直到stream无输出
        # 循环获取数组元素
        if array_n < 0:
            while not stream.peek(1):
                arg_result.append(arg_parse(array_type, stream))
        else:
            for _ in range(array_n):
                arg_result.append(arg_parse(array_type, stream))
    elif arg_type.__name__ == DATA.__name__:
        data_n = getattr(arg_type, 'n')       # 数据的个数
        # 如果`DATA`的数据个数小于零，那么读取剩下的所有数据
        if data_n < 0:
            data_n = -1
        arg_result = stream.DATA(data_n)
    # 基本类型的处理
    elif arg_type.__name__ == BYTE.__name__:
        arg_result = stream.BYTE()
    elif arg_type.__name__ == WORD.__name__:
        arg_result = stream.WORD()
    elif arg_type.__name__ == DWORD.__name__:
        arg_result = stream.DWORD()
    elif arg_type.__name__ == QWORD.__name__:
        arg_result = stream.QWORD()
    elif arg_type.__name__ == CHAR.__name__:
        arg_result = stream.CHAR()
    elif arg_type.__name__ == SHORT.__name__:
        arg_result = stream.SHORT()
    elif arg_type.__name__ == LONG.__name__:
        arg_result = stream.LONG()
    elif arg_type.__name__ == LLONG.__name__:
        arg_result = stream.LLONG()
    else:
        # 对于未知类型抛出异常
        raise AttributeError(f'未知类型：{arg_type}')
    return arg_result


def arg_dump(arg_value, arg_type, stream: FileWriter):
    """
    给定参数和参数类型，往`FileWriter`中写入数据。如果类型无法写入那么抛出异常`AttributeError`。

    参数:
        - arg_value: 参数，例如5
        - arg_type: 参数类型，例如`int`
        - stream: `FileWriter`

    返回值：
        无
    """
    # 如果是自定义的`Serializer`类型必然有`dump`方法
    if hasattr(arg_value, 'dump'):
        getattr(arg_value, 'dump')(stream)
    elif arg_type.__name__ == ARRAY.__name__:
        array_type = getattr(arg_type, 'type')   # 数组的元素类型
        array_n = getattr(arg_type, 'n')      # 数组的元素个数
        # 这里不需要考虑array_n<0的情况
        # 循环获取数组元素
        for array_element in arg_value:
            # 循环写入数组元素
            arg_dump(array_element, array_type, stream)
    elif arg_type.__name__ == DATA.__name__:
        data_n = getattr(arg_type, 'n')       # 数据的个数
        stream.DATA(arg_value)
    # 基本类型的处理
    elif arg_type.__name__ == BYTE.__name__:
        stream.BYTE(arg_value)
    elif arg_type.__name__ == WORD.__name__:
        stream.WORD(arg_value)
    elif arg_type.__name__ == DWORD.__name__:
        stream.DWORD(arg_value)
    elif arg_type.__name__ == QWORD.__name__:
        stream.QWORD(arg_value)
    elif arg_type.__name__ == CHAR.__name__:
        stream.CHAR(arg_value)
    elif arg_type.__name__ == SHORT.__name__:
        stream.SHORT(arg_value)
    elif arg_type.__name__ == LONG.__name__:
        stream.LONG(arg_value)
    elif arg_type.__name__ == LLONG.__name__:
        stream.LLONG(arg_value)
    else:
        # 对于未知类型抛出异常
        raise AttributeError(f'未知类型：{arg_type}')


class MetaSerializer(type):
    ROUGH_INSPECTED_TYPES = (
        BYTE.__name__,
        WORD.__name__,
        DWORD.__name__,
        QWORD.__name__,
        CHAR.__name__,
        SHORT.__name__,
        LONG.__name__,
        LLONG.__name__,
        DATA.__name__,
    )

    def __new__(cls, name, bases, attrs):
        if '__annotations__' in attrs:
            # 检查注解是否合理可解析
            annotations = attrs['__annotations__']
            for attr_name, attr_type in annotations.items():
                # 检查端序范围
                if attr_name == '__endian__':
                    if attr_type in (BIG_ENDIAN, LITTLE_ENDIAN):
                        continue
                    else:
                        raise AttributeError(
                            "`__endian__`注解必须是`BIG_ENDIAN`或`LITTLE_ENDIAN`")
                # 检查注解范围
                # 对于一些基本类型的检查
                if attr_type.__name__ in MetaSerializer.ROUGH_INSPECTED_TYPES:
                    continue
                # 对于数组类型的检查，需要检查数组内置的类型
                elif attr_type.__name__ == ARRAY.__name__:
                    array_type = getattr(attr_type, 'type')
                    # 数组内置的类型是基本类型
                    if array_type in MetaSerializer.ROUGH_INSPECTED_TYPES:
                        continue
                    # 或者是一个Serializer
                    elif issubclass(array_type, Serializer):
                        continue
                    raise AttributeError(
                        f'{name}.{attr_name}注解必须是DataType或是一个Serializer的数组')
                # 检查是否是一个Serializer
                elif issubclass(attr_type, Serializer):
                    continue
                else:
                    raise AttributeError(
                        f'{name}.{attr_name}注解必须是DataType的类型或是一个Serializer')
        return super().__new__(cls, name, bases, attrs)


class Serializer(metaclass=MetaSerializer):
    """
    解析器基类`Serializer`，所有解析器都需要继承它，实现了基本的`parse`功能和`dump`功能，默认的`__repr__`。

    如果需要写一个自己的解析器，需要继承它，然后通过注解描述解析格式，例如
    ```python
    class ExampleSerializer(Serializer):
       signature: DATA(5)
       size: DWORD 
    ```
    将会自动检测模板格式是否合理。
    """
    PLACEHOLDER = ('__endian__')
    """
    Serializer中可能出现的占位符
    """

    @classmethod
    def parse(cls, stream: FileReader):
        """
        根据注解内容解析文件格式

        参数：
            - cls: 模板
            - stream: `FileReader`
        返回值：
            文件解析结果
        """
        # 记录之前的字节序，因为可能会被修改
        old_byteorder = stream.byteorder
        obj = cls()
        for attr_name, attr_type in cls.__annotations__.items():
            # 动态调整端序
            if attr_name == '__endian__':
                if attr_type == BIG_ENDIAN:
                    stream.endian('big')
                elif attr_type == LITTLE_ENDIAN:
                    stream.endian('little')
                else:
                    # MetaSerializer将会执行检察
                    ...
                continue
            attr_value = arg_parse(attr_type, stream)
            setattr(obj, attr_name, attr_value)
        # 修改回原始字节序
        stream.endian(old_byteorder)
        return obj

    def dump(self, stream: FileWriter):
        """
        根据注解内容写入文件数据

        参数：
            - stream: `FileWriter`
        """
        # 记录之前的字节序，因为可能会被修改
        old_byteorder = stream.byteorder
        for attr_name, attr_type in self.__annotations__.items():
            # 动态调整端序
            if attr_name == '__endian__':
                if attr_type == BIG_ENDIAN:
                    stream.endian('big')
                elif attr_type == LITTLE_ENDIAN:
                    stream.endian('little')
                else:
                    # MetaSerializer将会执行检察
                    ...
                continue
            attr_value = getattr(self, attr_name)
            arg_dump(attr_value, attr_type, stream)
        # 修改回原始字节序
        stream.endian(old_byteorder)

    def check(self) -> bool:
        """
        检查函数，用于实现自检查

        返回值：
            是否通过检查
        """
        return True

    def __repr__(self):
        attr_reprs = []
        for attr_name in self.__annotations__.keys():
            if attr_name in self.PLACEHOLDER:
                continue
            attr_repr_str = repr(getattr(self, attr_name))
            attr_reprs.append(f'{attr_name}={attr_repr_str}')
        repr_str = f"{self.__class__.__name__}{{{', '.join(attr_reprs)}}}"
        return repr_str


def serializer_size(cls):
    """
    根据`class`注解计算该模板需要解析的数据大小。
    需要注意如果模板注解中存在可变大小类型`DATA(-1)`, `ARRAY(type, -1)`，大小为负时会以0计入。

    参数：
        - cls: `Serializer`模板类
    返回值：
        该模板类注解的大小
    """
    if cls.__name__ in BASIC_TYPE_SIZE:
        return BASIC_TYPE_SIZE[cls.__name__]
    elif cls.__name__ == DATA.__name__:
        data_n = getattr(cls, 'n')          # 数组的元素个数
        if data_n < 0:
            return 0
        return data_n
    elif cls.__name__ == ARRAY.__name__:
        array_type = getattr(cls, 'type')   # 数组的元素类型
        array_n = getattr(cls, 'n')         # 数组的元素个数
        if array_n < 0:
            return 0
        return serializer_size(array_type) * array_n
    elif not hasattr(cls, '__annotations__'):
        # 忽略无注解的解析器
        return 0
    total_size = 0
    for attr_type in cls.__annotations__.values():
        total_size += serializer_size(attr_type)
    return total_size


class DefaultSerializer(Serializer):
    """
    默认的`Parser`类
    """
    data: DATA(-1)
