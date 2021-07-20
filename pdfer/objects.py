from pdfer import lib
from fontTools.ttLib import TTFont, sfnt
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

import zlib
import hashlib

class catalog_object():
    def __init__(self):
        self.dict = {"/Pages": None}

    def add_pages(self, pages):
        self.dict["/Pages"] = pages

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def __str__(self):
        text = "<</Type /Catalog\n"
        for i in self.dict:
            text += i.__str__() + " %%" + self.dict[i].ident() + "%%\n"
        text += f">>\n"
        return text


class pages_object():
    def __init__(self):
        self.pages = []

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def append(self, page):
        self.pages.append(page)

    def current(self):
        return self.pages[-1]

    def __str__(self):
        text = "<<\n/Type /Pages\n/Kids ["
        for i in self.pages:
            text += " %%" + i.ident() + "%%"
        text += f"]\n/Count {len(self.pages)}\n>>\n"
        return text


class outlines_object():
    def __init__(self):
        self.dict = []

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def __str__(self):
        text = "<</Type /Outline\n"
        for i in self.dict:
            text += i.__str__() + " %%" + self.dict[i].ident() + "%%\n"
        text += f">>\n"
        return text


class page_object():
    def __init__(self, font):
        self.text_objs = []
        self.font = font

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def append(self, text):
        self.text_objs.append(text)

    def __str__(self):
        text = "<<\n/Type /Page\n/Contents ["
        for i in self.text_objs:
            if type(i) is table_object:
                for obj in i.get_objs(self.font):
                    text += " %%" + obj.ident() + "%%"
            else:
                text += " %%" + i.ident() + "%%"
        text += f"]\n/MediaBox [ 0 0 612 792 ]\n/Resources <</Font << /F1 %%{self.font.ident()}%% >>\n>>\n>>\n"
        return text


class text_object():
    def __init__(self):
        self.stream = ""

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def append(self, text):
        self.stream += text

    def __str__(self):
        text = f"<< /Length {len(self.stream)}>>\n"
        text += f"stream\n{self.stream}\nendstream\n"
        return text

class table_object():
    def __init__(self, y, width, offset_x, offset_y, heading, ratio):
        self.data = []
        self.heading = []
        self.offset = [offset_x, offset_y]
        self.dims = [y, 0]
        self.width = width
        self.ratio = ratio[:-1]

    def append(self, row):
        self.dims[1] += 1
        self.data.append(row)

    def get_objs(self, font_face):
        objs = []
        line_y = 0
        for row in self.data:
            max_row_y = 0
            objs.append(line_object((self.offset[0]+self.width, self.offset[0]), (self.offset[1]-line_y, self.offset[1]-line_y)))
            for i, cell in enumerate(row):
                cell_width = self.width / sum(self.ratio) * self.ratio[i]
                cell_x = self.offset[0] + (self.width / sum(self.ratio) * sum(self.ratio[:i]))
                text_obj = text_object()
                text_obj.append(f"BT\n{12 + 2.4} TL\n/F1 {12} Tf\n{cell_x + 1} {self.offset[1] +3.4 - line_y} Td\n")
                line = ""
                line_y_temp = 0
                for word in cell.split(" "):
                    line += word + " "
                    size = lib.get_text_size(line, 12, font_face)
                    if size > cell_width - 2:
                        line_y_temp += 12 + 2.4
                        line = line[:-1]
                        text = " ".join(line.split(" ")[:-1])
                        text_obj.append(f"0 0 ({text}) \"\n")
                        line = word + " "
                if line != "":
                    text = line[:-1]
                    text_obj.append(f"0 0 ({text}) \"\n%LOL\n")
                    line_y_temp += 12 + 2.4
                    text_obj.append("ET\n")
                    objs.append(text_obj)
                if line_y_temp > max_row_y:
                    max_row_y = line_y_temp
            for i in range(self.dims[0]):
                x =  self.offset[0] + (self.width / sum(self.ratio) * sum(self.ratio[:i]))
                objs.append(line_object((x+.5, x+.5), (self.offset[1]-line_y, self.offset[1]-line_y-max_row_y - 1)))
            objs.append(line_object((self.offset[0]+self.width - (.5), self.offset[0]+self.width - (.5)), (self.offset[1]-line_y, self.offset[1]-line_y-max_row_y - 1)))
            line_y += max_row_y + 1
        objs.append(line_object((self.offset[0]+self.width, self.offset[0]), (self.offset[1]-line_y, self.offset[1]-line_y)))
        self.height = line_y + 12
        return objs

    def __str__(self):
        return ""

