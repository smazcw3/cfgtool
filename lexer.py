class Token():
    ERROR = -1
    END = 0
    OPEN_PARENTHESIS = 1
    CLOSE_PARENTHESIS = 2
    EQUALS = 3
    COLON = 4
    SEMICOLON = 5
    PIPE = 6
    STAR = 7
    PLUS = 8
    TILDE = 9
    AND = 10
    QUESTION_MARK = 11
    IDENTIFIER = 12
    STRING = 13

    def __init__(self, token, tkstr, line, column, error_msg = None):
        self.token = token
        self.tkstr = tkstr
        self.line = line
        self.column = column
        self.error_msg = error_msg

    def __repr__(self):
        return "Token[%s, %s, %s, %s, %s, %s]" %\
          (self.token, self.tkstr, self.line, self.column, self.error_msg)

class Lexer():
    def __init__(self, data):
        self._input = data
        self._pos = 0
        self._newline = True
        self._line = 0
        self._column = 0

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
        self._column += 1
        self._pos += 1
        self._newline = (c == "\n")
        return c

    def _discard_whitespaces(self):
        c = self._consume_char()
        while " \t\r\n".find(c) >= 0 and c:
            c = self._consume_char();
        return c

    def _discard_comments(self):
        c = self._discard_whitespaces()
        while c == "#":
            while c and (not (c == "\n")):
                c = self._consume_char()
            if not c: return c
            c = self._discard_whitespaces()
        return c

    def parse_token(self):
        c = self._discard_comments()
        line = self._line
        column = self._column
        if not c:
            return Token(Token.END, "", line, column)

        punctuation_chars = "()=:;|*+~&?"
        punctuation_tokens = [
            Token.OPEN_PARENTHESIS,
            Token.CLOSE_PARENTHESIS,
            Token.EQUALS,
            Token.COLON,
            Token.SEMICOLON,
            Token.PIPE,
            Token.STAR,
            Token.PLUS,
            Token.TILDE,
            Token.AND,
            Token.QUESTION_MARK
        ]
        i = punctuation_chars.find(c)
        if i >= 0:
            return Token(punctuation_tokens[i], c, line, column)

        tokstr = c
        if c == "\"":
            escape = False
            while True:
                c = self._consume_char()
                if not c:
                    return Token(Token.ERROR, tokstr, line, column,
                                 "reached the end of input while expecting the end of string")
                if c == "\n":
                    return Token(Token.ERROR, tokstr, line, column,
                                 "a string cannot span multiple lines")
                tokstr += c
                if c == "\"" and (not escape):
                    return Token(Token.STRING, tokstr, line, column)
                escape = (c == "\\")

        def is_letter(ch):
            o = ord(ch)
            return (o >= ord('a') and o <= ord('z')) or \
                   (o >= ord('A') and o <= ord('Z'))

        def is_digit(ch):
            o = ord(ch)
            return o >= ord('0') and o <= ord('9')

        if is_letter(c):
            while True:
                c = self._peek_char()
                if (not is_letter(c)) and (not is_digit(c)): break
                self._consume_char()
                tokstr += c
            return Token(Token.IDENTIFIER, tokstr, line, column)

        return Token(Token.ERROR, tokstr, line, column,
                     "invalid token `%s'" % tokstr)

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

    lexer = Lexer(data)
    for t in lexer:
        print t

