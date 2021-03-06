#!/usr/bin/env python

"""
Run a staging server microservice. This script will figure out where
the microservice code is, load it, fetch the appropriate deposits from the
database, and run the service against each deposit in turn.

usage: pln-service.py [-h] [-v | -q] [-n | -f] [-d DEPOSIT] service

Run a staging service

positional arguments:
  service               Name of the service to run

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -q, --quiet           Silence most output
  -n, --dry-run         Do not update the deposit states
  -f, --force           Force updates to the deposit states.
  -d DEPOSIT, --deposit DEPOSIT
                        Run the service on one or more deposits
"""

import string
import sys
import traceback

from services.PlnService import parse_arguments
args = parse_arguments()

# allow hyphens in service names.
microservice = args.service.replace('-', '_')
# dynamically load the module based on the parameter.
service_module = 'services.microservices.' + microservice
try:
    module = __import__(service_module, fromlist=[microservice])
except ImportError as error:
    sys.exit('Cannot find microservice ' + service_module)

classname = string.capwords(microservice, '_').replace('_', '')

try:
    module_class = getattr(module, classname)
except AttributeError as error:
    sys.exit('Cannot find class ' + classname + ' in ' + service_module)

try:
    service_object = module_class(args)
except Exception as error:
    sys.exit('Cannot instantiate service ' + microservice.capitalize()
             + "\n" + str(error))

# run the service.
try:
    service_object.run()
except Exception as error:
    print traceback.format_exc()
    sys.exit('Service run failed: ' + str(error.message))
