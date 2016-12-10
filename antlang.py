import re
import types
from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, e
import copy
from functools import reduce
import sys

symbols = []

def lexer(string):
	string = re.sub(r'(\s|^)/.*\n','',string+'\n')
	stringlit = r'"[^"]*"'
	num = r'\-?\d*\.?\d+'
	frac = num + r'/' + num
	word = r'[A-Za-z\-_]+[A-Za-z0-9\-_]*'
	operator = r'\S̶|\S'
	regex = [stringlit, frac, word, num, operator]
	tokens = re.findall('|'.join(regex), string)
	result = []
	for token in tokens:
		if bool(re.match('^('+num+'|'+frac+')$', token)):
			result.append(('num',eval(token)))
		elif token.startswith('"'):
			result.append(('str',token[1:-1]))
		elif token in ['(',')','{','}','/',':',';']:
			result.append(('special',token))
		elif bool(re.match('^'+word+'$', token)):
			result.append(('var',token))
		else:
			result.append(('primitive',token))
	return result

def index_of_close(tokens):
	nesting = 1
	index = 1
	groups = [[]]
	for token in tokens[1:]:		
		if token == ('special', '(') or token == ('special', '{'): nesting += 1
		if token == ('special', ')') or token == ('special', '}'): nesting -= 1
		if (token == ('special', ')') or token == ('special', '}')) and nesting == 0:
			return {'index': index, 'groups': groups}
		if token == ('special', ';') and nesting == 1: groups.append([])
		else: groups[-1].append(token)
		index += 1
	return {'index': index, 'groups': groups}

def parser(tokens):
	if len(tokens) == 0:
		return ('num', 0)
	if len(tokens) == 1 and len(tokens[0]) == 2 and tokens[0][0] in ['num','str','var','primitive']:
		return tokens[0]
	if len(tokens) > 1 and tokens[0] == ('special','(') and tokens[1] == ('special',')'):
		return parser([[]]+tokens[2:])
	if len(tokens) > 2 and tokens[0] == ('special','('):
		i = index_of_close(tokens)['index']
		return parser([parser(tokens[1:i])]+tokens[1+i:])
	if len(tokens) > 2 and tokens[0] == ('special', '{'):
		o = index_of_close(tokens)
		inner = list(map(parser, o['groups']))
		return parser([[tokens[0]]+inner]+tokens[1+o['index']:])
	if len(tokens) > 1 and tokens[1] == ('special','/'):
		return parser([[tokens[1],parser([tokens[0]])]]+tokens[2:])
	if len(tokens) > 3 and tokens[1] == ('special','('):
		i = index_of_close(tokens[1:])['index']
		return parser([tokens[0],parser(tokens[2:i+1])]+tokens[2+i:])
	if len(tokens) > 3 and tokens[1] == ('special','{'):
		o = index_of_close(tokens[1:])
		return parser([tokens[0],[tokens[1]]+list(map(parser, o['groups']))]+tokens[2+o['index']:])
	if len(tokens) > 2 and tokens[2] == ('special','/'):
		return parser([tokens[0],[tokens[2],parser([tokens[1]])]]+tokens[3:])
	if len(tokens) > 2 and tokens[1] == ('special', ':') and tokens[0][0] == 'var':
		return [tokens[1], tokens[0][1], parser(tokens[2:])]
	if len(tokens) > 2:
		return [parser([tokens[1]]), parser([tokens[0]]), parser(tokens[2:])]
	if len(tokens) == 1 and isinstance(tokens[0], list):
		return tokens[0]
	if len(tokens) == 1:
		raise Exception('Unexpected ' + str(tokens[0][1]))
	else:
		raise Exception('Syntax Error')

