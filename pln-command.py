#!/usr/bin/env python

"""
Run a staging server command. This script will figure out where
the command code is, load it, and run the command.

usage: pln-command.py [-h] [-v | -q] [-n] command

Run a staging command

positional arguments:
  command        Name of the command to run
  subargs        Arugments to subcommand

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
  -q, --quiet    Silence most output

Use pln-command.py list_commands for a list of available commands
"""

import string
import sys
import traceback

from commands.PlnCommand import parse_arguments
args = parse_arguments()

# allow hyphens in command names.
command = args.command.replace('-', '_')
# dynamically load the module based on the parameter.
command_module = 'commands.microcommands.' + command
try:
    module = __import__(command_module, fromlist=[command])
except ImportError as error:
    sys.exit('Cannot find command ' + command_module)

classname = string.capwords(command, '_').replace('_', '')

try:
    module_class = getattr(module, classname)
except AttributeError as error:
    sys.exit('Cannot find class ' + classname + ' in ' + command_module)

try:
    command_object = module_class()
except Exception as error:
    sys.exit('Cannot instantiate command ' + command.capitalize()
             + "\n" + str(error))

# run the command.
try:
    command_object.run(args)
except Exception as error:
    print traceback.format_exc()
    sys.exit('Command run failed: ' + str(error.message))
