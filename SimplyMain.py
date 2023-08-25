"""
The SimplyNotJavaOrC interpreter. The semantics of language are as follows:
    - Math operators: +, -, *, /, **
    - Parenthesis ()
    - All operations follow the usual order of operations.
    - SinplyNotJavaOrC does floating point or int arithmetic based on if assignment or read is used.
    - Read converts anything numeric to a floating point.
    - Read command can read a variable from the user.
      READ x
      Prompt: "x := " 
    - Assignment is performed by ":="
       x := 2
    - PRINT < arglist > will print the value or values.
      PRINT "HELLO", "WORLD"
    - REFER TO THE BNF FOR THE REST OF THE SEMANTICS AND SYNTAX OF THE LANGUAGE
Errors
    - identify context sensitive errors
    - Variables must be declared before the language allows a person to use them.
    - Read or assignment allow users to get input from the user or manually assign a value via assignment.
    - The langauge will break typing if made to do so. If a int or float is put in a string array it will put in a int or float because math is a lot more important than strings in this language.
"""

from SimplyParser import Parser, ParseType, ParseTree
from SimplyLexer import Token, Lexer
import sys
from enum import Enum, auto
from collections import ChainMap
import pdb
import argparse


class RefType(Enum):
  ID = auto()
  FUNCTION = auto()


class Ref:
  """
    Reference which is bound to a name.
    """

  def __init__(self, ref_type, ref_value):
    self.ref_type = ref_type
    self.ref_value = ref_value  # value of any variable


class RefEnv:
  # Has 2 fields, ref type and ref value
  def __init__(self, parent=None):
    self.tab = ChainMap()
    if parent:
      self.tab = ChainMap(self.tab, parent.tab)
    self.return_value = None
    self.break_val = False

    
  def lookup(
      self,
      name):  # change ref value after a lookup is how you do an assignment
    """
    Search for a symbol in the reference environment.
    """
    # try to find the symbol
    if name not in self.tab:
      return None

    return self.tab[name]

    
  def insert(self, name, ref):
    """
        Insert a symbol into the inner-most reference environment.
        """
    self.tab[name] = ref


def eval_parse_tree(t, env):
    """
    Evaluate the parse tree
    """
    if t.node_type == ParseType.PROGRAM:
        return eval_program(t, env)
    elif t.node_type == ParseType.ATOMIC:
        return eval_atomic(t, env)
    elif t.node_type == ParseType.ASSIGN:
        return eval_assign(t, env)
    elif t.node_type == ParseType.ADD:
        return eval_add(t, env)
    elif t.node_type == ParseType.SUB:
        return eval_sub(t, env)
    elif t.node_type == ParseType.MUL:
        return eval_mul(t, env)
    elif t.node_type == ParseType.DIV:
        return eval_div(t, env)
    elif t.node_type == ParseType.POW:
        return eval_pow(t, env)
    elif t.node_type == ParseType.NEG:
        return eval_neg(t, env)
    elif t.node_type in (ParseType.IF, ParseType.IFELSE):
        return eval_branch(t, env)
    elif t.node_type == ParseType.LT:
        return eval_lt(t, env)
    elif t.node_type == ParseType.ET:
        return eval_et(t, env)
    elif t.node_type == ParseType.PRINT:
        return eval_print(t, env)
    elif t.node_type == ParseType.CALL:
        return eval_call(t, env)
    elif t.node_type == ParseType.RETURN:
        return eval_return(t, env)
    elif t.node_type == ParseType.NE:
        return eval_ne(t, env)
    elif t.node_type == ParseType.LTE:
        return eval_lte(t, env)
    elif t.node_type == ParseType.GT:
        return eval_gt(t, env)
    elif t.node_type == ParseType.GTE:
        return eval_gte(t, env)
    elif t.node_type == ParseType.ARRAY:
        return eval_array(t, env)
    elif t.node_type == ParseType.BLOCK:
        return eval_block(t, env)
    elif t.node_type == ParseType.STATEMENT:
        return eval_statement(t, env)
    elif t.node_type == ParseType.WHILE:
        return eval_while(t, env)
    elif t.node_type == ParseType.IMPORT:
        return eval_import(t, env)
    elif t.node_type == ParseType.SPLIT:
        return eval_split(t, env)
    elif t.node_type == ParseType.STATEMENT_LIST:
        return eval_statement_list(t, env)
    elif t.node_type == ParseType.PARAMLIST:
        return eval_paramlist(t, env)
    elif t.node_type == ParseType.BREAK:
        return eval_break(t, env)
    elif t.node_type == ParseType.READ:
        return eval_read(t, env)
    elif t.node_type == ParseType.ARGLIST:
        return eval_arglist(t, env)
    elif t.node_type == ParseType.REFLIST:
        return eval_reflist(t, env)
    elif t.node_type == ParseType.REF:
        return eval_ref(t, env)
    elif t.node_type == ParseType.DEF:
        return eval_def(t, env)
    elif t.node_type == ParseType.BOUNDS:
        return eval_bounds(t, env)
    elif t.node_type == ParseType.SWAP:
        return eval_swap(t, env)


