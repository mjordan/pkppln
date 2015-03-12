import abc
from abc import abstractmethod
import argparse
import inspect
from os.path import splitext, basename
import pkppln
import logging


def parse_arguments(arglist=None):
    argparser = argparse.ArgumentParser(description='Run a staging command')

    argparser.add_argument('-c', '--config', type=str, default='config.cfg',
                           help='Config file to use.')

    verbosity_group = argparser.add_mutually_exclusive_group()

    verbosity_group.add_argument('-v', '--verbose', action='count', default=0,
                                 help='Increase output verbosity')
    verbosity_group.add_argument('-q', '--quiet', action='store_true',
                                 default=False, help='Silence most output')

    argparser.add_argument('-n', '--dry-run', action='store_true',
                           help='Do not update the deposit states')

    argparser.add_argument('command', type=str,
                           help='Name of the command to run')
    argparser.add_argument('subargs', nargs=argparse.REMAINDER,
                           help='Arugments to subcommand')
    args = argparser.parse_args(arglist)
    if args.quiet:
        args.verbose = -1
    return args


class PlnCommand(object):

    """Superclass for all PLN commands. A command is different from a service
    because it doesn't rely on a deposit's state. This superclass takes care
    of finding deposits, updating them as necessary, and logging any errors."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, args):
        self.args = args
        pkppln.config_file_name = args.config
        self.handle = pkppln.get_connection()

    def name(self):
        """The name of the service, identical to the class name."""
        return type(self).__name__

    def log_message(self, message, level=logging.INFO):
        pkppln.log_message(message, level=level, log_type='microservice_log')

    @abstractmethod
    def execute(self, args):
        pass

    @abstractmethod
    def description(self):
        pass

    def output(self, n, message=''):
        """Output a message at verbosity n."""
        if self.args is not None:
            if self.args.verbose >= n and message != '':
                print message

    def module(self):
        filepath = inspect.getfile(self.__class__)
        filename = basename(filepath)
        module_name = splitext(filename)[0]
        return module_name

    def add_args(self, parser):
        pass

    def run(self):
        parser = argparse.ArgumentParser(
            description=self.description(),
            usage='%(prog)s [global options] ' +
            self.module() + ' [command options]'
        )
        self.add_args(parser)
        cmdargs = parser.parse_args(self.args.subargs)
        # args is a list of the unparsed arguments from the command line.
        # parse them out here and then call self.execute()
        self.execute(cmdargs)
