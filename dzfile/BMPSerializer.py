from .Common import *
from enum import IntEnum, unique


class BMPFileHeader(Serializer):
    """
    Bitmap文件格式的文件头
    """
    bfType: DATA(2)
    bfSize: DWORD
    bfReserved1: WORD
    bfReserved2: WORD
    bfOffBits: DWORD


class BMPInfoHeader(Serializer):
    """
    Bitmap文件格式的数据头
    """
    biSize: DWORD
    biWidth: LONG
    biHeight: LONG
    biPlanes: WORD
    biBitCount: WORD
    biCompression: DWORD
    biSizeImage: DWORD
    biXPelsPerMeter: LONG
    biYPelsPerMeter: LONG
    biClrUsed: DWORD
    biClrImportant: DWORD


class RGBR(Serializer):
    """
    RGB+保留字，可能是ALPHA
    """
    blue: BYTE
    green: BYTE
    red: BYTE
    reserved: BYTE


class RGB(Serializer):
    """
    RGB
    """
    blue: BYTE
    green: BYTE
    red: BYTE


@unique
class CompressionType(IntEnum):
    """
    压缩类型
    """
    BI_RGB = 0
    BI_RLE8 = 1
    BI_RLE4 = 2
    BI_BITFIELDS = 3
    BI_JPEG = 4
    BI_PNG = 5
    BI_ALPHABITFIELDS = 6


def parse(stream: FileReader):
    """
    解析Bitmap文件
    """
    start_pos = stream.tell()
    _fileHeader = BMPFileHeader.parse(stream)
    _infoHeader = BMPInfoHeader.parse(stream)
    unkown_size = _fileHeader.bfOffBits - \
        serializer_size(BMPFileHeader) - serializer_size(BMPInfoHeader)
    if _infoHeader.biCompression > 0:
        # 存在压缩，暂不作处理
        class Bitmap(Serializer):
            fileHeader: BMPFileHeader
            infoHeader: BMPInfoHeader
            if unkown_size > 0:
                unkown: DATA(unkown_size)
            if _infoHeader.biSizeImage > 0:
                rleData: DATA(_infoHeader.biSizeImage)
            else:
                rleData: DATA(_fileHeader.bfSize - _fileHeader.bfOffBits)
    else:
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
    stream.seek(start_pos)
    return Bitmap.parse(stream)
