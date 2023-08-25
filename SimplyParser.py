"""
This is a recursive descent parser for the SimplyNotJavaOrC Language. 
How we wrote this parser:
    1.) Construct the basic interface (lexer, next, has, must_be).
    2.) Convert each BNF rule into a mutually recursive function.
    3.) Add data structures to build the parse tree.
"""

import sys
from enum import Enum, auto
from SimplyLexer import Token, Lexer


class ParseType(Enum):
  PROGRAM = auto()
  ATOMIC = auto()
  ASSIGN = auto()
  ADD = auto()
  SUB = auto()
  MUL = auto()
  DIV = auto()
  POW = auto()
  NEG = auto()
  IF = auto()
  IFELSE = auto()
  LT = auto()
  ET = auto()
  PRINT = auto()
  CALL = auto()
  RETURN = auto()
  NE = auto()
  LTE = auto()
  GT = auto()
  GTE = auto()
  ARRAY = auto()
  BLOCK = auto()
  STATEMENT = auto()
  WHILE = auto()
  IMPORT = auto()
  SPLIT = auto()
  STATEMENT_LIST = auto()
  PARAMLIST = auto()
  BREAK = auto()
  READ = auto()
  ARGLIST = auto()
  REFLIST = auto()
  REF = auto()
  DEF = auto()
  BOUNDS = auto()
  SWAP = auto()
  NUMBER = auto()
  CHARACTER = auto()
  STRING = auto()
  BOOL = auto()

ariness = {
  ParseType.ATOMIC: 0,
  ParseType.ASSIGN: 2,
  ParseType.ADD: 2,
  ParseType.SUB: 2,
  ParseType.MUL: 2,
  ParseType.DIV: 2,
  ParseType.POW: 2,
  ParseType.NEG: 1,
  ParseType.IF: 2,
  ParseType.IFELSE: 3,
  ParseType.LT: 2,
  ParseType.ET: 2,
  ParseType.PRINT: 1,
  ParseType.CALL: 1,
  ParseType.RETURN: 1
}


class ParseTree:

  def __init__(self, node_type=ParseType.PROGRAM, token=None):
    self.node_type = node_type
    self.children = []
    self.token = token

  def print(self, level=0):
    """
    A handy print method. (for debugging) 
    """

    # get the midpoint
    m = int(len(self.children) / 2) - 1

    # left half
    for c in self.children[-1:m:-1]:
      c.print(level + 2)

    # print our node
    indent = '   ' * level

    if self.node_type == ParseType.ATOMIC:
      print(indent, self.token.lexeme, sep='')
    else:
      print(indent, self.node_type.name, sep='')

    # right half
    for c in self.children[m::-1]:
      c.print(level + 2)

  def insert_left_leaf(self, leaf):
    """
        Insert at the extreme left leaf position.
        """
    if len(self.children) < ariness[self.node_type]:
      self.children.insert(0, leaf)
      return

    self.children[0].insert_left_leaf(leaf)


