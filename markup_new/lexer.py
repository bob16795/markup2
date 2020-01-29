from markup_new import tokenclass, output
from __main__ import *

DIGITS = "1234567890"
CHARS  = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%./;,\"'=^\\?&P{}"
class Lexer:
    def __init__(self, text, fn):
        self.text = text
        self.pos = output.Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in '\t':
                tokens.append(tokenclass.Token(tokenclass.TT_IDENT, pos_start=self.pos))
                self.advance()
            elif self.current_char in ' ':
                start = self.pos
                self.advance()
                if self.current_char in ' ':
                    tokens.append(tokenclass.Token(tokenclass.TT_IDENT, pos_start=start, pos_end=self.pos))
                    self.advance()
                else:
                    tokens.append(self.make_text())
            elif self.current_char in '+':
                tokens.append(tokenclass.Token(tokenclass.TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char in '-':
                tokens.append(tokenclass.Token(tokenclass.TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char in '_':
                tokens.append(tokenclass.Token(tokenclass.TT_UNDERSCORE, pos_start=self.pos))
                self.advance()
            elif self.current_char in '!':
                tokens.append(tokenclass.Token(tokenclass.TT_EXCLAIM, pos_start=self.pos))
                self.advance()
            elif self.current_char in '|':
                tokens.append(tokenclass.Token(tokenclass.TT_BAR, pos_start=self.pos))
                self.advance()
            elif self.current_char in ':':
                tokens.append(tokenclass.Token(tokenclass.TT_COLON, pos_start=self.pos))
                self.advance()
            elif self.current_char in '*':
                tokens.append(tokenclass.Token(tokenclass.TT_STAR, pos_start=self.pos))
                self.advance()
            elif self.current_char in '\n':
                tokens.append(tokenclass.Token(tokenclass.TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in '(':
                tokens.append(tokenclass.Token(tokenclass.TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char in ')':
                tokens.append(tokenclass.Token(tokenclass.TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char in '<':
                tokens.append(tokenclass.Token(tokenclass.TT_LTAG, pos_start=self.pos))
                self.advance()
            elif self.current_char in '>':
                tokens.append(tokenclass.Token(tokenclass.TT_RTAG, pos_start=self.pos))
                self.advance()
            elif self.current_char in '[':
                tokens.append(tokenclass.Token(tokenclass.TT_LBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char in ']':
                tokens.append(tokenclass.Token(tokenclass.TT_RBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char in '$':
                tokens.append(tokenclass.Token(tokenclass.TT_DOLLAR, pos_start=self.pos))
                self.advance()
            elif self.current_char in '#':
                tokens.append(tokenclass.Token(tokenclass.TT_HASH, pos_start=self.pos))
                self.advance()
            elif self.current_char in CHARS:
                tokens.append(self.make_text())
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], errors.IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(tokenclass.Token(tokenclass.TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_text(self):
        text_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in CHARS + " ":
            text_str += self.current_char
            self.advance()
        return tokenclass.Token(tokenclass.TT_TEXT, text_str, pos_start, self.pos )

    def make_number(self):
        num_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + ".":
            num_str += self.current_char
            self.advance()
        return tokenclass.Token(tokenclass.TT_NUM, num_str, pos_start, self.pos)

def run(text, fn):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    return tokens, error
