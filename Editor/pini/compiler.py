# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import copy
from slpp import slpp
sys.path.insert(0,"../..")

from ply import *
from ply import lex
from ply import yacc

from types import *
from PySide.QtCore import *
import re
import os
import json

from prof import Prof

##### Lexer ######
import decimal
import ATL

class PiniError(Exception):
	# 문법 오류를 핸들링합니다.
	def __init__(self,token,lineno,message):
		self.lexToken = token
		self.lineno = lineno
		self.message = message

	def __str__(self):
		return self.message

class PiniSyntaxError(PiniError):
	def __init__(self,token,message):
		super(PiniSyntaxError,self).__init__(token,token.lineno,message)

class PiniIndentationError(PiniError):
	# 들어쓰기 오류를 핸들링합니다.
	def __init__(self,token,message):
		super(PiniIndentationError,self).__init__(token,token.lineno,message)

class PiniInvalidMacroInstError(PiniError):
	def __init__(self,lineno,message):
		super(PiniInvalidMacroInstError,self).__init__(None,lineno,message)

class PiniCannotFormulaOnAnimationError(PiniError):
	# 애니메이션 중 수식사용 오류를 핸들링합니다.
	def __init__(self,lineno,message):
		super(PiniCannotFormulaOnAnimationError,self).__init__(None,lineno,message)

tokens = (
	'DEF',
	'IF',
	'ELSEIF',
	'ELSE',
	'SAVEDNAME',
	'NAME',
	'NUMBER',  # Python decimals
	'STRING',  # single quoted strings only; syntax of raw strings
	'SUBSTRING',
	'LPAR',
	'RPAR',
	'COLON',
	'EQ',
	'GTEQ',
	'LTEQ',
	'IMPORTANTEQ',
	'ASSIGN',
	'LT',
	'GT',
	'HYPERGT',
	'LLT',
	'LLPAREN',
	'PLUS',
	'MINUS',
	'MULT',
	'DIV',
	'MOD',
	'RETURN',
	'WS',
	'BLPAREN',
	'BRPAREN',
	'NEWLINE',
	'COMMA',
	'INDENT',
	'DEDENT',
	'ENDMARKER',
	'LPAREN',
	'RPAREN',
	'WAVE',
	'IMPORTANT',
	'ATL',
	'ATLNODE',
	'ATLFRAME',
	'ATLLINE',
	'SEMICOLON',
	'ALL',
	'LPARENINSEMI',
	'RPARENINSEMI',
	'DOTLINE'
#	'ITERAL_TRUE',
#	'ITERAL_FALSE'
)

states=(
	("SEMI","exclusive"),
	#("MACRO","inclusive")
)

#t_NUMBER = r'\d+'
# taken from decmial.py but without the leading sign
def t_NUMBER(t):
	r"""(\d+(\.\d*)?|\.\d+)([eE][-+]? \d+)?"""
	t.value = float(t.value)
	return t

def t_STRING(t):
	r'\".*?\"'
	t.value=t.value[1:-1]#.decode("string-escape") # .swapcase() # for fun
	return t

def t_SUBSTRING(t):
	r'\'.*?\''
	t.value=t.value[1:-1]#.decode("string-escape") # .swapcase() # for fun
	t.type = "STRING"
	return t

#{ASD|ASD|ASD}

'''
def t_EXTENDARG(t):
	r'\n\t*?;[^\n]*'
	f = t.value.find(";")
	t.value = t.value[f+1:]
	return t
'''

t_DEF = r'@매크로'
t_ATL = r'@애니메이션'
t_ATLNODE = r'@노드'
t_ATLFRAME = r'@프레임'
t_IF = r'@조건'
t_ELSEIF = r'@다른조건'
t_ELSE = r'@그외'
t_RETURN = r'@돌아가기'
t_WAVE = r"~"
t_IMPORTANT = r"!"
t_COLON = r':'
t_IMPORTANTEQ = r'!='
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'
t_COMMA = r'\|'
#t_AMP = r'\&'
t_ignore = r' '
t_SEMI_ignore = r''

# OR , AND , NOT ,  또는 그리고
# Ply nicely documented how to do this.

RESERVED = {
#	u"": "DEF",
#	u"if": "IF",
#	u"return": "RETURN",
}

#############################
#SEMI STATE
def t_SEMICOLON(t):
	r';'
	t.lexer.push_state("SEMI")
	t.value = "\\n"
	return t

def t_DOTLINE(t):
	r','
	t.lexer.push_state("SEMI")
	t.value = ""
	t.type = "SEMICOLON"
	return t

def t_SEMI_LLT(t):
	r'<<'
	t.type = "ALL"
	t.value = "<"
	return t

def t_SEMI_LLPAREN(t):
	r'\[\['
	t.type = "ALL"
	t.value = "["
	return t

def t_SEMI_ALL(t):
	r'.'
	if t.value == u"[" : 
		t.lexer.mparen_count += 1
		t.lexer.push_state("INITIAL")
		t.type = "LPARENINSEMI"
	elif t.value == u"<" : 
		t.lexer.push_state("INITIAL")
		t.type = "LT"
	return t;

def t_EQ(t):
	r'=='
	return t

def t_GTEQ(t):
	r'>='
	return t

def t_LTEQ(t):
	r'<='
	return t
	
def t_LT(t):
	r'<'
	return t

def t_HYPERGT(t):
	r'>>' 
	return t

def t_GT(t):
	r'>'
	if len(t.lexer.lexstatestack) > 0 : 
		if t.lexer.lexstatestack[-1] == "SEMI" : 
			t.lexer.pop_state()
	return t



def t_NAME(t):
	r'[a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ][a-zA-Z_0-9가-힣ㄱ-ㅎㅏ-ㅣ.]*'
	t.type = RESERVED.get(t.value, "NAME")
	if t.value == u"참" : 
		t.type = "NUMBER"
		t.value = 1
	elif t.value == u"거짓" :  
		t.type = "NUMBER"
		t.value = 0
	elif t.value == u"또는" :
		t.type = "PLUS"
		t.value = '+'
	elif t.value == u"그리고" :  
		t.type = "MULT"
		t.value = '*'
	return t

def t_SAVEDNAME(t):
	r'\$[a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ][a-zA-Z_0-9가-힣ㄱ-ㅎㅏ-ㅣ.]*'
	t.type = RESERVED.get(t.value, "SAVEDNAME")
	return t

def t_ATLLINE(t):
	r'\&[a-zA-Z_가-힣ㄱ-ㅎㅏ-ㅣ][a-zA-Z_0-9가-힣ㄱ-ㅎㅏ-ㅣ.]*'
	t.type = RESERVED.get(t.value, "ATLLINE")
	return t

# Putting this before t_WS let it consume lines with only comments in
# them so the latter code never sees the WS part.  Not consuming the
# newline.  Needed for "if 1: #comment"
def t_comment(t):
	r"[ ]*\043[^\n]*"  # \043 is '#'
	pass

