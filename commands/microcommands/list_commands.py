from glob import glob
from os.path import abspath, dirname, basename
from commands.PlnCommand import PlnCommand


class ListCommands(PlnCommand):

    def execute(self, args):
        path = dirname(abspath(__file__))
        files = [basename(p) for p in glob(path + '/*.py')]
        files = [p.replace('.py', '') for p in files]
        files.sort()
        output = 'usage: pln-command.py [-h] [-v | -q] command ...\n'
        output += 'where command is one of \n'
        for f in files:
            if f == '__init__':
                continue
            output += '  ' + f + '\n'
        return output
