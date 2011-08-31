from lexer import Lexer, Token
import sys

class Grammar():
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "Grammar[" +\
               ",".join([repr(stmt) for stmt in self.statements]) +\
               "]"

    def __str__(self):
        return "\n\n".join([str(stmt) for stmt in self.statements])

class Statement():
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return "Statement[%s, %s]" % (self.identifier, repr(self.expression))

    def __str__(self):
        prefix = "\n "
        for i in range(len(self.identifier)):
            prefix = prefix + " "
        expr = str(self.expression)
        expr = prefix.join(expr.split("\n"))
        return "%s : %s%s;" % (self.identifier, expr, prefix)

class Expression():
    def __init__(self, components):
        self.components = components

    def __repr__(self):
        return "Expression[" +\
               ",".join([repr(comp) for comp in self.components]) +\
               "]"

    def __str__(self):
        return "\n| ".join([str(comp) for comp in self.components])

class Component():
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return "Component[" +\
               ",".join([repr(elm) for elm in self.elements]) +\
               "]"

    def __str__(self):
        return " ".join([str(elm) for elm in self.elements])

class Element():
    def __init__(self, term, modifier):
        self.term = term
        self.modifier = modifier

    def __repr__(self):
        return "Element[%s, %s]" % (self.term, self.modifier)

    def __str__(self):
        out = str(self.term)
        if self.modifier:
            out = out + self.modifier
        return out

class Term():
    def __init__(self, e, t):
        self.e = e
        self.t = t

    def __repr__(self):
        return "Term[%s, %s]" % (self.e, self.t)

    def __str__(self):
        out = ""
        if self.t == "expression":
            out = out + "("
        out = out + str(self.e)
        if self.t == "expression":
            out = out + ")"
        return out


class Parser():
    def __init__(self, data, name, errfn = None):
        self._name = name
        self._token = None
        self._error = False

        def report(msg):
            print >> sys.stderr, msg

        if not errfn: errfn = report
        self._errfn = errfn
        self._lexer = Lexer(data, name, errfn)

    def parse(self):
        return self.parse_grammar()

    def _next_token(self):
        while True:
            self._token = self._lexer.parse_token()
            if self._token.token == Token.WHITESPACE or \
               self._token.token == Token.COMMENT: continue
            break
        
        return self._token

    def _report_error(self, msg, token):
        self._error = True
        self._errfn("parser: %s[%s:%s]: %s" %\
                    (self._name, token.line, token.column, msg))

    def parse_grammar(self):
        self._next_token()
        statements = []
        while True:
            tk = self._token
            if tk.token == Token.END: break
            stmt = self._parse_statement()
            statements.append(stmt)
        if not self._error:
            return Grammar(statements)
        return None

    def _discard_until_semicolon(self):
        while True:
            tk = self._token
            self._next_token()
            if tk.token == Token.END or tk.token == Token.SEMICOLON:
                break

    def _parse_statement(self):
        tk = self._token
        if tk.token == Token.IDENTIFIER:
            identifier = tk.tkstr
            tk = self._next_token()
            if tk.token == Token.COLON:
                self._next_token()
                expression = self._parse_expression()
                tk =  self._token
                if tk.token == Token.SEMICOLON:
                    self._next_token()
                    return Statement(identifier, expression)
                else:
                    msg = "expecting `;' at the end of statement"
            else:
                msg = "expecting `:' for statement"
        else:
            msg = "expecting identifier at the begining of statement"

        self._report_error(msg, tk)
        self._discard_until_semicolon()
        return None

    def _parse_expression(self):
        components = []
        comp = self._parse_component()
        components.append(comp)
        while self._token.token == Token.PIPE:
            self._next_token()
            comp = self._parse_component()
            components.append(comp)
        return Expression(components)

    def _parse_component(self):
        elements = []
        while (not self._token.token == Token.PIPE) and\
              (not self._token.token == Token.SEMICOLON) and\
              (not self._token.token == Token.CLOSE_PARENTHESIS) and\
              (not self._token.token == Token.END):
            elm = self._parse_element()
            elements.append(elm)
        return Component(elements)

    def _parse_element(self):
        term = self._parse_term()
        modifier = None
        tk = self._token
        if tk.token == Token.STAR or \
           tk.token == Token.PLUS or \
           tk.token == Token.QUESTION_MARK:
            modifier = tk.tkstr
            self._next_token()
        return Element(term, modifier)

    def _parse_term(self):
        tk = self._token
        if tk.token == Token.IDENTIFIER:
            self._next_token()
            return Term(tk.tkstr, "identifier")
        elif tk.token == Token.STRING:
            self._next_token()
            return Term(tk.tkstr, "string")
        elif tk.token == Token.OPEN_PARENTHESIS:
            self._next_token()
            expression = self._parse_expression()
            tk = self._token
            if tk.token == Token.CLOSE_PARENTHESIS:
                self._next_token()
                return Term(expression, "expression")
            else:
                self._next_token()
                self._report_error("expecting `)' at the end of term", tk)
        else:
            self._report_error("invalid term `%s'" % tk.tkstr, tk)
            self._next_token()
        return None

if __name__ == '__main__':
    f = open("grammar.txt", "rb")
    data = f.read()
    f.close()

    parser = Parser(data, "grammar.txt")
    print parser.parse()

