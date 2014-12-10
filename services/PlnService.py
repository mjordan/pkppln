from datetime import datetime
import pkppln
import abc
from abc import abstractmethod
import logging
import MySQLdb


class PlnService(object):

    """
    Superclass for all PLN services. A service must provide state_before,
    state_after, and execute() methods, as defined below. This superclass
    takes care of finding the appropriate deposits, updating them as necessary,
    and logging any actions taken.
    """
    __metaclass__ = abc.ABCMeta

    args = None

    def name(self):
        """The name of the service, identical to the class name."""
        return type(self).__name__

    @abstractmethod
    def state_before(self):
        """The name of the state before this one."""
        return

    @abstractmethod
    def state_after(self):
        """The name of the state after this one."""
        return

    @abstractmethod
    def execute(self, deposit):
        """Execute a service against a deposit."""
        return ['', '']

    def output(self, n, message=''):
        """Output a message at verbosity n."""
        if self.args is not None:
            if self.args.verbose >= n and message != '':
                print message

    def log_microservice(self, uuid, start_time, end_time, result, error):
        """Log the service action ot the database."""
        mysql = pkppln.get_connection()
        if pkppln.log_microservice(
                self.name(), uuid, start_time, end_time, result, error):
            mysql.commit()
        else:
            mysql.rollback()

    def run(self, args):
        """
        Run the service. Fetches the deposits for the service and calls
        execute() for each one. execute() is expectd to return a pair:
        (result, message) where result is 'success' if the service succeeded or
        'failure' if the service failed. An optional message may be returned.
        """
        self.args = args
        deposits = pkppln.get_deposits(self.state_before())
        self.output(2, 'Found ' + str(len(deposits)) +
                    ' deposits for service ' + args.service)
        for deposit in deposits:
            self.output(1, deposit['deposit_url'])
            deposit_started = datetime.now()
            (result, error) = self.execute(deposit)
            deposit_ended = datetime.now()
            self.output(1, result)
            self.output(0, error)

            if args.dry_run:
                continue

            if result == 'success':
                pkppln.update_deposit(deposit['deposit_uuid'],
                                      self.state_after(),
                                      'success')
                self.log_microservice(deposit['deposit_uuid'],
                                      deposit_started,
                                      deposit_ended,
                                      result,
                                      error)
            elif args.force:
                self.output(0, 'forcing update')
                pkppln.update_deposit(deposit['deposit_uuid'],
                                      self.state_after(),
                                      'forced')
                self.log_microservice(deposit['deposit_uuid'],
                                      deposit_started,
                                      deposit_ended, result,
                                      'FORCED UPDATE ' + error)
