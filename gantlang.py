from tkinter import *
from tkinter import filedialog

import os
import sys

import json
import antlang

try:
	data = json.load(open('styles.json'))
except:
	data = {
		"font-family": "Helvetica",
		"font-size": 14,
		"title": "AntLang"
	}

r = Tk()
r.wm_title(data['title'])
r.configure()

FONT = (data['font-family'], data['font-size'])

symbols = []

infovar = StringVar()
infobox = Label(r, textvariable=infovar, font=FONT, relief=RIDGE)
infobox.pack(side=TOP, fill=BOTH)
infovar.set('\n')

content = StringVar()
text = Entry(r, font=FONT, textvariable=content)

def copy(string): text.insert(INSERT,string)

frame = Frame()

def add_symbol(symbol, info, example, key=None):
	global symbols
	symbols = sorted([symbol] + symbols, key = lambda s: 1/len(s))
	btn = Button(frame, text=symbol, command=lambda: copy(symbol), font=FONT)
	btn.pack(side=LEFT, fill=BOTH, expand=True)
	btn.bind('<Enter>',
	         lambda e: infovar.set(info+(' (CTRL ' + key + ')'
	                   if key is not None
	                   else '')+'\nExample: '+example))
	if key is not None:
		r.bind('<Control_L>' + key, lambda e: copy(symbol))

men = Menu(r, font=FONT)

def sub_add_command(submen, symbol):
	submen.add_command(label=symbol, command=lambda *a: copy(symbol))

def add_namespace(name, symbols):
	submen = Menu(men, font=FONT, tearoff=0)
	for symbol in symbols:
		sub_add_command(submen, symbol)
	men.add_cascade(label=name, menu=submen)

filemen = Menu(men, font=FONT, tearoff=0)

def open_file(*a):
	filename_with_path = filedialog.asksaveasfilename()
	filename = filename_with_path.split('/')[-1]
	content = ''
	try:
		content = open(filename_with_path).read()
	except:
		pass
	editor = Toplevel()
	editor.title(filename)
	button_frame = Frame(editor)
	button_frame.pack(side=TOP, expand=False, fill=BOTH)
	def command_save(*a):
		f = open(filename_with_path, 'w')
		f.write(text.get("1.0", END))
		f.close()
	button_save = Button(button_frame, font=FONT, text='Save', command=command_save)
	button_save.pack(side=LEFT, fill=BOTH, expand=True)
	def command_run(*a):
		content = text.get("1.0", END)
		for line in content.split('\n'):
			if line != '' and not line.startswith('/'):
				execute(line)
	button_run = Button(button_frame, font=FONT, text='Run', command=command_run)
	button_run.pack(side=LEFT, fill=BOTH, expand=True)
	text = Text(editor, font=FONT)
	text.insert(INSERT, content)
	text.pack(fill=BOTH, expand=1)

filemen.add_command(label='Open', command=open_file)

filemen.add_command(label='Restart', command=lambda *a: os.execl(sys.executable, sys.executable, *sys.argv))

men.add_cascade(label='File', menu=filemen)

add_namespace('Comparison', ['eq','ne','lt','le','gt','ge'])
add_namespace('Math', [ 'sin'
                      , 'cos'
                      , 'tan'
                      , 'asin'
                      , 'acos'
                      , 'atan'
                      , 'sinh'
                      , 'cosh'
                      , 'tanh'
                      , 'asinh'
                      , 'acosh'
                      , 'atanh'
                      ])
add_namespace('Lists', ['length', 'range'])
add_namespace('Strings', ['string', 'ustring'])

r.config(menu=men)

frame.pack(side=TOP, expand=False, fill=BOTH)

add_symbol('+', 'Plus', '3+5')
add_symbol('\\', 'Minus', '3\\5')
add_symbol('×', 'Times', '3×5', key='+')
add_symbol('÷', 'Divide', '3÷5', key='-')
add_symbol('|', 'Magnitude', '5|3')
add_symbol('^', 'Power', '2^0.5')
add_symbol('∧', 'Minimum', '1∧0', key='1')
add_symbol('∨', 'Maximum', '1∨0', key='2')
add_symbol(',', 'Catenate', '1,2,3')
add_symbol('⌷', 'Take', '-2⌷1,2,3', key='i')
add_symbol('⌷̶', 'Drop', '-2⌷̶1,2,3', key='j')
add_symbol('⌽', 'Mingle', '(1,2,3)⌽4,5,6', key='l')
add_symbol('⍴', 'Reshape', '2⍴1,2,3,4', key='r')
add_symbol('∘', 'Apply', '\∘5', key='o')
add_symbol('⍣', 'Apply N', '({x+1}⍣5)∘10', key='n')
add_symbol("'", 'Each', "sin'range∘5")
add_symbol('?', 'Filter', '{x gt 5}?range∘10')
add_symbol('/', 'Reduce', '0+/ 1,2,3')
add_symbol('-', 'Negate', '-1')
add_symbol('()', 'Group', '(5×1)+2')
add_symbol('{}', 'Function', '1 {x+2×y} 3')
add_symbol('→', 'Keyed Value', '', key='k')

r.geometry('800x600')

text.pack(side=BOTTOM, fill=X)

antlang.symbols = symbols

lbox = Listbox(r,font=FONT, relief=SUNKEN)
lbox.pack(side=BOTTOM, fill=BOTH, expand=True)

def log(string):
	lbox.insert(END, str(string))
	lbox.yview(END)

def execute(string):
	log(string)
	try:
		log(antlang.evaluate(string))
	except Exception as e:
		log(e)
	log('')

text.bind('<Return>', lambda *a: [execute(content.get()),text.select_range(0,END)][-1])

r.mainloop()
