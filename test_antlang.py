import pytest
import antlang as ant

data = [
    # Simple expressions
    ('(0,0.15,0.2)', [('special', '('), ('num', 0), ('primitive', ','), ('num', 0.15),
                      ('primitive', ','), ('num', 0.2), ('special', ')')], '0 0.15 0.2'),

    # Additions
    ('1+2', [('num', 1), ('primitive', '+'), ('num', 2)], '3'),
    ('1+2+3', [('num', 1), ('primitive', '+'), ('num', 2), ('primitive', '+'), ('num', 3)], '6'),

    # Subtractions
    ('2\\1', [('num', 2), ('primitive', '\\'), ('num', 1)], '1'),
    ('0.9\(0,0.15,0.2)', [('num', 0.9), ('primitive', '\\'), ('special', '('), ('num', 0),
                          ('primitive', ','), ('num', 0.15), ('primitive', ','), ('num', 0.2),
                          ('special', ')')], '0.9 0.75 0.7'),

    # Multiplications
    ('2×0.7', [('num', 2), ('primitive', '×'), ('num', 0.7)], '1.4'),
    ('7×0.7', [('num', 7), ('primitive', '×'), ('num', 0.7)], str(7*0.7)),
    ('18×0.7', [('num', 18), ('primitive', '×'), ('num', 0.7)], '12.6'),
    ('(2,7,18)×0.7', [('special', '('), ('num', 2), ('primitive', ','), ('num', 7), ('primitive', ','), ('num', 18),
                      ('special', ')'), ('primitive', '×'), ('num', 0.7)], ' '.join([str(x) for x in (1.4, 7*0.7, 12.6)])),
    ('(2,7,18)×0.9\(0,0.15,0.2)', [('special', '('), ('num', 2), ('primitive', ','), ('num', 7), ('primitive', ','),
                                   ('num', 18), ('special', ')'), ('primitive', '×'), ('num', 0.9), ('primitive', '\\'),
                                   ('special', '('), ('num', 0), ('primitive', ','), ('num', 0.15), ('primitive', ','),
                                   ('num', 0.2), ('special', ')')], '1.8 5.25 12.6'),

    # Modulo
    ('7|2', [('num', 7), ('primitive', '|'), ('num', 2)], '1'),

    # Average
    ('(2+7+18)÷3', [('special', '('), ('num', 2), ('primitive', '+'), ('num', 7), ('primitive', '+'), ('num', 18),
                    ('special', ')'), ('primitive', '÷'), ('num', 3)], '9.0'),

    # Sum
    ('0 +/ 1, 2, 3', [('num', 0), ('primitive', '+'), ('special', '/'), ('num', 1), ('primitive', ','),
                      ('num', 2), ('primitive', ','), ('num', 3)], '6'),

    # Length
    ('length∘2,7,18', [('var', 'length'), ('primitive', '∘'), ('num', 2), ('primitive', ','), ('num', 7),
                       ('primitive', ','), ('num', 18)], '3'),

    # Range
    ('range∘5', [('var', 'range'), ('primitive', '∘'), ('num', 5)], '0 1 2 3 4'),

    # Min/Max
    ('5∨2,7,18', [('num', 5), ('primitive', '∨'), ('num', 2), ('primitive', ','), ('num', 7), ('primitive', ','),
                  ('num', 18)], '5 7 18'),
    ('1∧0.1,0.15,0.2,1.5', [('num', 1), ('primitive', '∧'), ('num', 0.1), ('primitive', ','), ('num', 0.15),
                            ('primitive', ','), ('num', 0.2), ('primitive', ','), ('num', 1.5)], '0.1 0.15 0.2 1'),

    # Functions
    ('average: {(0+/x)÷length∘x}', [('var', 'average'), ('special', ':'), ('special', '{'), ('special', '('),
                                    ('num', 0), ('primitive', '+'), ('special', '/'), ('var', 'x'), ('special', ')'),
                                    ('primitive', '÷'), ('var', 'length'), ('primitive', '∘'), ('var', 'x'),
                                    ('special', '}')], '{}'),
    ('factorial:{1×/1+range∘x}', [('var', 'factorial'), ('special', ':'), ('special', '{'), ('num', 1),
                                  ('primitive', '×'), ('special', '/'), ('num', 1), ('primitive', '+'),
                                  ('var', 'range'), ('primitive', '∘'), ('var', 'x'), ('special', '}')], '{}'),
    ('fib:{({x,0+/-2⌷x}⍣x)∘0,1}', [('var', 'fib'), ('special', ':'), ('special', '{'), ('special', '('),
                                   ('special', '{'), ('var', 'x'), ('primitive', ','), ('num', 0), ('primitive', '+'),
                                   ('special', '/'), ('num', -2), ('primitive', '⌷'), ('var', 'x'), ('special', '}'),
                                   ('primitive', '⍣'), ('var', 'x'), ('special', ')'), ('primitive', '∘'), ('num', 0),
                                   ('primitive', ','), ('num', 1), ('special', '}')], '{}')

]

