from commands.PlnCommand import PlnCommand
import string
import argparse
from commands.microcommands.list_services import ListServices
from services.PlnService import parse_arguments


class Process(PlnCommand):

    def description(self):
        return "Run all processing steps for a deposit."

    def add_args(self, parser):
        parser.add_argument('deposit',
                            help='Deposit to process')
        parser.add_argument('srvargs', nargs=argparse.REMAINDER)

    def execute(self, args):
        if args.deposit is None:
            return 'No deposit'
        uuid = args.deposit
        service_args = args.srvargs + ['-d', uuid]

        for service in ListServices().services():
            self.output(1, service)
            module_name = 'services.microservices.' + service
            module = __import__(module_name, fromlist=[service])
            class_name = string.capwords(service, '_').replace('_', '')
            module_class = getattr(module, class_name)
            service_object = module_class()
            args = parse_arguments(service_args + [service])
            try:
                service_object.run(args)
            except Exception as e:
                self.output(0, str(e))
                raise
