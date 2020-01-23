TT_NUM = "NUMBER"
TT_TEXT = "TEXT"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACE = "LBRACE"
TT_RBRACE = "RBRACE"
TT_LBRACKET = "LBRACKET"
TT_RBRACKET = "RBRACKET"
TT_LTAG = "LTAG"
TT_RTAG = "RTAG"
TT_UNDERSCORE = "UNDERSCORE"
TT_NEWLINE = "NEWLINE"
TT_DOLLAR = "DOLLAR"
TT_GRAVE = "GRAVE"
TT_MINUS = "MINUS"
TT_STAR = "STAR"
TT_PLUS = "PLUS"
TT_HASH = "HASH"
TT_IDENT = "IDENT"
TT_BAR = "BAR"
TT_EXCLAIM = "EXCLAIM"
TT_COLON = "COLON"
TT_EOF = "EOF"

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(self.value)

        if pos_end:
            self.pos_end = pos_end
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