def eval_program(t, env):
  """
  Evaluate the program
  """
  fun_result = None
  for c in t.children:
    result = eval_parse_tree(c, env)

    # remember any non-none result
    if result is not None:
      fun_result = result

    # check to see if we have returned
    if env.return_value is not None:
      return env.return_value

    # no break here
  return fun_result

    
def eval_atomic(t, env):
  """
  Evaluate the atomic value.
  """
  # get literals
  if t.token.token in (Token.INTLIT, Token.FLOATLIT, Token.STRINGLIT, Token.CHARLIT):
    return t.token.value                     
  elif (t.token.token == Token.CHARACTER) or (t.token.token == Token.STRING) or (t.token.token == Token.BOOL) or (t.token.token == Token.NUMBER):
    bind(env, t.children[0].token.lexeme, Ref(RefType.ID, None))
  else:
      
  # get the variable
    v = env.lookup(t.token.lexeme)
    if not v:
      print(f"Undefined variable {t.token.lexeme} on line {t.token.line}")
      sys.exit(-1)
    elif v.ref_type != RefType.ID:
      print(f"{t.token.lexeme} on line {t.token.line} is not a variable.")
      sys.exit(-1)
    return v.ref_value


def bind(env, name, ref):
  """
    Bind the name in env to ref according to the correct scope
    resolution rules. DOES IT WORK FOR ARRAYS?
    """
  v = env.lookup(env)
  if v:
    # rebind to an existing name
    v.ref_value = ref.ref_value
    v.ref_type = ref.ref_type
  else:
    env.insert(name, ref)

      
def eval_read(t, env): 
  """
    Evaluate an input statement
    """
  for c in t.children[0].children:
    if len(c.children) == 1:
      x = c.children[0].token.lexeme
      value = env.lookup(x)
      if (type(value.ref_value) == list) and (type(value.ref_value[0]) == list):
        for i in range(0, len(value.ref_value)):
          for y in range(0, len(value.ref_value[i])):
            value2 = input(x + "[" + str(i) + "," + str(y) + "] := ")
            if value2.isdigit():
              value.ref_value[i][y] = int(value2)
            else:
              try:
                float(value2)
                value.ref_value[i][y] = float(value2)
              except:
                value.ref_value[i][y] = value2
      elif (type(value.ref_value) == list) and (type(value.ref_value[0]) != list):
        for i in range(0, len(value.ref_value)):
          value2 = input(x + "[" + str(i) + "] := ")
          if value2.isdigit():
            value.ref_value[i] = int(value2)
          else:
            try:
              float(value2)
              value.ref_value[i] = float(value2)
            except:
              value.ref_value[i] = value2
      else:
        value3 = input(x + " := ")
        if value3.isdigit(): 
          value.ref_value = int(value3)
        else:
          try:
            float(value3)
            value.ref_value = float(value3)
          except:
            value.ref_value = value3
    else:
      x = c.children[0].token.lexeme
      ind = eval_parse_tree(c.children[1], env)
      if len(ind) == 1:
        value = env.lookup(x)
        value5 = input(x + "[" + str(ind[0]) + "] := ")
        if value5.isdigit():
          value.ref_value[ind[0]] = int(value5)
        else:
          try:
            float(value5)
            value.ref_value[ind[0]] = float(value5)
          except:
            value.ref_value[ind[0]] = value5
      else:
        value = env.lookup(x)
        value5 = input(x + "[" + str(ind[0]) + "," + str(ind[1]) + "] := ") 
        if value5.isdigit():
          value.ref_value[ind[0]][ind[1]] = int(value5)
        else:
          try:
            float(value5)
            value.ref_value[ind[0]][ind[1]] = float(value5)
          except:
            value.ref_value[ind[0]][ind[1]] = value5


