import os
import unittest
import tempfile
import logging
from ournewballandchain import create_app, db, Invite, RSVP, TestConfig, rsvp
from mock import patch


class RSVPTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.logger.setLevel(logging.CRITICAL)
        self.test_client = self.app.test_client()

        with self.app.app_context():
            self.connection = db.engine.connect()
            self.transaction = self.connection.begin()
            self.invite = Invite(rsvp_code='TEST', name='Joe Blo')
            db.session.add(self.invite)
            db.session.commit()
            self.invite_id = self.invite.id

    def tearDown(self):
        self.transaction.rollback()

    def test_simple(self):
        rv = self.test_client.get('/rsvp/form')
        self.assertEquals(rv.status_code, 200)

    def test_qr_get(self):
        rv = self.test_client.get('/rsvp/form?code=TEST')
        self.assertEquals(rv.status_code, 200)
        self.assertTrue('Joe Blo' in rv.data)

    def test_qr_post(self):
        with patch('ournewballandchain.rsvp.rsvp_notify'):
            rv = self.test_client.post('/rsvp/form?code=TEST', 
                data={
                    'email':'test@test.com',
                    'attending':'1',
                    'guests':'2',
                    'guest_names': 'a, b',
                    'note':'TEST NOTE',
                },
                follow_redirects=True
            )
            self.assertEquals(rv.status_code, 200)
            self.assertEquals(rsvp.rsvp_notify.call_count, 1)
            #import pdb; pdb.set_trace()
            used_rsvp = rsvp.rsvp_notify.call_args[0][0]

            with self.app.app_context():
                db.session.add(used_rsvp) # Reattach to session
                used_invite = used_rsvp.invite
                found_rsvp = db.session.query(RSVP).filter_by(invite_id=self.invite.id).one()
                self.assertEquals(used_rsvp.id, found_rsvp.id)

            self.assertEquals(used_rsvp.email, 'test@test.com')
            self.assertEquals(used_rsvp.attending, True)
            self.assertEquals(used_rsvp.guests, 2)
            self.assertEquals(used_rsvp.guest_names, 'a, b')
            self.assertEquals(used_rsvp.note, 'TEST NOTE')
            self.assertEquals(used_rsvp.invite_id, self.invite.id)
            self.assertEquals(used_invite.id, self.invite_id)
            self.assertEquals(used_rsvp.qr_used, False)
            self.assertEquals(used_rsvp.code_used, True)

    def test_qr_post_with_code(self):
        with patch('ournewballandchain.rsvp.rsvp_notify'):
            rv = self.test_client.post('/rsvp/form?code=TEST&qr_used=1', 
                data={
                    'email':'test@test.com',
                    'attending':'1',
                    'guests':'2',
                    'guest_names': 'a, b',
                    'note':'TEST NOTE',
                },
                follow_redirects=True
            )
            self.assertEquals(rv.status_code, 200)
            self.assertEquals(rsvp.rsvp_notify.call_count, 1)
            #import pdb; pdb.set_trace()
            used_rsvp = rsvp.rsvp_notify.call_args[0][0]
            used_invite = rsvp.rsvp_notify.call_args[0][1]
            with self.app.app_context():
                db.session.add(used_rsvp) # Reattach to session
                used_invite = used_rsvp.invite
                found_rsvp = db.session.query(RSVP).filter_by(invite_id=self.invite.id).one()
                self.assertEquals(used_rsvp.id, found_rsvp.id)

            self.assertEquals(used_rsvp.email, 'test@test.com')
            self.assertEquals(used_rsvp.attending, True)
            self.assertEquals(used_rsvp.guests, 2)
            self.assertEquals(used_rsvp.guest_names, 'a, b')
            self.assertEquals(used_rsvp.note, 'TEST NOTE')
            self.assertEquals(used_rsvp.invite_id, self.invite.id)
            self.assertEquals(used_invite.id, self.invite_id)
            self.assertEquals(used_rsvp.qr_used, True)
            self.assertEquals(used_rsvp.code_used, True)

    def test_regular_post(self):
        with patch('ournewballandchain.rsvp.rsvp_notify'):
            rv = self.test_client.post('/rsvp/form', 
                data={
                    'name': 'Test',
                    'email':'test@test.com',
                    'attending':'1',
                    'guests':'2',
                    'guest_names': 'a, b',
                    'note':'TEST NOTE',
                },
                follow_redirects=True
            )
            self.assertEquals(rv.status_code, 200)
            self.assertEquals(rsvp.rsvp_notify.call_count, 1)
            #import pdb; pdb.set_trace()
            used_rsvp = rsvp.rsvp_notify.call_args[0][0]
            used_invite = rsvp.rsvp_notify.call_args[0][1]
            with self.app.app_context():
                db.session.add(used_rsvp) # Reattach to session
                found_rsvp = db.session.query(RSVP).filter_by(name='Test').one()
                self.assertEquals(used_rsvp.id, found_rsvp.id)

            self.assertEquals(used_rsvp.name, 'Test')
            self.assertEquals(used_rsvp.email, 'test@test.com')
            self.assertEquals(used_rsvp.attending, True)
            self.assertEquals(used_rsvp.guests, 2)
            self.assertEquals(used_rsvp.guest_names, 'a, b')
            self.assertEquals(used_rsvp.note, 'TEST NOTE')
            self.assertEquals(used_rsvp.invite_id, None)
            self.assertEquals(used_rsvp.qr_used, False)
            self.assertEquals(used_rsvp.code_used, False)


if __name__ == '__main__':
    unittest.main()