class line_object():
    def __init__(self, x, y, width=1):
        self.x = x
        self.y = y
        self.width = width

    def __str__(self):
        obj = text_object()
        obj.append(f"{self.width} w\n{self.x[0]} {self.y[0]} m\n{self.x[1]} {self.y[1]} l\nS")
        return str(obj)

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

class font_object():
    """
    <<
    /Type/Font
    /Subtype/TrueType
    /Name/F1
    /BaseFont/BCDEEE+Calibri
    /Encoding/WinAnsiEncoding
    /FontDescriptor 6 0 R
    /FirstChar 32
    /LastChar 32
    /Widths 18 0 R
    >>
    """
    def __init__(self, font_face, name="F1"):
        font = TTFont(font_face)
        face_name = font["name"].getName(1, 3, 1).string.replace(b'\x0a', b'').decode(errors="ignore")
        self.font_descriptor = font_descriptor_object(font_face, name)
        self.dict = {"/Type": "/Font",
                     "/Subtype": "/TrueType",
                     "/Name": name,
                     "/FirstChar": 0,
                     "/LastChar": 255,
                     "/BaseFont": "/" +face_name[1::2],
                     "/Encoding": "/MacRomanEncoding",
                     "/FontDescriptor": "%%" + self.font_descriptor.ident() + "%%"}
        try:
            self.font = TTFont(font_face)
            self.cmap = self.font['cmap']
            self.t = self.cmap.getcmap(3, 1).cmap
            self.s = self.font.getGlyphSet()
            self.units_per_em = self.font['head'].unitsPerEm
        except:
            pass

    def add_pages(self, pages):
        self.dict["/Pages"] = pages

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def __str__(self):
        text = "<<"
        for i in self.dict:
            text += i.__str__() + " " + self.dict[i].__str__() + "\n"
        text += f">>\n"
        return text

class font_descriptor_object():
    """
    <<
    /Type/FontDescriptor
    /FontName/BCDEEE+Calibri
    /Flags 32
    /ItalicAngle 0
    /Ascent 750
    /Descent -250
    /CapHeight 750
    /AvgWidth 521
    /MaxWidth 1743
    /FontWeight 400
    /XHeight 250
    /StemV 52
    /FontBBox[ -503 -250 1240 750]
    /FontFile2 19 0 R
    >>
    """
    def __init__(self, font_face, name="F1"):
        font = TTFont(font_face)
        self.name = font["name"].getName(1, 3, 1).string.replace(b'\x0a', b'').decode(errors="ignore")

        self.font_file = font_file_object(font_face)
        self.dict = {"/Type": "/FontDescriptor",
                     "/FontName": f"/{self.name[1::2]}",
                     "/ItalicAngle": "0",
                     "/Ascent": "750",
                     "/Descent": "-250",
                     "/CapHeight": "750",
                     "/AvgWidth": "521",
                     "/MaxWidth": "1743",
                     "/FontWeight": "400",
                     "/XHeight": "250",
                     "/StemV": "52",
                     "/FontBBox": "[ -503 -250 1240 750]",
                     "/FontFile2": "%%" + self.font_file.ident() + "%%"}

    def add_pages(self, pages):
        self.dict["/Pages"] = pages

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def __str__(self):
        text = "<<"
        for i in self.dict:
            text += i.__str__() + " " + self.dict[i].__str__() + "\n"
        text += f">>\n"
        return text

class font_file_object():
    """
    <<
    /Length
    >>
    """

    def __init__(self, file):
        self.stream = open(file, "r", encoding="mac-roman").read()
        self.length1 = len(self.stream)+1
        #self.stream = zlib.compress(self.stream.encode("mac-roman")).decode("mac-roman")
        self.length = len(self.stream)+1

    def ident(self):
        return hashlib.md5(self.__str__().encode('utf-8')).hexdigest()

    def __str__(self):
        text = f"<<\n/Length {self.length}\n/Length1 {self.length1}>>\n"
        text += f"stream\n{self.stream}\nendstream\n"
        return text
