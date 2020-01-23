import pdfer.objects as objs
import pdfer.lib as lib

class pdf_file():
    def __init__(self):
        self.catalog = objs.catalog_object()
        self.pages = objs.pages_object()
        self.catalog.add_pages(self.pages)
        self.outlines = objs.outlines_object()
        self.font = objs.font_object("/F1")
        self.level = [0, 0, 0]
        self.cpt = 0
        self.prt = 0
        self.chapters = []
        self.parts = []
        self.line_spacing = 2.4
        self.column_spacing = 20
        self.current_column = 1
        self._columns = 1
        self.media_box = [612, 792]
        self.title = ""
        self.author = ""
        self._font_face = lib.font_face("times.ttf")
        self.title_page = False
        self.index = {}
        self.toc = {}
        self.header = ["{page_number}", "{part}", "{chapter}"]
        self.footer = ["{author}", "", "{title}"]
        self.add_page()

    def add_header_footer(self, page, offset):
        chapter = ["", 0]
        part = ["", 0]
        number = 0
        for i in self.chapters:
            number += 1
            if i[0] + offset - 1 < page:
                chapter[0] = i[1]
                chapter[1] = number
        number = 0
        for i in self.parts:
            number += 1
            if i[0] + offset - 1 < page:
                part[0] = i[1]
                part[1] = number
        footer = False
        for i in [self.header, self.footer]:
            for align in range(0,3):
                if i[align] != "":
                    text = i[align].format(page_number = page + 1,
                                           page_total = len(self.pages.pages),
                                           title = self.title,
                                           author = self.author,
                                           part = part[0],
                                           part_number = part[1],
                                           chapter = chapter[0],
                                           chapter_number = chapter[1])
                    text_size = lib.get_text_size(text, 12, self.font_face)
                    x = 100
                    if align == 1:
                        x = (self.media_box[0] - text_size) / 2
                    if align == 2:
                        x = self.media_box[0] - text_size - 100
                    y = self.media_box[1] - 50
                    if footer:
                        y = 50
                    text_obj = objs.text_object()
                    text_obj.append(f"BT\n/F1 12 Tf\n{x} {y} Td\n0 0 ({text}) \"\nET")
                    self.pages.pages[page].text_objs[0:0] = [text_obj]
            footer = True

    def add_index_entry(self, entrys):
        for entry in entrys.split(";"):
            entry = entry.strip(" ")
            if entry[0] not in self.index:
                self.index[entry[0]] = {}
            if entry not in self.index[entry[0]]:
                self.index[entry[0]][entry] = []
            if not len(self.pages.pages) in self.index[entry[0]][entry]:
                self.index[entry[0]][entry].append(len(self.pages.pages))

    def add_page(self, text = None, size = None, odd = None):
        self.y = 692
        self.y_start = 692
        self.current_column = 1
        page = objs.page_object(self.font)
        self.pages.append(page)
        if (len(self.pages.pages) % 2 == 0) == odd:
            page = objs.page_object(self.font)
            self.pages.append(page)
        if text:
            self.add_text(text, size)

    def add_space(self, space):
        self.y -= (space)
        if self.y < 100:
            self.add_page()

    def add_heading(self, text, level):
        space = 0
        align = 1
        col_start = self.columns
        size = 32
        number = f""
        line = False
        if level > 0:
            self.level[level-1] += 1
            for i in range(level + 1, 2):
                self.level[i] = 0
            levels = [i.__str__() for i in self.level]
            number = ".".join(levels[::1]) + " "
            while ".0" in number:
                number = number.replace(".0", "")
            self.toc[number +text] = (level + 1, (len(self.pages.pages)))
        else:
            self.columns = 1
            number = ""
            self.level = [0, 0, 0]
            if level == -1:
                self.toc[f"Chapter {self.cpt + 1} - {text}"] = (1, len(self.pages.pages))
                self.cpt += 1
                size = 12
                align = 3
                line = True
                if self.pages.pages[-1].text_objs != []:
                    self.add_page(odd = True)
                self.chapters.append((len(self.pages.pages) - 1, text))
                self.add_space(250)
                self.add_text(f"Chapter {self.cpt}", 32, 3)
            if level == -2:
                self.toc[f"Part {self.prt + 1} - {text}"] = (0, len(self.pages.pages))
                self.cpt = 0
                self.prt += 1
                size = 45
                align = 3
                line = True
                if self.pages.pages[-1].text_objs != []:
                    self.add_page(odd = True)
                self.parts.append((len(self.pages.pages) - 1, text))
                self.add_space(200)
                self.add_line(0, 0)
                self.add_text(f"Part {self.prt}", size, 3)
        if level == 2:
            size = 24
        if level == 3:
            size = 16
        self.add_text(f"{number}{text}", size, align)
        if line:
            self.add_line(10, 30)
        if level == -2:
            self.add_page()
        self.columns = col_start

    @property
    def font_face(self):
        return self._font_face

    @font_face.setter
    def font_face(self, value):
        self._font_face = lib.font_face(value)

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        if value != self._columns:
            if (self._columns != 1) and (self.current_column != 1):
                self.add_page()
            self.y_start = self.y
            self._columns = value
            self.current_column = 1

    def add_line(self, padding_top, padding_bot):
        self.add_space(padding_top)
        obj = objs.text_object()
        obj.append(f"100 {self.y} m\n{self.media_box[0]-100} {self.y} l\nS")
        self.pages.pages[-1].append(obj)
        self.add_space(padding_bot)

    def add_text(self, text, size = 12, align=1):
        if self.y - (size + self.line_spacing) < 100:
            if self.current_column >= self._columns:
                self.current_column = 1
                self.add_page(text, size)
            else:
                self.current_column += 1
                self.y = self.y_start
                self.add_text(text, size)
        else:
            text_obj = objs.text_object()
            column_size = ((self.media_box[0]-200) - (self.column_spacing * (self.columns - 1))) / self.columns
            col_x = ((column_size + self.column_spacing) * (self.current_column - 1)) + 100 
            text_obj.append(f"BT\n{size + self.line_spacing} TL\n/F1 {size} Tf\n{col_x} {self.y} Td\n")
            full = False
            text = lib.addbs(text).replace("\n", "\n\t")
            if "\n" in text:
                text = "" + text
            for line in text.split("\n"):
                pdf_line = []
                for word in line.split(" "):
                    if not full:
                        pdf_line.append(word)
                        if lib.get_text_size(' '.join(pdf_line), size, self.font_face) >= column_size:
                            spacing = 1
                            try:
                                spacing =( column_size - lib.get_text_size(' '.join(pdf_line[:-1]), size, self.font_face)) / (len(pdf_line[:-1]) - 1)
                            except:
                                pass
                            text_obj.append(f"{spacing} 0 ({' '.join(pdf_line[:-1])}) \"\n")
                            self.y -= size + self.line_spacing
                            pdf_line = [word]
                            if self.y - (size + self.line_spacing) < 100:
                                full = True
                                overfill = pdf_line
                    else:
                        overfill.append(word)
                if not full:
                    if pdf_line:
                        if align == 1:
                            text_obj.append(f"0 0 ({' '.join(pdf_line)}) \"\n() '\n")
                        elif align == 2:
                            offset = column_size - lib.get_text_size(' '.join(pdf_line), size, self.font_face)
                            text_obj.append(f"{offset} 0 Td\n0 0 ({' '.join(pdf_line)}) \"\n() '\n")
                        elif align == 3:
                            offset = (column_size - lib.get_text_size(' '.join(pdf_line), size, self.font_face))/2
                            text_obj.append(f"{offset} 0 Td\n0 0 ({' '.join(pdf_line)}) \"\n() '\n")
                        self.y -= size + self.line_spacing
                        self.y -= size + self.line_spacing
                else:
                    if overfill:
                        overfill[-1] += "\n"
            if len(text.split("\n")) == 1:
                self.y += size + self.line_spacing
            text_obj.append("ET\n")
            self.pages.pages[-1].append(text_obj)
            if full:
                if self.current_column >= self._columns:
                    self.current_column = 1
                    self.add_page(' '.join(overfill)[:-1].replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\"), size)
                else:
                    self.current_column += 1
                    self.y = self.y_start
                    self.add_text(' '.join(overfill)[:-1].replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\"), size)

    def finish(self):
        toc_length = self.get_toc_size()
        toc_file = self.make_toc(toc_length)
        self.pages.pages[0:0] = toc_file.pages.pages
        self.add_index(toc_length)
        title_pos = (self.media_box[0] - lib.get_text_size(self.title, 12, self.font_face)) / 2
        for i, page in enumerate(self.pages.pages):
            self.add_header_footer(i, toc_length)
        if self.title_page:
            self.make_title_page()

    def make_title_page(self):
        title_file = pdf_file()
        title_file.add_line(30, 30)
        title_file.add_text(self.title.upper(), 48, 3)
        title_file.add_line(30, 30)
        self.pages.pages[0:0] = title_file.pages.pages

    def make_toc(self, offset):
        toc_file = pdf_file()
        toc_file.add_text("Table Of Contents", 32, 3)
        toc_file.add_line(5, 5)
        toc_file.columns = 2
        for i in self.toc:
            toc_file.add_text(("  " * (self.toc[i][0])) + i)
            toc_file.y += 12 + toc_file.line_spacing
            toc_file.add_text(str(self.toc[i][1] + offset),align=2)
        return toc_file

    def get_toc_size(self):
        toc_file = self.make_toc(0)
        length = len(toc_file.pages.pages)
        return length

    def add_index(self, offset):
        self.add_page()
        self.columns = 1
        self.add_text("INDEX", 32, 3)
        self.add_line(5, 5)
        self.columns = 3
        for letter in sorted(self.index):
            self.add_text(letter, 24)
            for text in self.index[letter]:
                self.add_text(text)
                self.y += 12 + self.line_spacing
                numbers = ", ".join([str(i + offset) for i in self.index[letter][text]])
                self.add_text(numbers,align=2)

    def sequence(self):
        objects_ordered = []
        objects_ordered.append(self.catalog)
        objects_ordered.append(self.outlines)
        objects_ordered.append(self.pages)
        for page in self.pages.pages:
            objects_ordered.append(page)
            for text in page.text_objs:
                objects_ordered.append(text)
        objects_ordered.append(self.font)   
        return objects_ordered

    def __str__(self):
        objects_ordered = self.sequence()
        text = "%PDF-1.2\n"
        footer = f"xref\n0 {len(objects_ordered) - 1}\n0000000000 65535 f\n"
        end = f"trailer\n<< /Size {len(objects_ordered) - 1}\n/Root 1 0 R\n>>\nstartxref\n"
        for i, object in enumerate(objects_ordered):
            footer += "{:0=10} 00000 n\n".format(len(text) - 1)
            text += f"{i + 1} 0 obj\n{object.__str__()}endobj\n"
        for i, object in enumerate(objects_ordered):
            text = text.replace(f"%%{object.ident()}%%", f"{i + 1} 0 R")
        end += f"{len(text)}\n%%EOF"
        return text + footer + end

if __name__=="__main__":
    file = pdf_file()
    print(file.__str__())
