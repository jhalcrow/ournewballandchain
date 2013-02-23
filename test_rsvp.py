from rsvp import edit_distance
import unittest

class RSVPTest(unittest.TestCase):

    def test_editdist(self):
        self.assertEquals(edit_distance('kitten', 'sitten'), 1)
        self.assertEquals(edit_distance('sitten', 'sitting'), 2)
