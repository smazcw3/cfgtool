
import sys

def _is_letter(ch):
    o = ord(ch)
    return (o >= ord('a') and o <= ord('z')) or \
           (o >= ord('A') and o <= ord('Z')) or \
           (o == ord('_'))

def _is_digit(ch):
    o = ord(ch)
    return o >= ord('0') and o <= ord('9')

def _is_octal(ch):
    o = ord(ch)
    return o >= ord('0') and o <= ord('7')

def _is_space(ch):
    return (" \t\r\n".find(ch) >= 0) and ch

class Token():
    ERROR = -1
    END = 0
    OPEN_PARENTHESIS = 1
    CLOSE_PARENTHESIS = 2
    COLON = 3
    SEMICOLON = 4
    PIPE = 5
    STAR = 6
    PLUS = 7
    QUESTION_MARK = 8
    IDENTIFIER = 9
    STRING = 10
    WHITESPACE = 11
    COMMENT = 12

    def __init__(self, token, tkstr, line, column):
        self.token = token
        self.tkstr = tkstr
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token[%s, %s, %s, %s]" %\
          (self.token, self.tkstr, self.line, self.column)

class Lexer():
    def __init__(self, data, name, errfn = None):
        self._input = data
        self._name = name
        self._pos = 0
        self._newline = True
        self._tab = False
        self._line = 0
        self._column = 0
        self._error = False
        self._errfn = errfn

        def report(msg):
            print >> sys.stderr, msg

        if not errfn:
            self.errfn = report

    def _available(self):
        return self._pos < len(self._input)

    def _peek_char(self):
        if self._available():
            c = self._input[self._pos]
            return c
        return ""

    def _consume_char(self):
        if not self._available():
            return ""

        if self._newline:
            self._line += 1
            self._column = 0
        c = self._peek_char()
        if self._tab:
            self._column += 4 - (self._column % 4)
        else:
            self._column += 1

        self._pos += 1
        self._newline = (c == "\n")
        self._tab = (c == "\t")
        return c

    def _report_error(self, msg):
        self._error = True
        self._errfn(msg)

    def _parse_whitespace(self):
        c = self._consume_char()

        line = self._line
        column = self._column
        tkstr = c

        while _is_space(self._peek_char()):
            c = self._consume_char();
            tkstr += c

        return Token(Token.WHITESPACE, tkstr, line, column)

    def _parse_comment(self):
        c = self._consume_char()

        line = self._line
        column = self._column
        tkstr = c

        while c and (not (c == "\n")):
            c = self._consume_char()
            tkstr += c

        return Token(Token.COMMENT, tkstr, line, column)


    def _parse_identifier(self):
        tkstr = self._consume_char()
        line = self._line
        column = self._column

        while True:
            c = self._peek_char()
            if (not _is_letter(c)) and (not _is_digit(c)): break
            self._consume_char()
            tkstr += c

        return Token(Token.IDENTIFIER, tkstr, line, column)

    def _parse_string(self):
        start = tkstr = self._consume_char()
        line = self._line
        column = self._column
        while True:
            c = self._consume_char()
            if not c or c == "\n":
                self._report_error("lexer: %s[%d:%d] malformed string" %\
                                   (self._name, line, column))
                break

            tkstr += c
            if c == start: break
            if c == "\\":
                c = self._consume_char()
                tkstr += c
                if "abfnrtv\\\"\'\n".find(c) >= 0:
                    continue
                if _is_octal(c):
                    count = 1
                    while count < 3 and _is_octal(self._peek_char()):
                        count += 1
                        c = self._consume_char()
                        tkstr += c
                else:
                    self._report_error("lexer: %s[%d:%d] invalid escape sequence `\\%s'" %\
                                       (self._name, self._line, self._column, c))
                

        return Token(Token.STRING, tkstr, line, column)

    def parse_token(self):
        c = self._peek_char()

        if not c:
            return Token(Token.END, "", self._line, self._column)

        punctuation_chars = "():;|*+?"
        punctuation_tokens = [
            Token.OPEN_PARENTHESIS,
            Token.CLOSE_PARENTHESIS,
            Token.COLON,
            Token.SEMICOLON,
            Token.PIPE,
            Token.STAR,
            Token.PLUS,
            Token.QUESTION_MARK
        ]
        i = punctuation_chars.find(c)
        if i >= 0:
            c = self._consume_char()
            return Token(punctuation_tokens[i], c, self._line, self._column)

        if _is_space(c):
            return self._parse_whitespace()

        if c == "#":
            return self._parse_comment()

        if c == "\"" or c == "\'":
            return self._parse_string()

        if _is_letter(c):
            return self._parse_identifier()

        c = self._consume_char()
        self._report_error("lexer: %s[%d:%d] invalid character `%s'" %\
                           (self._name, self._line, self._column, c))
        return Token(Token.ERROR, c, self._line, self._column)

    def __iter__(self):
        return self

    def next(self):
        t = self.parse_token()
        if t.token == Token.END:
            raise StopIteration
        else:
            return t

if __name__ == '__main__':
    f = open("grammar.txt", "rb")
    data = f.read()
    f.close()

    lexer = Lexer(data, "grammar.txt")
    for t in lexer:
        print t

