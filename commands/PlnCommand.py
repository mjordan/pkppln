import abc
from abc import abstractmethod
import argparse
import inspect
from os.path import splitext, basename


class PlnCommand(object):

    """Abstract base class for pln staging commands."""

    __metaclass__ = abc.ABCMeta

    args = None

    def name(self):
        return type(self).__name__
    
    def module(self):
        filepath = inspect.getfile(self.__class__)
        filename = basename(filepath)
        module_name = splitext(filename)[0]
        return module_name;

    def output(self, n, message=''):
        """Output a message at verbosity n."""
        if self.args is not None:
            if self.args.verbose >= n and message != '':
                print message

    def add_args(self, parser):
        pass

    @abstractmethod
    def description(self):
        pass

    def run(self, args):
        parser = argparse.ArgumentParser(
            description=self.description(),
            usage='%(prog)s [global options] ' + self.module() + ' [command options]'
        )
        self.add_args(parser)
        cmdargs = parser.parse_args(args.subargs)
        # args is a list of the unparsed arguments from the command line.
        # parse them out here and then call self.execute()
        print self.execute(cmdargs)

    @abstractmethod
    def execute(self, args):
        pass
