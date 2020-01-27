from pathlib import Path
LOGGING_VERBOSITY = 0
IGNORE_QUIT       = False

class OutputMethod:
    def print(self):
        print(self.as_string(), end = "")

class Log(OutputMethod):
    global LOGGING_VERBOSITY
    def __init__(self, log_name, details):
        self.log_name = log_name
        self.details = details
        self.level = 1

    def as_string(self):
        if LOGGING_VERBOSITY >= self.level:
            path = Path(self.details).resolve()
            path = str(path).replace(str(Path.cwd()), ".").replace(str(Path.home()), "~")
            result  = f'{self.log_name}: {path}\n'
            return result
        return ""

class LexingLog(Log):
    def __init__(self, details):
        super().__init__('Lexing', details)
        self.level = 2

class UsePatternLog(Log):
    def __init__(self, details):
        super().__init__('Using Pattern', details)
        self.level = 3

class UseFileMatchLog(Log):
    def __init__(self, details):
        super().__init__('Pattern Matched File', details)
        self.level = 3

class ParsingLog(Log):
    def __init__(self, details):
        super().__init__('Parsing', details)
        self.level = 2

class WritingLog(Log):
    def __init__(self, details):
        super().__init__('Writing', details)
        self.level = 2

class IncludeLog(Log):
    def __init__(self, details):
        super().__init__('Including', details)
        self.level = 3

class Warning(OutputMethod):
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File <{self.pos_start.fn}>, Line {self.pos_start.ln + 1}'
        result +=  '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end) + "\n"
        return result

class NoFileIncludedWarning(Warning):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'No File Included', details)

class Error(OutputMethod):
    global IGNORE_QUIT
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    def print(self):
        super().print()
        if not IGNORE_QUIT:
            quit()

    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File <{self.pos_start.fn}>, Line {self.pos_start.ln + 1}'
        result +=  '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end) + "\n"
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class CircularRefError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Circular refrence', details)

class NoSuchPathError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'No Such Path', details)

class NoSuchPropDefinedError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'No Such Path', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class VaryingTableRowSizeError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Tabl Rows Varry', details)

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')