# Whitespace
def t_WS(t):
	r'\t+'
	if t.lexer.at_line_start and t.lexer.paren_count == 0 and t.lexer.bparen_count == 0 and t.lexer.mparen_count == 0:
		return t

# Don't generate newline tokens when inside of parenthesis, eg
#   a = (1, 
#	2, 3)
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	t.type = "NEWLINE"
	if t.lexer.paren_count == 0 and t.lexer.bparen_count == 0 and t.lexer.mparen_count == 0:
		return t

def t_SEMI_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	t.type = "NEWLINE"
	t.lexer.pop_state()
	#if t.lexer.paren_count == 0 and t.lexer.bparen_count == 0 and t.lexer.mparen_count == 0:
	return t

##################
def t_LPAR(t):
	r'\('
	t.lexer.paren_count += 1
	return t

def t_RPAR(t):
	r'\)'
	t.lexer.paren_count -= 1
	return t
##################
def t_LPAREN(t):
	r'\['
	t.lexer.mparen_count += 1
	return t

def t_RPAREN(t):
	r'\]'
	t.lexer.mparen_count -= 1
	if len(t.lexer.lexstatestack) > 0 : 
		if t.lexer.lexstatestack[-1] == "SEMI" :
			t.type = "RPARENINSEMI" 
			t.lexer.pop_state()
	return t
##################
def t_BLPAREN(t):
	r'\{'
	t.lexer.bparen_count += 1
	return t

def t_BRPAREN(t):
	r'\}'
	t.lexer.bparen_count -= 1
	return t
##################

def t_error(t):
	raise PiniSyntaxError(t,"Unknown symbol %r" % (t.value[0],))
	print "Skipping", repr(t.value[0])
	t.lexer.skip(1)

def t_SEMI_error(t):
	raise PiniSyntaxError(t,"SEMI STATE >>> Unknown symbol %r" % (t.value[0],))
	print "SEMI STATE >>> Skipping", repr(t.value[0])
	t.lexer.skip(1)

## I implemented INDENT / DEDENT generation as a post-processing filter

# The original lex token stream contains WS and NEWLINE characters.
# WS will only occur before any other tokens on a line.

# I have three filters.  One tags tokens by adding two attributes.
# "must_indent" is True if the token must be indented from the
# previous code.  The other is "at_line_start" which is True for WS
# and the first n*o*n-WS/n*o*n-NEWLINE on a line.  It flags the check so
# see if the new line has changed indication level.

# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent
NO_INDENT   = 0
MAY_INDENT  = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line
def track_tokens_filter(lexer, tokens):
	lexer.at_line_start = at_line_start = True
	indent = NO_INDENT
	saw_colon = False
	for token in tokens:
		token.at_line_start = at_line_start

		if token.type == "COLON":
			at_line_start = False
			indent = MAY_INDENT
			token.must_indent = False
			
		elif token.type == "NEWLINE":
			at_line_start = True
			if indent == MAY_INDENT:
				indent = MUST_INDENT
			token.must_indent = False

		elif token.type == "WS":
			assert token.at_line_start == True
			at_line_start = True
			token.must_indent = False

		else:
			# A real token; only indent after COLON NEWLINE
			if indent == MUST_INDENT:
				token.must_indent = True
			else:
				token.must_indent = False
			at_line_start = False
			indent = NO_INDENT

		yield token
		lexer.at_line_start = at_line_start

def _new_token(type, lineno):
	tok = lex.LexToken()
	tok.type = type
	tok.value = None
	tok.lineno = lineno
	return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
	return _new_token("DEDENT", lineno)

# Synthesize an INDENT tag
def INDENT(lineno):
	return _new_token("INDENT", lineno)

# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
	# A stack of indentation levels; will never pop item 0
	levels = [0]
	token = None
	depth = 0
	prev_was_ws = False
	for token in tokens:

		if token.type == "WS":
			assert depth == 0
			depth = len(token.value)
			prev_was_ws = True
			# WS tokens are never passed to the parser
			continue

		if token.type == "NEWLINE":
			depth = 0
			if prev_was_ws or token.at_line_start:
				# ignore blank lines
				continue
			# pass the other cases on through
			yield token
			continue

		prev_was_ws = False
		if token.must_indent:
			# The current depth must be larger than the previous level
			if not (depth > levels[-1]):
				raise PiniIndentationError(token,"expected an indented block")

			levels.append(depth)
			yield INDENT(token.lineno)

		elif token.at_line_start:
			# Must be on the same level or one of the previous levels
			if depth == levels[-1]:
				# At the same level
				pass
			elif depth > levels[-1]:
				raise PiniIndentationError(token,"indentation increase but not in new block")
			else:
				# Back up; but only if it matches a previous level
				try:
					i = levels.index(depth)
				except ValueError:
					raise PiniIndentationError(token,"inconsistent indentation")
				for _ in range(i+1, len(levels)):
					yield DEDENT(token.lineno)
					levels.pop()

		yield token

	### Finished processing ###

	# Must dedent any remaining levels
	if len(levels) > 1:
		assert token is not None
		for _ in range(1, len(levels)):
			yield DEDENT(token.lineno)
	

# The top-level filter adds an ENDMARKER, if requested.
# Python's grammar uses it.
def filter(lexer, add_endmarker = True):
	token = None
	tokens = iter(lexer.token, None)
	tokens = track_tokens_filter(lexer, tokens)
	for token in indentation_filter(tokens):
		yield token

	if add_endmarker:
		lineno = 1
		if token is not None:
			lineno = token.lineno
		yield _new_token("ENDMARKER", lineno)

# Combine Ply and my filters into a new lexer

class IndentLexer(object):
	def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
		print debug, optimize, lextab,reflags
		self.lexer = lex.lex(debug=debug, optimize=optimize, lextab=lextab, reflags=reflags)
		self.token_stream = None
	def input(self, s, add_endmarker=True):
		self.lexer.paren_count = 0
		self.lexer.mparen_count = 0
		self.lexer.bparen_count = 0
		self.lexer.input(s)
		self.token_stream = filter(self.lexer, add_endmarker)
	def token(self):
		try:
			return self.token_stream.next()
		except StopIteration:
			return None

##########   Parser   ######
# The grammar comments come from Python's Grammar/Grammar file

## NB: compound_stmt in single_input is followed by extra NEWLINE!
# file_input: (NEWLINE | stmt)* ENDMARKER
def p_file_input_end(p):
	"""file_input_end : file_input ENDMARKER"""
	p[0] = p[1]
def p_file_input(p):
	"""file_input : file_input NEWLINE
				  | file_input stmt
				  | NEWLINE
				  | stmt"""
	if isinstance(p[len(p)-1], basestring):
		if len(p) == 3:
			p[0] = p[1]
		else:
			p[0] = [] # p == 2 --> only a blank line
	else:
		if len(p) == 3:
			p[0] = p[1] + p[2]
		else:
			p[0] = p[1]
			
