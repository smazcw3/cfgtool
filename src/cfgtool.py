#!/usr/bin/env python
from lexer import Lexer, Token
from parser import *
from utils import *
import sys



def main(argv):
    grammar_file = argv[1]
    f = open(grammar_file, "rb")
    data = f.read()
    f.close()

    parser = Parser(data, grammar_file)
    grammar = parser.parse()
    if not grammar: return 1
    compute_rule_dictionary(grammar)
    compute_epsilon_closure(grammar)
    compute_first(grammar)
    compute_follow(grammar)

    for stmt in grammar.statements:
       print "################### %s ###################\n" % stmt.identifier
       print stmt
       print "\n#Epsilon = %s;" % stmt.epsilon
       print "\n#First = %s;" % ", ".join(list(stmt.first))
       print "\n#Follow = %s;" % ", ".join(list(stmt.follow))
       print "\n\n\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
