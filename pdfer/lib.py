import os

def get_text_size(text, font_size, font_face):
    try:
        text = removebs(text)
        total = 0
        for c in text:
            if ord(c) in font_face.t and font_face.t[ord(c)] in font_face.s:
                total += font_face.s[font_face.t[ord(c)]].width
            else:
                total += font_face.s['.notdef'].width
        total = total*float(font_size)/font_face.units_per_em
        return int(total)
    except:
        return 0

def addbs(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("(", "\\(")
    text = text.replace(")", "\\)")
    return text


def removebs(text):
    text = text.replace("\\\\", "\\")
    text = text.replace("\\(", "(")
    text = text.replace("\\)", ")")
    return text