# funcdef: [decorators] 'def' NAME parameters ':' suite
# ignoring decorators
def p_funcdef(p):
	'funcdef : DEF NAME COLON suite'
	p[0] = {"type":"funcdef", "name":p[2], "stmts":p[4] ,"ln":p.lineno(1)}

def p_atl_stmts(p):
	'''
	atl_stmts : ATL NAME COLON atl_node_suite
	'''
	p[0] = {"type":"atl","nodes":p[4],"name":p[2],"ln":p.lineno(1)}

def p_atl_node(p):
	'''
	atl_node_stmt : ATLNODE NUMBER COLON atl_frame_suite
	'''
	p[0] = {"type":"atl_node","frames":p[4],"idx":p[2],"ln":p.lineno(1)}

def p_atl_frame(p):
	'''
	atl_frame_stmt : ATLFRAME NUMBER COLON atl_suite
	'''
	p[0] = {"type":"atl_frame","frame":p[2],"stmts":p[4],"ln":p.lineno(1)}
# power: atom trailer* ['**' factor]
# trailers enables function calls.  I only allow one level of calls
# so this is 'trailer'

def p_power_in_semi(p):
	"""
	power : LPARENINSEMI atom trailers RPARENINSEMI
		  | LPARENINSEMI atom RPARENINSEMI
	"""
	args = None
	if len(p) == 5 : 
		args = p[3]

	p[0] = {"type":"call_function","typeof":"var","native":False,"v":"return_temp","name":p[2],"args":args,"insemi":True,"ln":p.lineno(1)}

def p_power(p):
	"""power : atom
			 | LPAREN atom trailers RPAREN
			 | LPAREN atom RPAREN
			 | LPAREN LPAREN atom RPAREN RPAREN"""
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 6 :
		p[0] = {"type":"call_function","native":True,"typeof":"var","args":None,"name":p[3],"ln":p.lineno(1)}
	else:
		args = None
		if len(p) == 5 : 
			args = p[3]

		p[0] = {"type":"call_function","native":False,"typeof":"var","v":"return_temp","name":p[2],"args":args,"ln":p.lineno(1)}

# trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
def p_trailers(p):
	'''
	trailers : trailers trailer
			 | trailer
	'''
	if len(p) == 2 : 
		p[0] = [p[1]]
	else:
		p[0] = p[1] + [p[2]]

def p_trailer(p):
	'trailer : expr_stmt'
	p[0] = p[1]

# varargslist: (fpdef ['=' test] ',')* ('*' NAME [',' '**' NAME] | '**' NAME) | 
# highly simplified
def p_varargslist(p):
	"""varargslist : varargslist COMMA NAME
				   | NAME"""
	if len(p) == 4:
		p[0] = p[1] + p[3]
	else:
		p[0] = [p[1]]

# stmt: simple_stmt | compound_stmt
def p_stmt_simple(p):
	"""stmt : simple_stmt"""
	# simple_stmt is a list
	p[0] = p[1]

def p_stmt_compound(p):
	"""stmt : compound_stmt"""
	p[0] = [p[1]]

# simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
def p_simple_stmt(p):
	"""simple_stmt : small_stmts NEWLINE"""
	p[0] = p[1]

def p_small_stmts(p):
	"""small_stmts : small_stmts small_stmt
				   | small_stmt"""
	if len(p) == 3:
		p[0] = p[1] + [p[2]]
	else:
		p[0] = [p[1]]

# small_stmt: expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
#	import_stmt | global_stmt | exec_stmt | assert_stmt
def p_small_stmt(p):
	"""small_stmt : flow_stmt
				  | trailer
				  | goto
				  | markup_stmt
				  | words
				  | hypergoto
				  | bookmark
				  | funcinfo
				  | autocomplete"""
	p[0] = p[1]

def p_atl_line_stmts(p):
	"""
	atl_line_stmts : atl_line_stmts atl_line_stmt
				   | atl_line_stmt
	"""
	if len(p) == 3:
		p[0] = p[1] + [p[2]]
	else:
		p[0] = [p[1]]


def p_atl_line_stmt(p):
	"""atl_line_stmt : atl_line"""
	p[0] = p[1]


# expr_stmt: testlist (augassign (yield_expr|testlist) |
#					  ('=' (yield_expr|testlist))*)
# augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
#			 '<<=' | '>>=' | '**=' | '//=')
def p_expr_stmt(p):
	"""expr_stmt : testlist ASSIGN testlist
				 | testlist """
	if len(p) == 2:
		# a list of expressions
		p[0] = p[1]
	else:
		#p[0] = Assign(p[1], p[3])
		p[0] = {"type":"assign","l":p[1],"r":p[3],"ln":p.lineno(2)}

def p_flow_stmt(p):
	"flow_stmt : return_stmt"
	p[0] = p[1]

# return_stmt: 'return' [testlist]
def p_return_stmt(p):
	'''
	return_stmt : RETURN testlist
				| RETURN
	'''
	if len(p) == 3 : 
		p[0] = {"type":"return","v":p[2],"ln":p.lineno(1)}
	else:
		p[0] = {"type":"return","v":None,"ln":p.lineno(1)}

def p_compound_stmt(p):
	"""compound_stmt : if_stmt
					 | funcdef
					 | atl_stmts"""
	p[0] = p[1]

def p_if_stmt(p):
	'''
	if_stmt : IF test COLON suite
			| if_stmt if_else_stmt
			| if_stmt else_stmt
	'''
	if len(p) == 5 : 
		p[0] = {"type":"if", "test":p[2], "stmts":p[4] ,"elseif":[], "else":None, "ln":p.lineno(1)}
	else:
		if p[2]["type"] == "elseif" : 
			p[1]["elseif"].append(p[2])
		else:
			p[1]["else"] = p[2]
		p[0] = p[1]

def p_if_else_stmt(p):
	'''
	if_else_stmt : if_else_stmt suite
				 | ELSEIF test COLON 
	'''
	#p[0] = {"type":"elseif", "test":p[2], "stmts":p[4] }
	if len(p) == 4 : 
		p[0] = {"type":"elseif", "test":p[2], "stmts":[] ,"ln":p.lineno(1)}
	else : 
		p[1]["stmts"] = p[2]
		p[0] = p[1]

def p_else_stmt(p):
	'''
	else_stmt : else_stmt suite
			  | ELSE COLON 
	'''
	if isinstance(p[1],unicode) : 
		p[0] = {"type":"else", "stmts":[] ,"ln":p.lineno(1)}
	else:
		p[1]["stmts"] = p[2]
		p[0] = p[1]

def p_atl_node_suite(p):
	'''
	atl_node_suite : NEWLINE INDENT atl_node_stmts DEDENT
	'''
	p[0] = p[3]

def p_atl_node_stmts(p):
	'''
	atl_node_stmts : atl_node_stmts atl_node_stmt
				   | atl_node_stmt 
	'''
	if len(p) == 3:
		p[0] = p[1] + [p[2]]
	else:
		p[0] = [p[1]]

def p_atl_frame_suite(p):
	'''
	atl_frame_suite : NEWLINE INDENT atl_frame_stmts DEDENT
	'''
	p[0] = p[3]

