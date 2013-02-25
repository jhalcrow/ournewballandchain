import os
import ournewballandchain
import unittest
import tempfile

class RSVPTestCase(unittest.TestCase):

    def setUp(self):
        self.app = ournewballandchain.create_app(ournewballandchain.TestConfig).test_client()

    def test_simple(self):
        rv = self.app.get('/rsvp')
        self.assertEquals(rv.status_code, 200)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()