# Automatically make the action build if none is specified
import sys
if len(sys.argv) == 1:
	sys.argv.append('build')

# create the cx_Freeze setup
from cx_Freeze import setup, Executable

setup(
		# Name the program (antlang)
		name='AntLang',
		# Create the description
		description='A Scientific Environment',
		# Build from file gantlang.py
		executables = [Executable('gantlang.py')]
	)