def p_atl_frame_stmts(p):
	'''
	atl_frame_stmts : atl_frame_stmts atl_frame_stmt
					| atl_frame_stmt
	'''
	if len(p) == 3:
		p[0] = p[1] + [p[2]]
	else:
		p[0] = [p[1]]

def p_suite(p):
	"""suite : NEWLINE INDENT stmts DEDENT"""
	p[0] = p[3]

def p_stmts(p):
	"""stmts : stmts stmt
			 | stmt"""
	if len(p) == 3:
		p[0] = p[1] + p[2]
	else:
		p[0] = p[1]

def p_atl_suite(p) : 
	"""
	atl_suite : NEWLINE INDENT atl_line_stmts DEDENT
	"""
	p[0] = p[3]

def p_atl_line(p):
	'''
	atl_line : ATLLINE comparison NAME NAME NEWLINE
			 | ATLLINE comparison NAME NEWLINE
			 | ATLLINE comparison NEWLINE
	'''
	p[1] = p[1][1:]
	if len(p) == 6 : 
		p[0] = {"type":"atl_line","name":p[1],"v":p[2],"op1":p[3],"op2":p[4],"ln":p.lineno(1)}
	elif len(p) == 5 : 
		p[0] = {"type":"atl_line","name":p[1],"v":p[2],"op1":p[3],"op2":None,"ln":p.lineno(1)}
	elif len(p) == 4 : 
		p[0] = {"type":"atl_line","name":p[1],"v":p[2],"op1":None,"op2":None,"ln":p.lineno(1)}
## No using Python's approach because Ply supports precedence

# comparison: expr (comp_op expr)*
# arith_expr: term (('+'|'-') term)*
# term: factor (('*'|'/'|'%'|'//') factor)*
# factor: ('+'|'-'|'~') factor | power
# comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
precedence = (
	("nonassoc", "EQ", "GT", "LT","GTEQ","LTEQ","IMPORTANTEQ"),
	("left", "PLUS", "MINUS"),
	("left", "MULT", "DIV", "MOD"),
	("right", "UMINUS","UNOT"),
)

def p_def_argu(p):
	"funcinfo : IMPORTANT atom atom"
	info = []
	if len(p[3]["v"]) > 1 : 
		info = p[3]["v"][1:]
	p[0] = {"type":"funcInfo", "name":p[2],"explain":p[3]["v"][0], "info":info}


def p_markup_stmt(p):
	"""
	markup_stmt : markup GT
	"""
	if len(p) == 3 :
		p[0] = p[1]

def p_comparison(p):
	"""
	comparison : comparison LT comparison
			   | comparison EQ comparison
			   | comparison GT comparison
			   | comparison GTEQ comparison
			   | comparison LTEQ comparison
			   | comparison IMPORTANTEQ comparison
			   | comparison PLUS comparison
			   | comparison MINUS comparison
			   | comparison MULT comparison
			   | comparison DIV comparison
			   | comparison MOD comparison
			   | PLUS comparison
			   | MINUS comparison %prec UMINUS
			   | IMPORTANT comparison %prec UNOT
			   | power
	"""
	if len(p) == 4:
		t1,t2 = p[1]["typeof"],p[3]["typeof"]
		v1,v2 = p[1]["v"],p[3]["v"]
		value = v1
		_type = t1
		if t2 == "var" : 
			_type = t2

		if t1 == "number" and t2 == "number":
			if p[2] == '+':
				value = v1+v2
			elif p[2] == '-':
				value = v1-v2
			elif p[2] == '*':
				value = v1*v2
			elif p[2] == '/':
				value = v1/v2
			elif p[2] == '%':
				value = v1%v2
			elif p[2] == '==':
				value = v1==v2
			elif p[2] == '>':
				value = v1>v2
			elif p[2] == '<':
				value = v1<v2
			elif p[2] == '>=':
				value = v1>=v2
			elif p[2] == '<=':
				value = v1<=v2
			elif p[2] == '!=':
				value = v1!=v2

		elif t1 == "var" or t2 == "var" : 
			value = (p[1],p[2],p[3])

		elif t1 == "string" or t2 == "string":
			if p[2] == '+':
				if isinstance(v1,float) : 
					if v1 == int(v1) : 
						v1 = int(v1)
					v1 = str(v1)
				if isinstance(v2,float) : 
					if v2 == int(v2) : 
						v2 = int(v2) 
					v2 = str(v2)
				value = v1+v2
			elif p[2] == '==':
				value = v1==v2
			elif p[2] == '!=':
				value = v1!=v2
			_type = "string"

		p[0] = {"type":"comparison","typeof":_type,"v":value,"ln":p.lineno(2)}
	elif len(p) == 3:
		if p[2]["typeof"] == "number" : 
			if p[1] == "+" : 
				p[2]["v"] = 1*float(p[2]["v"])
			elif p[1] == "-" : 
				p[2]["v"] = -1*float(p[2]["v"])
			elif p[1] == "!" : 
				p[2]["v"] = not float(p[2]["v"])

			p[0] = {"type":"comparison","typeof":p[2]["typeof"],"v":p[2]["v"],"ln":p.lineno(1)}
		elif p[2]["typeof"] == "string" :
			if len(p[2]["v"]) > 0 :
				p[0] = {"type":"comparison","typeof":p[2]["typeof"],"v":False,"ln":p.lineno(1)}
			else:
				p[0] = {"type":"comparison","typeof":p[2]["typeof"],"v":True,"ln":p.lineno(1)}

		elif p[2]["typeof"] == "var" :
			if p[1] == "!" :
				value = ({"type":"comparison","typeof":"number","v":0},"!",p[2])
			else:
				value = ({"type":"comparison","typeof":"number","v":-1},"*",p[2])
			p[0] = {"type":"comparison","typeof":"var","v":value,"ln":p.lineno(1)}
		else:
			p[0] = p[2]
	else:
		p[0] = p[1]

def p_markup(p):
	"""
	markup : markup atom
		   | LT NAME
		   | LT ASSIGN NAME
		   | LT ASSIGN SAVEDNAME
		   | LT DIV NAME
	"""
	if len(p) == 4 :
		if p[2] == u"=" :  
			p[0] = {"type":"markup","class":p[2],"args":[{"v":p[3]}],"ln":p.lineno(1)}
		else : 
			p[0] = {"type":"markup","class":p[2],"args":[{"v":p[3]}],"ln":p.lineno(1)}
	else:
		if p[1] == u"<" : 
			p[0] = {"type":"markup","class":p[2],"args":[],"ln":p.lineno(1)}
		else:
			p[1]["args"] += [p[2]]
			p[0] = p[1]

def p_bookmark(p):
	"bookmark : COLON NAME"
	p[0] = {"type":"bookmark","name":{"type":"atom","typeof":"var","v":p[2]},"ln":p.lineno(2)}

def p_goto(p):
	"goto : GT NAME"
	p[0] = {"type":"goto","name":{"type":"atom","typeof":"var","v":p[2]},"ln":p.lineno(2)}

