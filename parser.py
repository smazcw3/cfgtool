from lexer import Lexer, Token
import sys

class Parser():
    def __init__(self, data, name):
        self._lexer = Lexer(data)
        self._name = name
        self._token = None

    def parse(self):
        return self.parse_grammar()

    def _next_token(self):
        self._token = self._lexer.parse_token()
        if self._token.token == Token.ERROR:
            self._report_error(self._token.error_msg, self._token)
        return self._token

    def _report_error(self, msg, token):
        print >> sys.stderr, "%s:%s:%s: %s" % (self._name, token.line,
            token.column, msg)

    def parse_grammar(self):
        self._next_token()
        while True:
            tk = self._token
            if tk.token == Token.END: break
            self._parse_statement()

    def _discard_until_semicolon(self):
        while True:
            tk = self._token
            self._next_token()
            if tk.token == Token.END or tk.token == Token.SEMICOLON:
                break

    def _parse_statement(self):
        tk = self._token
        if tk.token == Token.IDENTIFIER:
            tk = self._next_token()
            if tk.token == Token.EQUALS:
                self._next_token()
                self._parse_expression()
                tk =  self._token
                if tk.token == Token.SEMICOLON:
                    self._next_token()
                    return
                else:
                    msg = "expecting `;' at the end of statement"
            else:
                msg = "expecting `=' for statement"
        else:
            msg = "expecting identifier at the begining of statement"

        if msg: self._report_error(msg, tk)
        self._discard_until_semicolon()

    def _parse_expression(self):
        self._parse_simple_expression()
        while self._token.token == Token.PIPE:
            self._next_token()
            self._parse_simple_expression()

    def _parse_simple_expression(self):
        self._parse_element()
        while (not self._token.token == Token.PIPE) and\
              (not self._token.token == Token.SEMICOLON) and\
              (not self._token.token == Token.END):
            self._parse_element()

    def _parse_element(self):
        tk = self._token
        has_prefix = False
        if tk.token == Token.TILDE or tk.token == Token.TILDE:
            has_prefix = True
            tk = self._next_token()
        self._parse_term()
        tk = self._token
        if not has_prefix and (tk.token == Token.STAR or \
                               tk.token == Token.PLUS or \
                               tk.token == Token.QUESTION_MARK):
            self._next_token()

    def _parse_term(self):
        tk = self._token
        if tk.token == Token.IDENTIFIER:
            self._next_token()
        elif tk.token == Token.STRING:
            self._next_token()
        elif tk.token == Token.OPEN_PARENTHESIS:
            self._next_token()
            self._parse_expression()
            tk = self._token
            if tk.token == Token.CLOSE_PARENTHESIS:
                self._next_token()
            else:
                self._next_token()
                self._report_error("expecting `)' at the end of term", tk)
        else:
            self._report_error("invalid term `%s'" % tk.tkstr, tk)
            self._next_token()

if __name__ == '__main__':
    f = open("grammar.txt", "rb")
    data = f.read()
    f.close()

    parser = Parser(data, "grammar.txt")
    parser.parse()