def eval_print(t, env):
  """
  Evaluate a print statement
  """
  val = eval_parse_tree(t.children[0], env)
  for i in range(0, len(val)):
    print(str(val[i]))


def eval_assign(t, env): 
  if t.children[0].node_type == ParseType.ARRAY:
     v2 = t.children[0].children[0].token.lexeme 
     ind = eval_parse_tree(t.children[0].children[1], env)
     if len(ind) == 1:
       value = env.lookup(v2)
       value.ref_value[ind[0]] = eval_parse_tree(t.children[1], env)
     else:
       value = env.lookup(v2)
       value.ref_value[ind[0]][ind[1]] = eval_parse_tree(t.children[1], env)
  else:
    value = env.lookup(t.children[0].token.lexeme)
    value.ref_value = eval_parse_tree(t.children[1], env)


def eval_add(t, env): 
  """
    Evaluate an addition operation.           
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False

  # Type checking if right side is ref
  if t.children[1].node_type == ParseType.REF:
    value2 = eval_parse_tree(t.children[1], env)
    if type(value2) not in (int, float):
      execute = False
  else: # Type checking if right side is not ref
    if type(t.children[1].token.value) not in (int, float):
      execute = False
  if execute:
    return eval_parse_tree(t.children[0], env) + eval_parse_tree(t.children[1], env)
  elif not execute:
    print("Cannot add these types.")
    sys.exit(-1)


def eval_sub(t, env):
  """
    Evaluate an subtraction operation.
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False

  # Type checking if right side is ref
  if t.children[1].node_type == ParseType.REF:
    value2 = eval_parse_tree(t.children[1], env)
    if type(value2) not in (int, float):
      execute = False
  else: # Type checking if right side is not ref
    if type(t.children[1].token.value) not in (int, float):
      execute = False

  if execute:
    return eval_parse_tree(t.children[0], env) - eval_parse_tree(t.children[1], env)
  elif not execute:
    print("Cannot subtract these types.")
    sys.exit(-1)
      

def eval_mul(t, env):
  """
    Evaluate an multiplication operation.
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False

  # Type checking if right side is ref
  if t.children[1].node_type == ParseType.REF:
    value2 = eval_parse_tree(t.children[1], env)
    if type(value2) not in (int, float):
      execute = False
  else: # Type checking if right side is not ref
    if type(t.children[1].token.value) not in (int, float):
      execute = False

  if execute:
    return eval_parse_tree(t.children[0], env) * eval_parse_tree(t.children[1], env)
  elif not execute:
    print("Cannot multiply these types.")
    sys.exit(-1)


def eval_div(t, env):
  """
    Evaluate an multiplication operation.
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False
  
  # Type checking if right side is ref
  if t.children[1].node_type == ParseType.REF:
    value2 = eval_parse_tree(t.children[1], env)
    if type(value2) not in (int, float):
      execute = False
    if value2 == 0:
      print(f"Division by 0 on line {t.token.line}.")
      sys.exit(-1)
  else: # Type checking if right side is not ref
    if type(t.children[1].token.value) not in (int, float):
      execute = False
    elif eval_parse_tree(t.children[1], env) == 0:
      print(f"Division by 0 on line {t.token.line}.")
      sys.exit(-1)

  if execute:
    return eval_parse_tree(t.children[0], env) / eval_parse_tree(t.children[1], env)
  elif not execute:
    print("Cannot divide these types.")
    sys.exit(-1)