def p_hypergoto(p):
	"hypergoto : HYPERGT NAME"
	p[0] = {"type":"hypergoto","name":{"type":"atom","typeof":"var","v":p[2]},"ln":p.lineno(2)}

def p_atom_pick_array(p):
	"atom : atom LPAREN atom RPAREN"
	p[0] = {"type":"atom","typeof":"var","v":{"idx":p[3],"v":p[1]}}

def p_atom_name(p):
	"""atom : NAME"""
	p[0] = {"type":"atom","typeof":"var","v":p[1],"ln":p.lineno(1)}

def p_atom_savedname(p):
	"""atom : SAVEDNAME"""
	p[0] = {"type":"atom","typeof":"var","save":True,"v":p[1]}

def p_atom_number(p):
	"atom : NUMBER"
	p[0] = {"type":"atom","typeof":"number","v":p[1],"ln":p.lineno(1)}

def p_atom_string(p):
	"atom : STRING"
	p[0] = {"type":"atom","typeof":"string","v":p[1],"ln":p.lineno(1)}

def p_atom_cal_bind(p):
	"""
	atom : LPAR testlist RPAR
		 | LPAR RPAR
	"""
	v = {}
	if len(p) == 4 : 
		v = p[2]
	p[0] = v

def p_atom_tuple(p):
	"""
	atom : BLPAREN testlist BRPAREN
		 | BLPAREN BRPAREN
	"""
	v = {}
	if len(p) == 4 : 
		v = p[2]
	p[0] = {"type":"atom","typeof":"list","v":v}

# testlist: test (',' test)* [',']
# Contains shift/reduce error
def p_testlist(p):
	"""testlist : testlist_multi COMMA
				| testlist_multi """
	if len(p) == 2:
		p[0] = p[1]
	else:
		# May need to promote singleton to tuple
		if isinstance(p[1], list):
			p[0] = p[1]
		else:
			p[0] = [p[1]]
	# Convert into a tuple?
	#if isinstance(p[0], list):
	#	p[0] = ast.Tuple(p[0])

def p_words(p):
	"""
	words : words ALL
		  | ALL
		  | SEMICOLON
	"""
	if len(p) == 2 : 
		p[0] = {"type":"word","list":[p[1]],"ln":p.lineno(1)}
	elif len(p) == 3:  
		p[1]["list"] += [p[2]]
		p[0] = p[1]

def p_testlist_multi(p):
	"""testlist_multi : testlist_multi COMMA test
					  | test"""
	if len(p) == 2:
		# singleton
		p[0] = p[1]
	else:
		if isinstance(p[1], list):
			p[0] = p[1] + [p[3]]
		else:
			# singleton -> tuple
			p[0] = [p[1], p[3]]

# test: or_test ['if' or_test 'else' test] | lambdef
#  as I don't support 'and', 'or', and 'not' this works down to 'comparison'
def p_test(p):
	"test : comparison"
	p[0] = p[1]
	
# arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test)
# XXX INCOMPLETE: this doesn't allow the trailing comma
def p_arglist(p):
	"""arglist : arglist COMMA argument
			   | argument"""
	if len(p) == 4:
		p[0] = p[1] + [p[3]]
	else:
		p[0] = [p[1]]

# argument: test [gen_for] | test '=' test  # Really [keyword '='] test
def p_argument(p):
	"argument : test"
	p[0] = p[1]

#### auto complete ####
def p_def_autocomplete(p):
	"""
	autocomplete : WAVE atom atom
	"""
	if p[1] == "~" : 
		p[0] = {"type":"autocomplete","name":p[2],"list":p[3]}

def p_error(p):
	print "Error!", repr(p)
	raise PiniSyntaxError(p,repr(p))

class GardenSnakeParser(object):
	def __init__(self, lexer = None):
		if lexer is None:
			lexer = IndentLexer()
		self.lexer = lexer
		self.parser = yacc.yacc(start="file_input_end")

	def parse(self, code):
		self.lexer.lexer.lineno=-1 # pass 라는 숨겨진 문장이 포함되므로, -1 부터 카운트합니다.

		while len(self.lexer.lexer.lexstatestack) > 0:
			self.lexer.lexer.pop_state()
			
		self.lexer.input(code)
		result = self.parser.parse(lexer = self.lexer)
		return result

def getV(v):
	ret = unicode( "", "utf-8")	
	if v != None:
		if isinstance(v, unicode)==False:
			ret = str(v)
			ret = unicode(ret, "utf-8")
		else:
			ret = v
	return  ret

###### Code generation ######
class LNXCompiler(object):
	def __init__(self):
		self.parser = GardenSnakeParser()
	def compile(self, code, filename="<string>", isActivePreProcess=True):
		# pre-process
		if isActivePreProcess:
			try:
				from controller.ProjectController import ProjectController
				for define in ProjectController().defines:
					code = code.replace(define[0],define[1])
			except Exception, e:
				pass

		code = code.replace("]<","] <")
		# compile
		tree = self.parser.parse(code)
		return tree

####### Support UTF-8 ############
for k in locals().keys() :
	if k.startswith("t_"):
		v = locals()[k]
		if type(v) == FunctionType : 
			if v.__doc__ :
				locals()[k].__doc__ = unicode(locals()[k].__doc__,"utf-8")
		elif type(v) == StringType:
			locals()[k] = unicode(locals()[k],"utf-8")

