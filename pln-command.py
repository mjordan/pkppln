#!/usr/bin/env python

"""
"""

import string
import sys
import traceback

import argparse
argparser = argparse.ArgumentParser(
    description='Run a staging command',
    epilog='Use pln-command.py list_commands for a list of available commands'
)
verbosity_group = argparser.add_mutually_exclusive_group()

verbosity_group.add_argument('-v', '--verbose', action='count', default=0,
                             help='Increase output verbosity')
verbosity_group.add_argument('-q', '--quiet', action='store_true',
                             default=False, help='Silence most output')
argparser.add_argument('command', type=str, help='Name of the command to run')
argparser.add_argument('subargs', nargs=argparse.REMAINDER)
    args = argparser.parse_args()

command = args.command
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
             + "\n" + error.message)

# run the service.
try:
    command_object.run(args)
except Exception as error:
    print traceback.format_exc()
    sys.exit('Command run failed: ' + str(error.message))
