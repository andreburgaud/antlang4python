import antlang

while True:
	try:
		line = input(6*' ')
	except:
		exit()
	try:
		print(antlang.evaluate(line))
	except (Exception) as e:
		print(e)
	print('')