####### Optimizer #########
class LNXOptimizer(object) : 
	def __init__(self):
		self.ifcount = 0

	@staticmethod
	def cmd(c):
		if c == "calculate" : 
			return 0
		elif c == "assign" : 
			return 1
		elif c == "ifgoto" : 
			return 2
		elif c == "bookmark" : 
			return 3
		elif c == "goto" : 
			return 4
		elif c == "call" : 
			return 5
		elif c == "funcdef" : 
			return 6
		elif c == "return" : 
			return 7
		elif c == "autocomplete" : 
			return 8
		elif c == "funcInfo" : 
			return 9
		elif c == "animation" : 
			return 10
		elif c == "hypergoto" : 
			return 11
		elif c == "word" : 
			return 12
		elif c == "markup" : 
			return 13

	def new_value(self,value,isOptimize=True):
		typeof = "number"
		if type(value) == StringType : 
			typeof = "string"
		elif type(value) == ListType : 
			typeof = "list"
		ret = {
			"type":"atom",
			"typeof":typeof,
			"v":value,
		}
		if isOptimize : 
			return self.optimize_atom(ret)
		else:
			return ret

	def new_const(self,name,value,ln):
		var = self.optimize_atom({
			"type":"atom",
			"typeof":"var",
			"v":name,
		})
		r = []
		if not isinstance(value,dict) : 
			value = self.new_value(value)
		else:
			if isinstance(value["v"],tuple) : 
				value = {"t":0,"v":value["v"]}

		r.append(self.operate_assign(var,value,ln))
		return r

	##var type
	# 0 : var # 1 : number # 2 : string
	def optimize_atom(self,o):
		if isinstance(o,dict):
			for k in o.keys():
				self.optimize_atom(o[k])
		elif isinstance(o,tuple) or \
			 isinstance(o,list):
			for v in o:
				self.optimize_atom(v)
		else:
			return o

		if not "type" in o :
			return o

		if o["type"] != "atom" and \
		   o["type"] != "comparison" : 
			return o
		
		o["t"] = 0
		if o["typeof"] == "list":
			o["t"] = 3
		elif o["typeof"] == "string":
			o["t"] = 2
		elif o["typeof"] == "number" : 
			o["t"] = 1

		del o["typeof"]
		del o["type"]
		return o

	def operate_assign(self,left,right,line):
		return {
			"t" : LNXOptimizer.cmd("assign"),
			"L":left,
			"R":right,
			"ln":line,
		}

	def operate_animation(self,v,ln) : 
		def default_line(st):
			_set = 0
			_ease = None
			
			if st["op1"] in ATL.line_increment : 
				_set = ATL.line_increment.index(st["op1"])
			elif st["op1"] in ATL.line_ease :
				_ease = ATL.line_ease.index(st["op1"])

			if st["op2"] in ATL.line_increment : 
				_set = ATL.line_increment.index(st["op2"])
			elif st["op2"] in ATL.line_ease :
				_ease = ATL.line_ease.index(st["op2"])

			if isinstance(st["v"]["v"],tuple) : 
				st["v"]["v"] = st["v"]["v"][0]["v"]

			return {
				"s" : _set,
				"t" : ATL.line_type.index(st["name"]) if st["name"] in ATL.line_type else None,
				"o" : st["v"]["t"],
				"v" : st["v"]["v"],
				"e" : _ease
			}
		for node in v["nodes"] : 
			del node["type"]
			for frame in node["frames"] : 
				fList = []
				for stmt in frame["stmts"] : 
					line = default_line(stmt)
					if line["t"] != None  :
						if line["e"] == None:
							del line["e"]
						fList.append(line)
					if type(line["v"]) == TupleType:
						raise PiniCannotFormulaOnAnimationError(frame["ln"],"Animation target cannot be formula")
				frame["stmts"] = fList
				del frame["type"]
		del v["type"]
		return {
			"t" : LNXOptimizer.cmd("animation"),
			"json" : json.dumps(v,ensure_ascii=False,encoding="utf-8"),
			"ln" : ln
		}

	def operate_bookmark(self,name,line):
		return {
			"t":LNXOptimizer.cmd("bookmark"),
			"name":name["v"],
			"ln":line
		}

	def operate_ifgoto(self,cond,goto,elsename,line):
		if not "v" in goto : 
			goto["v"] = ""
		if not "v" in elsename : 
			elsename["v"] = ""

		return {
			"t":LNXOptimizer.cmd("ifgoto"),
			"cond":cond,
			"goto":goto["v"],
			"else":elsename["v"],
			"ln":line
		}

	def operate_goto(self,goto,line):
		return {
			"t":LNXOptimizer.cmd("goto"),
			"goto":goto,
			"ln":line
		}

	def operate_hypergoto(self,goto,line):
		return {
			"t":LNXOptimizer.cmd("hypergoto"),
			"goto":goto,
			"ln":line
		}

	def operate_call(self,name,args,native,ln):
		return {
			"t":LNXOptimizer.cmd("call"),
			"name":name,
			"args":args,
			"native":native,
			"ln":ln
		}

	def operate_def(self,name,stmts,line):
		return {
			"t":LNXOptimizer.cmd("funcdef"),
			"name":name,
			"stmts":stmts,
			"ln":line
		}

	def operate_return(self,result,line):
		ret = []
		return ret+[{
			"t":LNXOptimizer.cmd("return"),
			"ret":self.optimize_atom(result),
			"ln":line
		}]

	def operate_word(self,strs,ln):
		return {
			"t":LNXOptimizer.cmd("word"),
			"strs":strs,
			"ln":ln,
		}

	def operate_markup(self,cls,args,ln,close=False):
		return {
			"t":LNXOptimizer.cmd("markup"),
			"name":cls,
			"args":[v["v"] for v in args],
			"ln":ln,
			"close":close
		}

	def optimize(self,tree,isInline=False):
		if tree == None:
			return []

		isWordMode = False
		o = []
		def q(a,v):
			if isinstance(v,dict) : 
				a.append(v)
			else:
				try:
					a += v
				except Exception, e:
					print v
					raise e

		for v in tree :
			if isWordMode : 
				if v["type"] != "word" and v["type"] != "markup" :
					if not "insemi" in v :
						ln = v["ln"]
						q(o,self.operate_markup(u"클릭",[],ln))
						#q(o,self.operate_markup(u"클린",[],ln))
						q(o,self.operate_markup(u"대사창사라짐",[],v["ln"]))
						isWordMode = False

			if v["type"] == "atom" or \
			   v["type"] == "comparison" : 
				continue # 단순 변수 사용은 의미가 없음.

			elif v["type"] == "assign" :
				# name이 아닌데 assign하는건 저장되는게 아니니 출력하지 않음.
				l,r = v["l"],v["r"]
				if l["typeof"] == "var" : 
					count = 0

					q(o,self.operate_assign(l["v"],self.optimize_atom(r),v["ln"]))

			elif v["type"] == "if" : 
				_i = str(self.ifcount)
				self.ifcount += 1

				_else = v["elseif"][0] if len(v["elseif"]) > 0 else v["else"]
				_if_end = self.new_value("%if_end_"+_i)
				if _else == None :
					_else = _if_end
				else :
					_else = self.new_value("%else_"+_i+"_0")

				test = self.optimize_atom(v["test"])

				q(o,self.operate_ifgoto(test,{},_else,v["ln"]))
				q(o,self.optimize(v["stmts"]))

				ln = v["stmts"][-1]["ln"]
				q(o,self.operate_goto(_if_end,ln))
				
				count = 0
				for e in v["elseif"] : 
					_else = self.new_value("%else_"+_i+"_"+str(count))
					_next = self.new_value("%else_"+_i+"_"+str(count+1))
					q(o,self.operate_bookmark(_else,e["ln"]))

					test = self.optimize_atom(e["test"])

					q(o,self.operate_ifgoto(test,{},_next,e["ln"]))
					q(o,self.optimize(e["stmts"]))

					ln = e["stmts"][-1]["ln"]
					q(o,self.operate_goto(_if_end,ln))
					
					count += 1
				
				if count > 0 or v["else"] : 
					_else = self.new_value("%else_"+_i+"_"+str(count))
					ln = -1
					if v["else"]:
						ln = v["else"]["ln"]
					q(o,self.operate_bookmark(_else,ln))

				if v["else"] : 
					q(o,self.optimize(v["else"]["stmts"]))

					ln = v["else"]["stmts"][-1]["ln"]

				q(o,self.operate_bookmark(_if_end,ln))

			elif v["type"] == "call_function" : 
				ln = v["ln"]
				q(o,self.operate_call(v["name"]["v"],self.optimize_atom(v["args"]),v["native"],ln))

			elif v["type"] == "funcdef" : 
				q(o,self.operate_def(v["name"],self.optimize(v["stmts"]),v["ln"]))

			elif v["type"] == "atl" : 
				self.optimize_atom(v)
				q(o,self.operate_animation(v,v["ln"]))

			elif v["type"] == "bookmark" : 
				q(o,self.operate_bookmark(v["name"],v["ln"]))
			
			elif v["type"] == "goto" : 
				q(o,self.operate_goto(v["name"],v["ln"]))
			
			elif v["type"] == "hypergoto" : 
				q(o,self.operate_hypergoto(v["name"],v["ln"]))
			
			elif v["type"] == "return" :
				q(o,self.operate_return(v["v"],v["ln"]))
			
			elif v["type"] == "autocomplete" :
				self.optimize_atom(v)
				v["t"] = LNXOptimizer.cmd("autocomplete")
				q(o,v)

			elif v["type"] == "funcInfo" : 
				self.optimize_atom(v)
				v["t"] = LNXOptimizer.cmd("funcInfo")
				q(o,v)

			elif v["type"] == "word" : 
				if not isWordMode :
					q(o,self.operate_markup(u"대사창나타남",[],v["ln"]))
				q(o,self.operate_word(v["list"],v["ln"]))
				isWordMode = True

			elif v["type"] == "markup" : 
				self.optimize_atom(v["args"])
				q(o,self.operate_markup(v["class"],v["args"],v["ln"]))

			else:
				print ">>>>",v["type"]

		if (not isInline) and isWordMode : 
			q(o,self.operate_markup(u"클릭",[],v["ln"]))
			#q(o,self.operate_markup(u"클린",[],v["ln"]))
			q(o,self.operate_markup(u"대사창사라짐",[],v["ln"]))

		return o

