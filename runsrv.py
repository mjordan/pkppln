#!/usr/bin/env python

"""
Run a staging server microservice. This script will figure out where
the microservice code is, load it, fetch the appropriate deposits from the
database, and run the service against each deposit in turn.

usage: runsrv.py [-h] [-v | -q] [-n | -f] service

Run a staging service

positional arguments:
  service        Name of the service to run

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
  -q, --quiet    Silence most output
  -n, --dry-run  Do not update the deposit states
  -f, --force    Force updates to the deposit states.

Service is one of harvest, validate_payload, validat_bag, virus_check,
validate_export, reserialize_bag, stage_bag, deposit_to_pln

"""

import string
import sys
import traceback

import argparse
argparser = argparse.ArgumentParser(description='Run a staging service')
argparser.add_argument('service', type=str, help='Name of the service to run')

verbosity_group = argparser.add_mutually_exclusive_group()

verbosity_group.add_argument('-v', '--verbose', action='count', default=0,
                             help='Increase output verbosity')
verbosity_group.add_argument('-q', '--quiet', action='store_true',
                             default=False, help='Silence most output')
update_group = argparser.add_mutually_exclusive_group()
update_group.add_argument('-n', '--dry-run', action='store_true',
                          help='Do not update the deposit states')
update_group.add_argument('-f', '--force', action='store_true',
                          help='Force updates to the deposit states.')
args = argparser.parse_args()
if args.quiet:
    args.verbose = -1

microservice = args.service
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
    service_object = module_class()
except Exception as error:
    sys.exit('Cannot instantiate service ' + microservice.capitalize()
             + "\n" + error.message)

# run the service.
try:
    service_object.run(args)
except Exception as error:
    print traceback.format_exc()
    sys.exit('Service run failed: ' + str(error.message))
