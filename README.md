# DZFILE

## 简介

很鸡肋的一个文件格式解析 Python 包，可以自定义解析器模板。

简单的一个入门用法：

```python
import dzfile

filename = './test/30755992.bmp'
bmp = dzfile.parse(filename)
print(bmp)
```

它将解析出 Bitmap 中的文件格式。

> 但解析程度取决于所写的解析器模板。

目前 `dzfile.parse` 可以解析的后缀为

- `BMP` - Bitmap 图片文件格式的解析
- `ARIA2DHT` - ARIA2 中的 `dht.dat` 文件格式的解析
- ...



## 一些模块的简单介绍

### `DataType`

解析器模板支持的类型有

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

还有不在 `DataType` 库中的有

- `Time32`: 32位的时间类型，字符串输出为 `localtime`
- `Time64`: 64位的时间类型，字符串输出为 `localtime`

**支持嵌套序列器**。



### `FileStream`

为了方便文件读取而写的文件输入输出流接口类，包括

- `FileReader`: 文件输入类
- `FileWriter`: 文件输出类



### `Common`

`Common` 接口模块，方便导入编写解析器模板相关的内容。

一般用法为

```python
from dzfile.Common import *		# 包外导入
from .Common import *			# 包内导入
```

包含但不限于相关数据类型，`FileReader`，`FileWriter`，`Serializer`。



### `Serializer`

`Serializer` 是解析器基类，所有的解析器模板都需要继承它进行编写，它将对子类所写的注解进行检查，以保证 `parse` 和 `dump` 不会报错。

> 这里是使用了 `MetaSerializer` 作为元类，在 `__new__` 中写了检查逻辑。

`Serializer` 包含几个基本函数：

- `parse`: 用于自动化解析文件，传入 `FileReader`，是一个 `classmethod`
- `dump`: 将数据以模板给出的格式写入文件，传入 `FileWriter`
- `check`: 用于自检查，约定相关信息以 `warning` 形式输出到 `Serializer.check_logger`
- `__repr__`: 根据解析器注解生成相应的表示字符串

同时在包中还包含一些工具函数：

- `arg_parse(arg_type, stream: FileReader)`: 传入一个参数类型和文件流，从文件流中解析数据返回。
- `arg_dump(arg_value, arg_type, stream: FileWriter)`: 传入一个参数值、参数类型和文件流，参考参数类型将参数值写入文件流。
- `serializer_size`: 计算一个解析器模板的大小（需要的输入数据的大小），对于负可变大小的数据类型只会计算为 0。



### `dzfile`

这是主模块，主要包含一个全局变量和两个函数：

- `parse_handlers`: 全局变量，包含了各种可处理后缀对应的解析函数
- `register_parse_handler(file_extension: str, parse_handler: handler_type)`: 注册函数，用于注册后缀对应的解析函数
- `parse(file_path: str, file_extension: str = None)`: 解析函数，返回解析后结果，默认值是 `DefaultSerializer` 解析器的解析结果。



## 解析器的简单编写

### 文件格式描述

以 `Bitmap` 的文件头为例，应该如下表所示

| 字节大小 | 描述                   |
| -------- | ---------------------- |
| 2        | 文件类型（通常为“BM”） |
| 4        | 文件大小               |
| 2        | 保留字段 1             |
| 2        | 保留字段 2             |
| 4        | 图像数据偏移量         |

那么用解析器描述，应该如下代码所示

```python
from dzfile.Common import *

class BMPFileHeader(Serializer):
    """
    Bitmap文件格式的文件头
    """
    bfType: DATA(2)
    bfSize: DWORD
    bfReserved1: WORD
    bfReserved2: WORD
    bfOffBits: DWORD
```

这样就完成了一个新的解析器，可以试着尝试用来解析文件头。

```python
from dzfile import FileReader

filename = './test/30755992.bmp'
fs = FileReader(filename)
bf = BMPFileHeader.parse(fs)
print(bf)
```

可以发现打印出来的结果应该是

```python
BMPFileHeader{bfType=b'BM', bfSize=27254, bfReserved1=2448, bfReserved2=0, bfOffBits=54}
```

Bitmap 的文件头已经成功被解析。



### 字节序

有一些文件，可能是以大字节序格式记录的；而有一些文件，可能是即存在大字节序又存在小字节序，即混合字节序。

模板解析器**默认以小字节序**解析文件，如果想要改变字节序，在对应解析的部分以 `__endian__` 注解，例如

```python
from dzfile.Common import *

class DHTHeader(Serializer):
    __endian__: BIG_ENDIAN
    magic: DATA(2)
    format: BYTE
    reversed1: DATA(3)
    version: WORD
```

字节序仅允许描述为 `BIG_ENDIAN` 或 `LITTLE_ENDIAN`，如果不是这二者可能会被元类 `MetaSerializer` 检查出错误。

同时也可以中途改变字节序，例如

```python
from dzfile.Common import *

class DHTHeader(Serializer):
    __endian__: BIG_ENDIAN
    magic: DATA(2)
    format: BYTE
    __endian__: LITTLE_ENDIAN
    reversed1: DATA(3)
    __endian__: BIG_ENDIAN
    version: WORD
```



### 动态模板

一个可能的动态模板示例，并未展现全部代码

```python
# 计算填充
bytesPerLine = _infoHeader.biWidth * _infoHeader.biBitCount // 8
padding = 4 - (bytesPerLine % 4)

class BMPLine(Serializer):
    if _infoHeader.biBitCount < 8:
        imageData: DATA(bytesPerLine)
    elif _infoHeader.biBitCount == 8:
        colorIndex: DATA(_infoHeader.biWidth)
    elif _infoHeader.biBitCount == 24:
        colors: ARRAY(RGB, _infoHeader.biWidth)
    elif _infoHeader.biBitCount == 32:
        colors: ARRAY(RGBR, _infoHeader.biWidth)
    if (padding != 4):
        padBytes: DATA(padding)
class Bitmap(Serializer):
    fileHeader: BMPFileHeader
    infoHeader: BMPInfoHeader
    if unkown_size > 0:
        unkown: DATA(unkown_size)
    lines: ARRAY(BMPLine, abs(_infoHeader.biHeight))
```



## 未来展望

写这个包的目的主要是想利用 Python 的动态性来解决某些文件解析上的问题，但现在的问题在于解析器模板不具有很好的鲁棒性，数据类型太少，同时模板数太少。

希望在未来能够解决这些方面，将这个包变成较为优秀的包。