###### Lua Linker ######
class LNXLuaLinker(object) : 
	def __init__(self):
		slpp.newline = ''
		slpp.tab = ''
		self.opTable = {
			'==':'==',
			'!=':'~=',
			'<':'<',
			'>':'>',
			'<=':'<=',
			'>=':'>=',
			'!':'!'
		}

	def linking(self,obj,isline=False):
		linked = self._linking(obj)
		if isline : 
			return linked
		return self.lua_header() + linked + self.lua_footer()

	def ARG(self,name,args,rets):
		if args == None:
			return "nil","nil"

		new_ret = "function(rets)\n"
		del_ret = "function()\n"
		for v in args : 
			new_ret += self._G(name+"."+v["l"]["v"]) + " = "+self.ASSIGN_R(v['r'],rets)+"\n"
			del_ret += self._G(name+"."+v["l"]["v"]) +' = nil\n'
		new_ret += "end\n"
		del_ret += "end\n"
		return new_ret,del_ret

	def _G(self,idx):
		return "_LNXG['"+idx+"']"

	def _CALL(self,name,args,rets):
		args = self.ARG(name,args,rets)
		rets.append("_VM_LOOP_('"+name+"',_LNXF['"+name+"'],idx,"+args[0]+","+args[1]+",nil,rets,fcall)")
		return "rets["+str(len(rets))+"]"

	def _V(self,v):
		if v["t"] == 0:
			return "("+self._G(v["v"])+" or 0)"
		if v["t"] == 2:
			return '"'+v["v"]+'"'
		else:
			return str(v["v"])

	def CALCULATE_PART(self,v,rets):
		ret = ""
		if isinstance(v["v"],tuple):
			ret = self.CALCULATE(v["v"][0],v["v"][2],v["v"][1],rets)
		else:
			if "type" in v and v["type"] == "call_function" : 
				ret = self._CALL(v["name"]["v"],v["args"],rets)
			else:
				ret = self._V(v)
		return ret

	def CALCULATE(self,L,R,OP,rets):
		l = self.CALCULATE_PART(L,rets)
		r = self.CALCULATE_PART(R,rets)

		if OP in self.opTable.keys():
			if OP == "!":
				return "(" + r + " ~= 0 and 0 or 1)"
			else:
				return "((" + l + self.opTable[OP] + r + ") and 1 or 0)"
		else:
			return "(" + l + OP + r + ")"

	def ASSIGN_R(self,R,rets):
		return self.CALCULATE_PART(R,rets)

	def ASSIGN(self,v,rets):
		L = v["L"]
		if isinstance(L, dict) : 
			L = v["L"]["v"]

		R = self.ASSIGN_R(v["R"],rets)

		optinal = ""
		if L.startswith("$") : #L_Saved!
			optinal = "\nlocal tmp="+R+"\nif "+self._G(L)+" ~= tmp then LXVM:VarSave( '"+L+"', tmp ) end\n"
			R = "tmp"

		return " "+optinal + self._G(L) + "=" + R +";" 

	def RETS_CALC(self,rets):
		result = "{}"

		if len(rets) > 0:
			result = "{"

			for ret in rets:
				result += "function(vm,idx,rets,fcall) return " + ret + " end,"

			result += "}"

		return result

	def fnb(self):
		return " function(vm,idx) "

	def fnbe(self):
		return " function(vm,idx,rets) "

	def fne(self):
		return " end "

	def CMD_ASSIGN(self,v,rets):
		assign_result = self.ASSIGN(v,rets)
		return self.fnbe() + assign_result + self.fne()

	def CMD_CALL(self,v,rets):
		if v["native"] : 
			return v["name"]
		call_result = self._CALL(v["name"],v["args"],rets)
		return self.fnb() + self.fne()

	def CMD_IFGOTO_COND(self,v,rets):
		assign_result = self.ASSIGN_R(v["cond"],rets)
		return self.fnbe() + "local test ="+ assign_result +"; if type(test) == 'number' then return test~=0 else return test end"+ self.fne()

	def CMD_RETURN(self,v,rets):
		if v["ret"] == None:
			return self.fnb() + "return" + self.fne()
		return_result = self.ASSIGN_R(v["ret"],rets)
		return self.fnbe() + "return "+return_result+ self.fne()

	def CMD_MARKUP(self,v):
		return self.fnb() + 'pini.Dialog:AddMarkup('+slpp.encode({"word":True,"name":v["name"],"args":v["args"]})+')'+self.fne()

	def CMD_WORD(self,v):
		return self.fnb() + 'pini.Dialog:Add('+slpp.encode(v["strs"])+')' + self.fne()

	def _linking(self,obj,stck=None):
		strStack = ',"'+stck+'"' if stck else ''
		
		BMKS = {}
		ATLS = ""
		funcInfo = ""
		funcCode = ""

		def AppendCode(lnc,c):
			lnc[1] = lnc[1]+1
			lnc[0] += c

		code = "_LNXF[fname] = "
		if stck : 
			code = "_LNXF['"+stck+"'] = "
		code += "function() return {\n"
		lnc = [code,1]
		funcInfoCounter = 1

		# assignChunk = ""

		for v in obj :
			rets = []
			ln = "--lc:"+str(lnc[1])
			if "ln" in v:
				ln += ' | ln:'+str(v["ln"])
			ln += "\n"

			if v["t"] == 1 : #assign
				cmd_result = self.CMD_ASSIGN(v,rets)
				AppendCode(lnc,"{ t=1, pre="+self.RETS_CALC(rets)+", f="+cmd_result+"},"+ln)
				# assignChunk += self.ASSIGN(v,rets)+"\n"

			elif v["t"] == 2 : #ifgoto
				ifgoto_result = self.CMD_IFGOTO_COND(v,rets)
				AppendCode(lnc,"{ t=2, pre="+self.RETS_CALC(rets)+", test="+ifgoto_result+", ['else']='"+v["else"]+"' },"+ln)

			elif v["t"] == 3 : #bookmark
				AppendCode(lnc,"{ t=3 },--"+v["name"]+ln)
				BMKS[v["name"]] = lnc[1]

			elif v["t"] == 4 : #goto
				AppendCode(lnc,"{ t=4, n='"+v["goto"]["v"]+"'},"+ln)

			elif v["t"] == 5 : #call
				cmdcall_result = self.CMD_CALL(v,rets)
				AppendCode(lnc,"{ t=5, pre="+self.RETS_CALC(rets)+", f="+cmdcall_result+"},"+ln)

			elif v["t"] == 6 : #func-def
				name = v["name"]
				stmts = v["stmts"]
				funcCode += self._linking(stmts,name)

			elif v["t"] == 7 : #return 
				cmdreturn_result = self.CMD_RETURN(v,rets)
				AppendCode(lnc,"{ t=7, pre="+self.RETS_CALC(rets)+", f="+cmdreturn_result+" },"+ln)

			elif v["t"] == 8 : #autocomplete 
				_ = []
				for r in v["list"]["v"]:
					_.append([e["v"] for e in r["v"]])
				_ = slpp.encode(_)
				if _ == None:
					_ = "{}"
				funcInfo += '_AUTO_["'+v["name"]["v"]+'"]='+_+'\n'

			elif v["t"] == 9 : #funcInfo 
				explain = v["explain"]
				info = v["info"]
				fname = v["name"]["v"]

				funcInfo += "__def,__exd = {},{}\n"
				for e in info : 
					e = e["v"]
					if len(e)>0 : 
						t = [v1["v"] for v1 in e[2:]]
						name = e[1]["v"]
						if e[0]["v"] == 1 : 
							funcInfo += '__def["'+name+'"] = '+slpp.encode(t)+'\n'
						else:
							funcInfo += '__exd["'+name+'"] = '+slpp.encode(t)+'\n'

				#code += 'XVM:registFunctionInfo("'+fname+'","'+explain["v"]+'",__def,__exd)\n'
				funcInfo += '_LNXFucInfo["'+fname+'"] = {}\n'
				funcInfo += '_LNXFucInfo["'+fname+'"]["default"] = "'+explain["v"]+'"\n'
				funcInfo += '_LNXFucInfo["'+fname+'"]["extens"]  = __def\n'
				funcInfo += '_LNXFucInfo["'+fname+'"]["explain"] = __exd\n'
				funcInfo += '_LNXFucInfo["'+fname+'"]["idx"]     = '+unicode(funcInfoCounter)+'\n'
				funcInfoCounter = funcInfoCounter + 1

			elif v["t"] == 10 : #animation def
				ATLS += 'AnimMgr:registAnimation('+slpp.encode(v)+')\n'

			elif v["t"] == 11 : #hyper-goto
				AppendCode(lnc,"{ t=11, n='"+v["goto"]["v"]+"'},"+ln)

			elif v["t"] == 12 : #word
				AppendCode(lnc,"{ t=12, f="+self.CMD_WORD(v)+"},"+ln)

			elif v["t"] == 13 : #markup
				AppendCode(lnc,"{ t=13, f="+self.CMD_MARKUP(v)+"},"+ln)

		code = lnc[0]+"} end\n\n"
		_bmks = "_LNXB['"+stck+"']=" if stck else "_LNXB[fname]=" 
		if len(BMKS.keys()) > 0 : 
			_bmks += slpp.encode(BMKS)+"\n"
		else:
			_bmks += "{}\n"
		return funcInfo+_bmks+ATLS+funcCode+code

	def lua_header(self):
		return '''
_LNXG = _LNXG or {}
_LNXF = _LNXF or {}
_LNXB = _LNXB or {}
_AUTO_ = _AUTO_ or {}
_LNXFucInfo = _LNXFucInfo or {}
local function m(fname)
	local __def = nil
	local __exd = nil
'''

	def lua_footer(self):
		return '''
end
return m
'''

