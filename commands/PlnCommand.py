import abc
from abc import abstractmethod
import argparse


class PlnCommand(object):

    """Abstract base class for pln staging commands."""

    __metaclass__ = abc.ABCMeta

    args = None

    def name(self):
        return type(self).__name__

    def output(self, n, message=''):
        """Output a message at verbosity n."""
        if self.args is not None:
            if self.args.verbose >= n and message != '':
                print message

    def add_args(self, parser):
        pass

    def run(self, args):
        parser = argparse.ArgumentParser(description='List deposits')
        self.add_args(parser)
        cmdargs = parser.parse_args(args.subargs)
        # args is a list of the unparsed arguments from the command line.
        # parse them out here and then call self.execute()
        self.execute(cmdargs)

    @abstractmethod
    def execute(self, args):
        pass