def md_map(monad, dyad=None):
	if dyad is None: dyad = monad
	def g(x,y=None):
		if y is None: return list(map(g,x)) if isinstance(x, list) else monad(x)
		if x == [] or y == []: return []
		if not isinstance(x, list) and not isinstance(y, list): return dyad(x,y)
		if not isinstance(x, list): x = [x]
		if not isinstance(y, list): y = [y]
		res = []
		length = max(len(x), len(y))
		for i in range(length): res.append(g(x[i%len(x)], y[i%len(y)]))
		return res
	return g

signum = lambda x: 1 if x>0 else -1 if x<0 else 0

def _repr(x):
	if isinstance(x, float):
		return '{0:.14f}'.format(x)
	if isinstance(x, int):
		return _repr(float(x))
	else:
		return str(x)

def scalar(x):
	return x[0] if isinstance(x,list) and len(x) > 0 else x

def python(statement, argument = None):
	if statement == 'import' and argument != None:
		return __import__(str(argument))
	elif statement == 'eval' and argument != None:
		return eval(str(argument))
	elif statement == 'call':
		if not isinstance(argument, list): argument = [argument]
		o = argument[0]
		args = []
		kwargs = {}
		for arg in argument[1:]:
			if isinstance(arg, tuple):
				kwargs[arg[0]] = arg[1]
			else:
				args.append(arg)
		return o(*args, **kwargs)
	else:
		raise Exception('Python Error')

stdlib = {
	"sin": md_map(sin),
	"cos": md_map(cos),
	"tan": md_map(tan),
	"asin": md_map(asin),
	"acos": md_map(acos),
	"atan": md_map(atan),
	"sinh": md_map(sinh),
	"cosh": md_map(cosh),
	"tanh": md_map(tanh),
	"asinh": md_map(asinh),
	"acosh": md_map(acosh),
	"atanh": md_map(atanh),
	"eq": lambda a,b: int(_repr(scalar(a))==_repr(scalar(b))),
	"ne": lambda a,b: int(_repr(scalar(a))!=_repr(scalar(b))),
	"lt": lambda a,b: int(scalar(a)<scalar(b)),
	"le": lambda a,b: int(scalar(a)<=scalar(b)),
	"gt": lambda a,b: int(scalar(a)>scalar(b)),
	"ge": lambda a,b: int(scalar(a)>=scalar(b)),
	"length": lambda x: len(x) if isinstance(x,list) else 1,
	"range": md_map(lambda n: [signum(scalar(n))*x for x in range(abs(scalar(n)))]),
	"string": lambda x: "".join(map(lambda a: str(AntLang(a)),x if isinstance(x,list) else [x])),
	"ustring": lambda s: list(str(s)),
	"import": "import",
	"eval": "eval",
	"call": "call",
	"python": python,
	"dot": lambda o, a: o.__getattribute__(str(a))
}