#######TOOL-CHAIN########
import traceback
class LNXToolChain(object) : 
	def __init__(self):
		self.compile   = LNXCompiler().compile
		self.optimize  = LNXOptimizer().optimize
		self.luaLinker = LNXLuaLinker().linking

	def build(self,text):
		text = "pass\n"+text+"\n"
		try:
			s,o = self.gen_obj(text)
			return self.gen_lua(o)
		except Exception, e:
			print "LNXToolChain BUILD > ",e
			traceback.print_exc(file=sys.stdout)
			return False

	def gen_obj(self,text,isInline=False,isActivePreProcess=True):
		text = "pass\n"+text+"\n"
		obj = None
		try:
			text = text.replace("\\","\\\\")
			tree = self.compile(text,None,isActivePreProcess)
			obj  = self.optimize(tree,isInline)
		except Exception, e:
			print "LNXToolChain GEN_OBJECT > ",e
			traceback.print_exc(file=sys.stdout)
			return False,e.lineno
		return True,obj

	def gen_lua(self,obj) :
		return self.luaLinker(obj)

	def gen_lua_line(self,obj):
		return self.luaLinker(obj,True)

	def compileFile(self,path,dist=None,isActivePreProcess=True):
		fp = QFile(path)
		fp.open(QIODevice.ReadOnly | QIODevice.Text)

		fin = QTextStream(fp)
		fin.setCodec("UTF-8")

		text = fin.readAll()

		fin = None
		fp.close()

		s,o = self.gen_obj(text,isActivePreProcess)
		if o != None and s != False :
			filename = os.path.basename(dist)
			filename,ext = os.path.splitext(filename)
			lua = self.gen_lua(o)
			if dist : 
				fp = QFile(dist)
				fp.open(QIODevice.WriteOnly | QIODevice.Text)
				
				out = QTextStream(fp)
				out.setCodec("UTF-8")
				out.setGenerateByteOrderMark(False)
				out << lua

				out = None
				fp.close()

			return lua,o,-1
		return None,None,o

	#########################

if __name__ == "__main__":
	build = LNXToolChain().build
	####### Test code #######
	code = u"""
c = 30*w+[w]+[w]+[w]+20+b
c = 30*w+20+b
c = 30*w+20+b
c = 30*w+20+b
"""

	print build(code)
	print "--==> Done"