data_fun = [
    ('fib: {({x,0+/-2⌷x}⍣x)∘0,1}', 'fib∘10', '0 1 1 2 3 5 8 13 21 34 55 89'),
    ('factorial: {1×/1+range∘x}', 'factorial∘5', '120'),
    ('factorial: {1×/1+range∘x}', 'factorial∘0', '1'),
    ('average: {(0+/x)÷length∘x}', 'average∘2,7,18', '9.0'),
    # Take
    ('fruits: "apples", "oranges", "bananas", "strawberries", "cake"', '3⌷fruits', 'apples oranges bananas'),
    ('fruits: "apples", "oranges", "bananas", "strawberries", "cake"', '-3⌷fruits', 'bananas strawberries cake'),
    # Drop
    ('fruits: "apples", "oranges", "bananas", "strawberries", "cake"', '2⌷̶fruits', 'bananas strawberries cake'),
    ('fruits: "apples", "oranges", "bananas", "strawberries", "cake"', '-2⌷̶fruits', 'apples oranges bananas'),
    # Mingle
    ('l1: (1,2,3)', 'l1⌽(4,5,6)', '(1 4) (2 5) (3 6)'),
    # Reshape
    ('l2: (1,2,3,4)', '2⌽(1,2,3,4)', '(1 2) (3 4)'),
    # Python
    ('zen: import python "this"', 'zen dot "i"', '25'),
    ('math: import python "math"', 'call python (math dot "factorial"), 4', '24'),
    ('fact: {call python (math dot "factorial"), x}', 'fact∘10', '3628800'),
    ('builtins: import python "builtins"', 'call python (builtins dot "chr"), 65', 'A'),
    ('chr: {call python (builtins dot "chr"), x}', 'chr∘65', 'A')
]

data_lexer = [(x, y) for (x, y, _) in data]
data_eval = [(x, z) for (x, _, z) in data]

def idfn(val):
    return str(val)

@pytest.mark.parametrize('a,tokens', data_lexer, ids=idfn)
def test_lexer(a, tokens):
    assert ant.lexer(a) == tokens

@pytest.mark.parametrize('a,res', data_eval, ids=idfn)
def test_eval(a, res):
    assert str(ant.evaluate(a)) == res

@pytest.mark.parametrize('decl,fun_call,res', data_fun, ids=idfn)
def test_fun(decl, fun_call, res):
    ant.evaluate(decl)
    ant.evaluate(fun_call) == res

def test_names():
    ant.evaluate('one: 1')
    ant.evaluate('two: 2')
    ant.evaluate('plus: +')
    ant.evaluate('three: 3')
    assert str(ant.evaluate('one plus two')) == str(ant.evaluate('three'))

def test_discount():
    ant.evaluate('discount: {x × 1\y÷100}')
    res = ' '.join([str(x) for x in (1.8, 7*(80/100), 9.0)])
    assert str(ant.evaluate('(2,7,18) discount 10,20,50')) == res
