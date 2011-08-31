
from lexer import Lexer, Token
from parser import *


def compute_rule_dictionary(grammar):
    grammar.rule = dict()
    for stmt in grammar.statements:
        grammar.rule[stmt.identifier] = stmt


def _expression_nullable(expression, grammar):
    for component in expression.components:
        if _component_nullable(component, grammar):
            return True
    return False

def _component_nullable(component, grammar):
    for element in component.elements:
        if not _element_nullable(element, grammar):
            return False
    return True

def _element_nullable(element, grammar):
    if element.modifier == "*" or element.modifier == "?":
        return True
    return _term_nullable(element.term, grammar)

def _term_nullable(term, grammar):
    if term.t == "string": return False
    if term.t == "identifier":
        if term.e in grammar.rule:
            return grammar.rule[term.e].epsilon
        return False

    return _expression_nullable(term.e, grammar)


def compute_epsilon_closure(grammar):
    for stmt in grammar.statements:
        stmt.epsilon = False

    changed = True
    while changed:
        changed = False
        for stmt in grammar.statements:
            if stmt.epsilon: continue
            if _expression_nullable(stmt.expression, grammar):
                changed = True
                stmt.epsilon = True




def _expression_first(expression, grammar):
    first = set()
    for component in expression.components:
        compfirst = _component_first(component, grammar)
        first  |= compfirst
    return first

def _component_first(component, grammar):
    first = set()
    for element in component.elements:
        elementfirst = _element_first(element, grammar)
        first |= elementfirst
        if not _element_nullable(element, grammar):
            break
    return first

def _element_first(element, grammar):
    return _term_first(element.term, grammar)

def _term_first(term, grammar):
    if term.t == "string": return set([term.e])
    if term.t == "identifier":
        if term.e in grammar.rule:
            return grammar.rule[term.e].first
        return set([term.e])

    return _expression_first(term.e, grammar)


def compute_first(grammar):
    for stmt in grammar.statements:
        stmt.first = set()

    changed = True
    while changed:
        changed = False
        for stmt in grammar.statements:
            first = _expression_first(stmt.expression, grammar)
            if first != stmt.first:
                changed = True
                stmt.first = first


def _expression_follow(expression, follow, grammar):
    changed = False
    for component in expression.components:
        changed |= _component_follow(component, follow, grammar)
    return changed

def _component_follow(component, follow, grammar):
    changed = False
    for i in range(len(component.elements)):
        element = component.elements[i]
        uselast = True
        for j in range(i + 1, len(component.elements)):
            nextelement = component.elements[j]
            changed |= _element_follow(element, _element_first(nextelement, grammar), grammar)
            if not _element_nullable(nextelement, grammar):
                uselast = False
                break
        if uselast:
            changed |= _element_follow(element, follow, grammar)

    return changed

def _element_follow(element, follow, grammar):
    changed = False
    if element.modifier == "*" or element.modifier == "+":
        changed |= _term_follow(element.term, _element_first(element, grammar), grammar)
    changed |= _term_follow(element.term, follow, grammar)
    return changed

def _term_follow(term, follow, grammar):
    if term.t == "string": return False
    if term.t == "identifier":
        if term.e in grammar.rule:
            changed = not (grammar.rule[term.e].follow >= follow)
            grammar.rule[term.e].follow |= follow
            return changed
        return False

    return _expression_follow(term.e, follow, grammar)


def compute_follow(grammar):
    for stmt in grammar.statements:
        stmt.follow = set()

    changed = True
    while changed:
        changed = False
        for stmt in grammar.statements:
            changed |= _expression_follow(stmt.expression, stmt.follow, grammar)