def do(ast, ws=stdlib):
	if isinstance(ast,list):
		if len(ast) == 0: return []
		if ast[0] == ('special', ':'):
			val = do(ast[2], ws)
			ws[ast[1]] = val
			return val
		if ast[0] == ('special', '{'):
			body = ast[1:]
			def f(x=None,y=None,*rest):
				closure = copy.copy(ws)
				if x is not None: closure['x'] = x
				if y is not None: closure['y'] = y
				res = []
				for expr in body:
					res = do(expr, closure)
				return res
			return f
		if ast[0] == ('special','/'):
			func = do(ast[1], ws)
			return lambda x,xs: reduce(func, [x]+(xs if isinstance(xs, list) else [xs]))
		xast = [do(x, ws) for x in ast]
		if isinstance(xast[0], types.FunctionType):
			return xast[0](*xast[1:])
	elif ast[0] == 'num':
		return ast[1]
	elif ast[0] == 'str':
		return ast[1]
	elif ast[0] == 'primitive':
		if ast[1] == '+': return md_map(lambda x,y: x+y)
		elif ast[1] == '\\': return md_map(lambda x: -x, lambda x,y: x-y)
		elif ast[1] == '×': return md_map(lambda x,y: x*y)
		elif ast[1] == '÷': return md_map(lambda x: 1/x, lambda x,y: x/y)
		elif ast[1] == '|': return md_map(lambda x,y: x%y)
		elif ast[1] == '^': return md_map(lambda x: e**x, lambda x,y: x**y)
		elif ast[1] == '∧': return md_map(lambda x,y: min(x,y))
		elif ast[1] == '∨': return md_map(lambda x,y: max(x,y))
		elif ast[1] == ',':
			return lambda x,y: (x if isinstance(x, list) else [x]) + (y if isinstance(y, list) else [y])
		elif ast[1] == '∘':
			def _apply(f,x):
				if callable(f): return f(x)
				if not isinstance(f, list): f = [f]
				if not isinstance(x, list): return f[x]
				else: return list(map(lambda x: _apply(f,x), x))
			return _apply
		elif ast[1] == '⌷':
			def take(n,x):
				if not isinstance(x,list): x = [x]
				if n >= 0: return x[:n]
				else: return x[n:]
			return take
		elif ast[1] == '⌷̶':
			def drop(n,x):
				if not isinstance(x,list): x = [x]
				if n >= 0: return x[n:]
				else: return x[:n]
			return drop
		elif ast[1] == '⌽':
			def mingle(x,y):
				if not isinstance(x, list): x = [x]
				if not isinstance(y, list): y = [y]
				if x == [] or y == []: return []
				return [[x[i%len(x)],y[i%len(y)]] for i in range(max(len(x),len(y)))]
			return mingle
		elif ast[1] == '⍴':
			def reshape(n,v):
				res = [[]]
				if not isinstance(v,list): v = [v]
				for x in v:
					if len(res[-1]) == n: res.append([x])
					else: res[-1].append(x)
				return res
			return reshape
		elif ast[1] == '⍣':
			def apply_n(f, n):
				def g(x,y=None):
					if y is None:
						for i in range(n):
							x = f(x)
						return x
					else:
						for i in range(n):
							y = f(x,y)
						return y
				return g
			return apply_n
		elif ast[1] == '→':
			return lambda x, y: (x, y)
		elif ast[1] == "'":
			return lambda f,x: list(map(f,x if isinstance(x,list) else [x]))
		elif ast[1] == '?':
			return lambda f,x: list(filter(f,x if isinstance(x,list) else [x]))
		else: raise Exception('Spelling Error')
	elif ast[0] == 'var':
		if ast[1] in ws.keys(): return ws[ast[1]]
		else: raise Exception('Undefined Variable')

class AntLang:
	def __init__(self, val): self.val = val
	def __str__(self, inner = False):
		if isinstance(self.val, list) and len(list) > 50:
			return '[' + str(len(list)) + ' ELEMENTS]'
		if isinstance(self.val, list):
			if inner: return '(' + ' '.join(map(lambda x: AntLang(x).__str__(inner = True), self.val)) + ')'
			else: return ' '.join(map(lambda x: AntLang(x).__str__(inner = True), self.val))
		if callable(self.val): return '{}'
		if isinstance(self.val, tuple):
			return str(AntLang(self.val[0])) + '→' + str(AntLang(self.val[1]))
		if isinstance(self.val, dict):
			return '[DICTIONARY]'
		if isinstance(self.val, types.ModuleType):
			return '[MODULE]'
		else: return str(self.val)
	__repr__ = __str__

def evaluate(string):
	tokens = lexer(string)
	ast = parser(tokens)
	return AntLang(do(ast))

if __name__ == '__main__':
	if len(sys.argv) == 3 and sys.argv[1] == '-f':
		script = open(sys.argv[2]).read()
		for line in script.split('\n'):
			evaluate(line)
	else:
		while True:
			try:
				if len(sys.argv) > 1 and sys.argv[1] == '-np':
					line = input('')
				else:
					line = input('--> ')
				print(evaluate(line))
			except (EOFError):
				quit()
			except Exception as e:
				print(e)
			except:
				pass
