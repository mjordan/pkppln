from datetime import datetime
import pkppln
import abc
from abc import abstractmethod
import logging
import MySQLdb


class PlnService(object):
    __metaclass__ = abc.ABCMeta

    args = None

    def name(self):
        return type(self).__name__

    @abstractmethod
    def state_before(self):
        return

    @abstractmethod
    def state_after(self):
        return

    @abstractmethod
    def execute(self, deposit):
        return ['', '']

    def output(self, n, message=''):
        if self.args is not None:
            if self.args.verbose >= n and message != '':
                print message

    def log_microservice(self, uuid, start_time, end_time, result, error):
        mysql = pkppln.get_connection()
        cursor = mysql.cursor()
        try:
            cursor.execute("""
            INSERT INTO microservices (microservice, deposit_uuid, started_on,
            finished_on, outcome, error) VALUES(%s, %s, %s, %s, %s, %s)""",
                           [self.name(), uuid, start_time, end_time,
                            result, error])
            # @todo: check to make sure cursor.rowcount == 1 and not 0.
        except MySQLdb.Error as mysql_error:
            mysql.rollback()
            logging.exception(mysql_error)
        mysql.commit()

    def run(self, args):
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
