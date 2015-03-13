import sys
from os.path import abspath, dirname
import abc
from abc import abstractmethod

sys.path.append(dirname(dirname(abspath(__file__))))
from tests.pln_testcase import PkpPlnTestCase


class ProcessingTestCase(PkpPlnTestCase):

    __metaclass__ = abc.ABCMeta

