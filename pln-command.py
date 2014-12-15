#!/usr/bin/env python

"""
"""

import string
import sys
import traceback

import argparse
argparser = argparse.ArgumentParser(description='Run a staging command')
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
    sys.exit('Cannot instantiate service ' + command.capitalize()
             + "\n" + error.message)

# run the service.
try:
    command_object.run(args)
except Exception as error:
    print traceback.format_exc()
    sys.exit('Command run failed: ' + str(error.message))
