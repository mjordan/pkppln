from glob import glob
from os.path import abspath, dirname, basename
from commands.PlnCommand import PlnCommand


class ListCommands(PlnCommand):

    def description(self):
        return "List all commands available."

    def execute(self, args):
        path = dirname(abspath(__file__))
        files = [basename(p) for p in glob(path + '/*.py')]
        files = [p.replace('.py', '') for p in files]
        files.sort()
        self.output(0, 'usage: pln-command.py [-h] [-v | -q] command ...')
        self.output(0, 'where command is one of')
        for f in files:
            if f == '__init__':
                continue
            self.output(0, '  ' + f)
