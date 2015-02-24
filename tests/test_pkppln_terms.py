import unittest
import sys
import _mysql
import logging

from os.path import abspath, dirname
from ConfigParser import ConfigParser

sys.path.append(dirname(dirname(abspath(__file__))))
import pkppln
from tests.pln_testcase import PkpPlnTestCase


class TestPkpPlnTerms(PkpPlnTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPkpPlnTerms, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestPkpPlnTerms, cls).tearDownClass()

    def test_get_term_languages(self):
        languages = pkppln.get_term_languages()
        self.assertIn('en-CA', languages)
        self.assertIn('en-US', languages)
        self.assertNotIn('en-ZZ', languages)

    def test_get_term_keys(self):
        keys = pkppln.get_term_keys()
        self.assertEquals(5, len(keys))
        self.assertIn('utf8.single', keys)
        self.assertIn('utf8.double', keys)
        self.assertIn('utf8.triple', keys)
        self.assertIn('typographic.doublequote', keys)
        self.assertIn('single.anglequote', keys)

    def test_get_term(self):
        terms = pkppln.get_term('utf8.triple')
        self.assertTrue(type(terms) is dict)
        self.assertEquals(u'U+20AC: \u20AC', terms['content'])
        terms = pkppln.get_term('utf8.single', 'en-CA')
        self.assertTrue(type(terms) is dict)
        self.assertEquals(u'I am good to go Canada', terms['content'])
        terms = pkppln.get_term('utf8.triple', 'en-CA')
        self.assertIsNone(terms)
        terms = pkppln.get_term('fooooo')
        self.assertIsNone(terms)

    def test_get_all_terms(self):
        terms = pkppln.get_all_terms()
        self.assertEquals(5, len(terms))
        self.assertEquals(
            5, len([term for term in terms if term['lang_code'] == 'en-US'])
        )
        self.assertSequenceEqual(
            [0, 1, 2, 3, 4], [term['weight'] for term in terms]
        )

        terms = pkppln.get_all_terms('en-CA')
        self.assertEquals(5, len(terms))
        self.assertEquals(
            3, len([term for term in terms if term['lang_code'] == 'en-US'])
        )
        self.assertEquals(
            2, len([term for term in terms if term['lang_code'] == 'en-CA'])
        )
        self.assertSequenceEqual(
            [0, 1, 2, 3, 4], [term['weight'] for term in terms]
        )

        terms = pkppln.get_all_terms('zz-ZZ')
        self.assertEquals(5, len(terms))
        self.assertEquals(
            5, len([term for term in terms if term['lang_code'] == 'en-US'])
        )
        self.assertSequenceEqual(
            [0, 1, 2, 3, 4], [term['weight'] for term in terms]
        )

    def test_get_terms_key(self):
        terms = pkppln.get_terms_key('single.anglequote')
        self.assertEquals(1, len(terms))
        self.assertEquals(5, terms[0]['id'])

        terms = pkppln.get_terms_key('utf8.single')
        self.assertEquals(2, len(terms))
        self.assertEquals(6, terms[0]['id'])
        self.assertEquals(1, terms[1]['id'])

    def test_edit_term(self):
        handle = pkppln.get_connection()
        term = pkppln.get_term('utf8.single', db=handle)
        term['content'] = 'edited.'
        pkppln.edit_term(term, db=handle)
        handle.commit()
        term = pkppln.get_term('utf8.single')
        self.assertEquals('edited.', term['content'])
        self.assertEquals(3, len(pkppln.get_terms_key('utf8.single')))
        pkppln.db_execute('DELETE FROM terms_of_use WHERE id=%s', [term['id']])

    def test_update_term(self):
        handle = pkppln.get_connection()
        term = pkppln.get_term('utf8.single', db=handle)
        term['weight'] = -1
        pkppln.edit_term(term, handle)
        handle.commit()
        term = pkppln.get_term('utf8.single', db=handle)
        self.assertEquals(-1, term['weight'])
        term['weight'] = 0
        pkppln.edit_term(term, handle)
        handle.commit()


pkppln.config_file_name = 'config_test.cfg'
if __name__ == '__main__':  # pragma: no cover
    unittest.main()