class Parser:
  """
    Parser state will follow the lexer state.
    We consume the stream token by token.
    Match our tokens, if no match is possible, 
    print an error and stop parsing.
    """

  def __init__(self, lexer):
    self.__lexer = lexer

  def __next(self):
    """
        Advance the lexer.
        """
    self.__lexer.next()

  def __has(self, t):
    """
        Return true if t matches the current token.
        """
    ct = self.__lexer.get_tok()
    return ct.token == t

  def __must_be(self, t):
    """
        Return true if t matches the current token.
        Otherwise, we print an error message and
        exit.
        """
    if self.__has(t):
      return True

    # print an error
    ct = self.__lexer.get_tok()
    print(
      f"Parser error at line {ct.line}, column {ct.col}.\nReceived token {ct.token.name} expected {t.name}"
    )
    sys.exit(-1)

  def parse(self):
    """
        Attempt to parse a program.
        """
    self.__next()
    return self.__program()

  def __program(self):

    tree = ParseTree(ParseType.PROGRAM, self.__lexer.get_tok())

    while not self.__has(Token.EOF) and not self.__has(
        Token.ELSE) and not self.__has(Token.END):
      if self.__has(Token.BEGIN):
        self.__next()
        node = ParseTree(ParseType.BLOCK, self.__lexer.get_tok())
        tree.children.append(node)
        self.__block2(node)
        return tree
      elif self.__has(Token.NUMBER) or self.__has(Token.CHARACTER) or self.__has(Token.BOOL) or self.__has(Token.STRING):
        node = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
        self.__next()
        self.__must_be(Token.ID)
        value = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
        node.children.append(value)
        self.__next()
        self.__program2(tree, node)
        return tree
      elif self.__must_be(Token.DEF):
        node = ParseTree(ParseType.DEF, self.__lexer.get_tok())
        self.__next()
        tree.children.append(node)
        self.__fun(node)
        self.__fun_declist2(tree)
        tree.children.append(self.__block())
        return tree

  def __program2(self, lv, lv2):
    node5 = self.__var_declist2(lv2)
    if node5:
      lv.children.append(node5)
    else:
      lv.children.append(lv2)
    self.__var_declist(lv)
    self.__fun_declist(lv)
    lv.children.append(self.__block())

  def __fun_declist(self, lv):
    self.__must_be(Token.DEF)
    node = ParseTree(ParseType.DEF, self.__lexer.get_tok())
    self.__next()
    lv.children.append(node)
    self.__fun(node)
    self.__fun_declist2(lv)

  def __fun_declist2(self, lv):
    if self.__has(Token.DEF):
      node = ParseTree(ParseType.DEF, self.__lexer.get_tok())
      self.__next()
      lv.children.append(node)
      self.__fun(node)
      self.__fun_declist2(lv)
    else:
      return False

  def __fun(self, lv):
    if self.__has(Token.PROC) or self.__has(Token.NUMBER) or self.__has(
        Token.CHARACTER) or self.__has(Token.BOOL) or self.__must_be(
          Token.STRING):
      token2 = self.__lexer.get_tok()
      node = ParseTree(ParseType.ATOMIC, token2)
      self.__next()
      self.__must_be(Token.ID)
      token = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.ATOMIC, token)
      self.__must_be(Token.LPAREN)
      self.__next()
      node.children.append(result)
      lv.children.append(node)
      lv.children.append(self.__variable_choice_fun(lv))

  def __variable_choice_fun(self, lv):
    if self.__has(Token.RPAREN):
      self.__next()
      return self.__block()
    else:
      result = ParseTree(ParseType.PARAMLIST, self.__lexer.get_tok())
      result.children.append(self.__param_list(result))
      self.__must_be(Token.RPAREN)
      self.__next()
      lv.children.append(self.__block())
      return result

  def __param_list(self, lv):
    if self.__has(Token.NUMBER) or self.__has(Token.CHARACTER) or self.__has(
        Token.BOOL) or self.__must_be(Token.STRING):
      token = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.ATOMIC, token)
      result.children.append(self.__variable_choice_param1())
      self.__variable_choice_param2(lv)
      return result

  def __variable_choice_param1(self):
    if self.__has(Token.ID):
      token = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.ATOMIC, token)
      return result
    elif self.__must_be(Token.CLOSED_BRACKET):
      token = self.__lexer.get_tok()
      node = ParseTree(ParseType.ARRAY, token)
      self.__next()
      if self.__must_be(Token.ID):
        atomic = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
        node.children.append(atomic)
        self.__next()
        return node
      else:
        return False

  def __variable_choice_param2(self, lv):
    if self.__has(Token.COMMA):
      self.__next()
      lv.children.append(self.__param_list(lv))
    else:
      return False

  def __block(self):
    if self.__must_be(Token.BEGIN):
      result = ParseTree(ParseType.BLOCK, self.__lexer.get_tok())
      self.__next()
      self.__block2(result)
      return result

  def __block2(self, lv):
    if self.__has(Token.NUMBER) or self.__has(Token.CHARACTER) or self.__has(
        Token.BOOL) or self.__has(Token.STRING):
      token = self.__lexer.get_tok()
      self.__next()
      typee = ParseTree(ParseType.ATOMIC, token)
      self.__must_be(Token.ID)
      token2 = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.ATOMIC, token2)
      typee.children.append(result)
      node3 = self.__var_declist2(typee)
      if node3:
        lv.children.append(node3)
      else:
        lv.children.append(typee)
      self.__var_declist(lv)
      node5 = ParseTree(ParseType.STATEMENT_LIST, self.__lexer.get_tok())
      lv.children.append(node5)
      self.__stmnt_list(node5)
      self.__must_be(Token.END)
      self.__next()
    else:
      node5 = ParseTree(ParseType.STATEMENT_LIST, self.__lexer.get_tok())
      lv.children.append(node5)
      self.__stmnt_list(node5)
      self.__must_be(Token.END)
      self.__next()

  def __var_declist(self, lv):
    if self.__has(Token.NUMBER) or self.__has(Token.CHARACTER) or self.__has(
        Token.BOOL) or self.__has(Token.STRING):
      type_dec_tok = self.__lexer.get_tok()
      self.__next()
      type_dec_tree = ParseTree(ParseType.ATOMIC, type_dec_tok)
      self.__must_be(Token.ID)
      token2 = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.ATOMIC, token2)
      type_dec_tree.children.append(result)
      node4 = self.__var_declist2(type_dec_tree)
      if node4:
        lv.children.append(node4)
      else:
        lv.children.append(type_dec_tree)
      self.__var_declist(lv)
    else:
      return False

  def __var_declist2(self, lv):
    if self.__has(Token.LBRACKET):
      self.__next()
      result = ParseTree(ParseType.ARRAY, self.__lexer.get_tok())
      result.children.append(lv)
      self.__bounds(result)
      self.__must_be(Token.RBRACKET)
      self.__next()
      return result
    else:
      return False

  def __bounds(self, lv):
    value = ParseTree(ParseType.BOUNDS, self.__lexer.get_tok())
    self.__must_be(Token.INTLIT)
    token = self.__lexer.get_tok()
    self.__next()
    result = ParseTree(ParseType.ATOMIC, token)
    lv.children.append(value)
    value.children.append(result)
    self.__bounds2(value)

  def __bounds2(self, lv):
    if self.__has(Token.COMMA):
      self.__next()
      self.__must_be(Token.INTLIT)
      result = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      self.__next()
      lv.children.append(result)
      self.__bounds2(lv)
    else:
      return False

  def __stmnt_list(self, lv):
    result2 = ParseTree(ParseType.STATEMENT, self.__lexer.get_tok())
    lv.children.append(result2)
    result2.children.append(self.__stmnt())
    self.__stmnt_list_alt(lv)

  def __stmnt_list_alt(self, lv):
    if self.__has(Token.ID) or self.__has(Token.IF) or self.__has(
        Token.WHILE) or self.__has(Token.LPAREN) or self.__has(
          Token.INTLIT) or self.__has(Token.FLOATLIT) or self.__has(
            Token.CHARLIT) or self.__has(Token.STRING) or self.__has(
              Token.PRINT) or self.__has(Token.READ) or self.__has(
                Token.SPLIT) or self.__has(Token.BREAK) or self.__has(
                  Token.IMPORT) or self.__has(Token.RETURN):
      result2 = ParseTree(ParseType.STATEMENT, self.__lexer.get_tok())
      lv.children.append(result2)
      result2.children.append(self.__stmnt())
      self.__stmnt_list_alt(lv)
    else:
      return False

  def __stmnt(self):
    if self.__has(Token.ID):
      leaf = self.__lexer.get_tok()
      self.__next()
      left = ParseTree(ParseType.ATOMIC, leaf)
      node = self.__stmnt_alt(left)
      return node
    elif self.__has(Token.IF):
      node = ParseTree(ParseType.IF, self.__lexer.get_tok())
      self.__next()
      c = self.__condition()
      b1 = self.__block()
      node.children.append(c)
      node.children.append(b1)
      value = self.__branch_alt(c, b1)
      if value:
        return value
      else:
        return node
    elif self.__has(Token.WHILE):
      leaf = self.__lexer.get_tok()
      self.__next()
      result = ParseTree(ParseType.WHILE, leaf)
      result.children.append(self.__condition())
      result.children.append(self.__block())
      return result
    elif self.__has(Token.LPAREN):
      self.__next()
      node = self.__expression()
      self.__must_be(Token.RPAREN)
      self.__next()
      return node
    elif self.__has(Token.INTLIT) or self.__has(Token.FLOATLIT) or self.__has(
        Token.CHARLIT) or self.__has(Token.STRINGLIT):
      return self.__expression()
    elif self.__has(Token.PRINT):
      result = ParseTree(ParseType.PRINT, self.__lexer.get_tok())
      self.__next()
      result.children.append(self.__arg_list())
      return result
    elif self.__has(Token.READ):
      result = ParseTree(ParseType.READ, self.__lexer.get_tok())
      self.__next()
      result.children.append(self.__ref_list())
      return result
    elif self.__has(Token.BREAK):
      node = ParseTree(ParseType.BREAK, self.__lexer.get_tok())
      self.__next()
      return node
    else:
      return self.__return()

  def __stmnt_alt(self, lv):
    if self.__has(Token.ASSIGN):
      node = ParseTree(ParseType.ASSIGN, self.__lexer.get_tok())
      self.__next()
      self.__stmnt_alt3(node, lv)
      return node
    elif self.__has(Token.SWAP):
      node2 = ParseTree(ParseType.REF, self.__lexer.get_tok())
      node2.children.append(lv)
      node = ParseTree(ParseType.SWAP, self.__lexer.get_tok())
      self.__next()
      node.children.append(node2)
      node.children.append(self.__ref())
      return node
    elif self.__has(Token.LBRACKET):
      node = ParseTree(ParseType.ARRAY, self.__lexer.get_tok())
      self.__next()
      node.children.append(lv)
      node.children.append(self.__arg_list())
      self.__must_be(Token.RBRACKET)
      self.__next()
      value = self.__stmnt_alt2(node)
      return value
    elif self.__has(Token.LPAREN):
      self.__next()
      return self.__call_alt(lv)
    elif self.__has(Token.CLOSED_BRACKET):
      self.__next()
      self.__must_be(Token.ASSIGN)
      node = ParseTree(ParseType.ASSIGN, self.__lexer.get_tok())
      self.__next()
      node.children.append(lv)
      self.__must_be(Token.SPLIT)
      node2 = ParseTree(ParseType.SPLIT, self.__lexer.get_tok())
      node.children.append(node2)
      self.__next()
      self.__must_be(Token.LPAREN)
      self.__next()
      node2.children.append(self.__split_alt())
      self.__must_be(Token.RPAREN)
      self.__next()
      self.__must_be(Token.STRINGLIT)
      NODE5 = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      self.__next()
      node2.children.append(NODE5)
      return node
    else:
      return self.__ref_alt(lv)

  def __stmnt_alt2(self, lv):
    if self.__has(Token.ASSIGN):
      node = ParseTree(ParseType.ASSIGN, self.__lexer.get_tok())
      self.__next()
      node.children.append(lv)
      node.children.append(self.__expression())
      return node
    elif self.__must_be(Token.SWAP):
      node = ParseTree(ParseType.SWAP, self.__lexer.get_tok())
      self.__next()
      node.children.append(lv)
      node.children.append(self.__ref())
      return node

  def __stmnt_alt3(self, lv, lv2):
    if self.__has(Token.IMPORT):
      token = self.__lexer.get_tok()
      self.__next()
      node = ParseTree(ParseType.IMPORT, token)
      lv.children.append(lv2)
      self.__import2(node)
      lv.children.append(node)
    else:
      lv.children.append(lv2)
      lv.children.append(self.__expression())

  def __branch_alt(self, c, b1):
    if self.__has(Token.ELSE):
      node = ParseTree(ParseType.IFELSE, self.__lexer.get_tok())
      self.__next()
      node.children.append(c)
      node.children.append(b1)
      node.children.append(self.__block())
      return node
    else:
      return False

  def __split_alt(self):
    if self.__has(Token.CHARLIT) or self.__has(Token.STRINGLIT):
      node = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      self.__next()
      return node
    else:
      return self.__ref()

  def __delimiter(self):
    if self.__has(Token.CHARLIT) or self.__must_be(Token.STRING):
      node = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      self.__next()
      return node

  def __condition(self):
    left = self.__expression()
    if self.__has(Token.EQUAL):
      result = ParseTree(ParseType.ET, self.__lexer.get_tok())
    elif self.__has(Token.NOT_EQUAL_TO):
      result = ParseTree(ParseType.NE, self.__lexer.get_tok())
    elif self.__has(Token.LESS_THAN):
      result = ParseTree(ParseType.LT, self.__lexer.get_tok())
    elif self.__has(Token.LESS_THAN_OR_EQUAL):
      result = ParseTree(ParseType.LTE, self.__lexer.get_tok())
    elif self.__has(Token.GREATER_THAN):
      result = ParseTree(ParseType.GT, self.__lexer.get_tok())
    elif self.__must_be(Token.GREATER_THAN_OR_EQUAL):
      result = ParseTree(ParseType.GTE, self.__lexer.get_tok())
    self.__next()
    right = self.__expression()
    result.children = [left, right]
    return result

  def __expression(self):
    left = self.__term()
    node = self.__expression2()
    if node:
      node.insert_left_leaf(left)
    else:
      node = left
    return node

  def __expression2(self):
    if self.__has(Token.PLUS):
      self.__next()
      node = ParseTree(ParseType.ADD, self.__lexer.get_tok())
      t = self.__term()
      e = self.__expression2()
      node.children.append(t)
      if e:
        e.insert_left_leaf(node)
        node = e
      return node
    elif self.__has(Token.MINUS):
      self.__next()
      node = ParseTree(ParseType.SUB, self.__lexer.get_tok())
      t = self.__term()
      e = self.__expression2()
      node.children.append(t)
      if e:
        e.insert_left_leaf(node)
        node = e
      return node
    else:
      return False

  def __term(self):
    left = self.__factor()
    node = self.__term2()
    if node:
      node.insert_left_leaf(left)
    else:
      node = left
    return node

  def __term2(self):
    if self.__has(Token.TIMES):
      self.__next()

      node = ParseTree(ParseType.MUL, self.__lexer.get_tok())
      f = self.__factor()
      t = self.__term2()
      node.children.append(f)

      if t:
        t.insert_left_leaf(node)
        node = t
      return node

    elif self.__has(Token.DIVIDE):
      self.__next()

      node = ParseTree(ParseType.DIV, self.__lexer.get_tok())
      f = self.__factor()
      t = self.__term2()
      node.children.append(f)

      if t:
        t.insert_left_leaf(node)
        node = t
      return node

    else:
      return False

  def __factor(self):
    if self.__has(Token.MINUS):
      left = ParseTree(ParseType.NEG, self.__lexer.get_tok())
      self.__next()
      left.children.append(self.__exponent())
    else:
      left = self.__exponent()
    node = self.__factor2()
    if node:
      node.children.insert(0, left)
    else:
      node = left
    return node

  def __factor2(self):
    if self.__has(Token.POW):
      self.__next()

      node = ParseTree(ParseType.POW, self.__lexer.get_tok())
      node.children.append(self.__factor())
      return node
    else:
      return False

  def __exponent(self):
    if self.__has(Token.LPAREN):
      self.__next()
      node = self.__expression()
      self.__must_be(Token.RPAREN)
      self.__next()
      return node
    elif self.__has(Token.ID):
      leaf = self.__lexer.get_tok()
      self.__next()
      node = ParseTree(ParseType.ATOMIC, token=leaf)
      v2 = self.__exponent_alt(node)
      return v2
    elif self.__has(Token.INTLIT) or self.__has(Token.FLOATLIT) or self.__has(
        Token.CHARLIT) or self.__must_be(Token.STRINGLIT):
      node = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      self.__next()
      return node

  def __exponent_alt(self, lv):
    if self.__has(Token.LPAREN):
      self.__next()
      return self.__call_alt(lv)
    else:
      top_node = ParseTree(ParseType.REF, self.__lexer.get_tok())
      top_node.children.append(lv)
      self.__ref_alt(top_node)
      return top_node

  def __arg_list(self):
    node = ParseTree(ParseType.ARGLIST, self.__lexer.get_tok())
    done = False
    while not done:
      node.children.append(self.__expression())
      if self.__has(Token.COMMA):
        self.__next()
      else:
        done = True
    return node

  def __ref_list(self):
    node = ParseTree(ParseType.REFLIST, self.__lexer.get_tok())
    done = False
    while not done:
      node.children.append(self.__ref())
      if self.__has(Token.COMMA):
        self.__next()
      else:
        done = True
    return node

  def __ref(self):
    top_node = ParseTree(ParseType.REF, self.__lexer.get_tok())
    self.__must_be(Token.ID)
    token = self.__lexer.get_tok()
    self.__next()
    node = ParseTree(ParseType.ATOMIC, token)
    top_node.children.append(node)
    self.__ref_alt(top_node)
    return top_node

  def __ref_alt(self, lv):
    if self.__has(Token.LBRACKET):
      self.__next()
      lv.children.append(self.__arg_list())
      self.__must_be(Token.RBRACKET)
      self.__next()
    else:
      return False

  def __call_alt(self, lv):
    node = ParseTree(ParseType.CALL, self.__lexer.get_tok())
    if self.__has(Token.RPAREN):
      self.__next()
      node.children.append(lv)
      return node
    else:
      node.children.append(self.__arg_list())
      self.__must_be(Token.RPAREN)
      self.__next()
      node.children.insert(0, lv)
      return node

  def __return(self):
    self.__must_be(Token.RETURN)
    node = ParseTree(ParseType.RETURN, self.__lexer.get_tok())
    self.__next()
    node.children.append(self.__expression())
    return node

  def __import2(self, lv):
    if self.__has(Token.STRINGLIT):
      node2 = ParseTree(ParseType.ATOMIC, self.__lexer.get_tok())
      lv.children.append(node2)
      self.__next()
    else:
      node2 = self.__ref()
      lv.children.append(node2)


# unit test
if __name__ == "__main__":
  p = Parser(Lexer())
  tree = p.parse()
  tree.print()