def eval_pow(t, env):
  """
    Evaluate an exponent operation.
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False

  # Type checking if right side is ref
  if t.children[1].node_type == ParseType.REF:
    value2 = eval_parse_tree(t.children[1], env)
    if type(value2) not in (int, float):
      execute = False
  else: # Type checking if right side is not ref
    if type(t.children[1].token.value) not in (int, float):
      execute = False

  if execute:
    return eval_parse_tree(t.children[0], env)**eval_parse_tree(t.children[1], env)
  elif not execute:
    print("Cannot perform power on these types.")
    sys.exit(-1)


def eval_neg(t, env):
  """
    Evaluate a negation
    """
  execute = True
  # Type checking if left side is ref
  if t.children[0].node_type == ParseType.REF:
    value = eval_parse_tree(t.children[0], env)
    if type(value) not in (int, float):
      execute = False
  else: # Type checking if left side is not ref
    if type(t.children[0].token.value) not in (int, float):
      execute = False

  if execute:
    return -eval_parse_tree(t.children[0], env)
  elif not execute:
    print("Cannot negate this type.")
    sys.exit(-1)


def eval_branch(t, env):
  """
    Evaluate a branch
    """
  if eval_parse_tree(t.children[0], env):
    eval_parse_tree(t.children[1], env)
  elif t.node_type == ParseType.IFELSE:
    eval_parse_tree(t.children[2], env)


def eval_gte(t, env):
  """
    Evaluate >= operation
    """
  return eval_parse_tree(t.children[0], env) >= eval_parse_tree(
    t.children[1], env)


def eval_lte(t, env):
  """
    Evaluate <= operation
    """
  return eval_parse_tree(t.children[0], env) <= eval_parse_tree(
    t.children[1], env)


def eval_gt(t, env):
  """
    Evaluate > operation
    """
  return eval_parse_tree(t.children[0], env) > eval_parse_tree(
    t.children[1], env)


def eval_lt(t, env):
  """
    Evaluate < operation
    """
  return eval_parse_tree(t.children[0], env) < eval_parse_tree(
    t.children[1], env)


def eval_et(t, env):
  """
    Evaluate < operation
    """
  return eval_parse_tree(t.children[0],
                         env) == eval_parse_tree(t.children[1], env)


def eval_ne(t, env):
  """
    Evaluate ~= operation
    """
  return eval_parse_tree(t.children[0], env) != eval_parse_tree(
    t.children[1], env)


def eval_def(t, env):
  """
    Define a function
    """
  name = t.children[0].children[0].token.lexeme
  env.insert(name, Ref(RefType.FUNCTION, t))


def eval_call(t, env): 
  """
    Call a function
    """
  name = t.children[0].token.lexeme
  arglist = eval_parse_tree(t.children[1], env)

  # retrieve the function
  fun = env.lookup(name)
  if not fun:
    print(f"Call to undefined function {name} on line {t.token.line}")
    sys.exit(-1)
  elif fun.ref_type != RefType.FUNCTION:
    print(f"Call to non-function {name} on line {t.token.line}")
    sys.exit(-1)
  fun = fun.ref_value

  # create the local environment
  local = RefEnv(env)

  if fun.children[2].node_type == ParseType.PARAMLIST:  # If there are parameters
    # get the parameter list
    paramlist = eval_parse_tree(fun.children[2], env)

    # verify the parameter list
    if len(arglist) != len(paramlist):
      print(f"Wrong number of parameters to function {name} on line {t.token.line}")
      sys.exit(-1)

    # all parameters are local (by design)
    for i in range(len(paramlist)):
      local.insert(paramlist[i], Ref(RefType.ID, arglist[i]))

    # call the function
    return eval_parse_tree(fun.children[1], local)
  else:  # If there are no parameters
    return eval_parse_tree(fun.children[1], local)


def eval_return(t, env):
  """
    Evaluate Return
    """
  env.return_value = eval_parse_tree(t.children[0], env)
  return env.return_value

def eval_break(t, env):
  """
  Evaluate break. 
  """
  
  env.break_val = True


def eval_array(t, env):
  """
    Evaluate ARRAY What about the unbounded ones
    """
  name = t.children[0].children[0].token.lexeme
  bounds = eval_parse_tree(t.children[1], env)

  if len(bounds) == 1:
    value2 = [None] * bounds[0]
    bind(env, name, Ref(RefType.ID, value2))
  else:
    value3 = [[None] * bounds[1] for i in range(bounds[0])]
    bind(env, name, Ref(RefType.ID, value3))


def eval_while(t, env):
  """
    Evaluate WHILE
    """
  while eval_parse_tree(t.children[0], env) and not env.break_val:
    eval_parse_tree(t.children[1], env)
  env.break_val = False
      
def eval_import(t, env):
  """
    Evaluate IMPORT
    """
  f = open(eval_parse_tree(t.children[0], env), 'r')
  contents = f.read()
  f.close()
  return contents


def eval_split(t, env):
  """
    Evaluate SPLIT
    """
  return eval_parse_tree(t.children[0],
                         env).split(eval_parse_tree(t.children[1], env))


def eval_block(t, env):
  #leads to statement list
  fun_result = None
  for c in t.children:
    if env.break_val:                                                                   
       return fun_result  
    result = eval_parse_tree(c, env)

    if result is not None:
      fun_result = result

  return fun_result

def eval_statement(t, env):
  """
    Evaluate Statement
    """
  if not env.break_val:                                                                   
     return eval_parse_tree(t.children[0], env)                                           
  return  


def eval_statement_list(t, env):
  """
    Evaluate Statement_list
    """
  fun_result = None
  for c in t.children:
    if env.break_val:                                                                     
       return
    result = eval_parse_tree(c, env)
    # remember any non-none result
    if result is not None:
      fun_result = result

    # check to see if we have returned
    if env.return_value is not None:
      return env.return_value

  return fun_result

def eval_paramlist(t, env): 
  fun_result = []
  for c in t.children:
    fun_result.append(c.children[0].token.lexeme)

  return fun_result


def eval_arglist(t, env): 
  fun_result = []
  for c in t.children:
    result = eval_parse_tree(c, env)

    if result is not None:
      fun_result.append(result)
      
  return fun_result


def eval_reflist(t, env):  
  
  fun_result = []
  for c in t.children:
    result = eval_parse_tree(c, env)

    if result is not None:
      fun_result.append(result)

  return fun_result


def eval_ref(t, env):  
  if len(t.children) == 2:
    v = t.children[0].token.lexeme
    arglist = eval_parse_tree(t.children[1], env)
    if len(arglist) == 2:
      bigval = env.lookup(v)
      value2 = bigval.ref_value[arglist[0]][arglist[1]]
      return value2
    else:
      bigval2 = env.lookup(v)
      value22 = bigval2.ref_value[arglist[0]]
      return value22
  else:
    return eval_parse_tree(t.children[0], env)


def eval_bounds(t, env):  
  fun_result = []
  for c in t.children:
    result = eval_parse_tree(c, env)

    if result is not None:
      fun_result.append(result)

  return fun_result


def eval_swap(t, env): 

  # lookup to ref objects and swap the ref values
  value = t.children[0]
  value2 = t.children[1]

  if ((len(value.children) == 1) and (len(value2.children) == 1)):
    name1 = value.children[0].token.lexeme
    name1_val = env.lookup(name1)

    name2 = value.children[1].token.lexeme
    name2_val = env.lookup(name2)

    temp = name2_val.ref_value
    name2_val.ref_value = name1_val.ref_value
    name1_val.ref_value = temp


if __name__ == "__main__":
  if len(sys.argv) == 2:
    f = open(sys.argv[1])
    l = Lexer(f)
  else:
    l = Lexer()
  parser = Parser(l)
  pt = parser.parse()
  eval_parse_tree(pt, RefEnv())
