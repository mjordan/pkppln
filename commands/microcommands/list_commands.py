import os
from os.path import abspath, dirname, splitext

from commands.PlnCommand import PlnCommand


class ListCommands(PlnCommand):

    def is_command(self, filename):
        if filename.startswith('_'):
            return False
        if filename.endswith('.pyc'):
            return False
        return True

    def description(self):
        return "List all commands"

    def execute(self, args):
        files = os.listdir(dirname(abspath(__file__)))
        cmds = [ splitext(f)[0] for f in files if self.is_command(f)]
        for cmd in sorted(cmds):
            print cmd
        