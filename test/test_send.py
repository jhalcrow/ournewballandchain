import unittest
import json
import mock
from ournewballandchain.models import RSVP, Invite
import ournewballandchain.utils

class SendTest(unittest.TestCase):
    def setUp(self):
        self.invite = Invite(
            id = 1,
            name = "Invite Name",
            rsvp_code = "Code"
        )
        self.rsvp = RSVP(
            name = "Name",
            email = "Email",
            guests = 2,
            guest_names = "Guest names",
            attending = True,
            note = "Note",
            qr_used = True,
            code_used = True
        )

    def test_notify_us_ok(self):
        post_resp = mock.Mock()
        post_resp.json.return_value = 'resp'
        expected_body = '''\
Name: Name
Email: Email
Number of Guests: 2
Guest Names: Guest names
Note: Note

QR Code Used: True
Manual Code Used: True
''' % self.rsvp.__dict__

        with mock.patch('ournewballandchain.utils.requests.post') as post, \
                mock.patch('ournewballandchain.utils.handle_mandrill_response') as handler:
            
            post.return_value = post_resp
            ournewballandchain.utils.notify_us(
                self.rsvp,
                'api_key',
                ['jonathan.halcrow@gmail.com',]
            )

            post.assert_called_once()
            self.assertEquals(post.call_args[0][0], 'https://mandrillapp.com/api/1.0/messages/send.json')
            mesg = json.loads(post.call_args[1]['data'])
            self.assertEquals(mesg['key'], 'api_key')
            self.assertEquals(mesg['message']['text'].strip(), expected_body.strip())
            self.assertEquals(mesg['message']['to'], [{'email': 'jonathan.halcrow@gmail.com'}])
            self.assertEquals(mesg['message']['subject'], 'Wedding RSVP: Name is attending')

            handler.assert_called_once_with('resp')


    def test_notify_us_not_attending(self):
        self.rsvp.attending = False
        self.rsvp.guests = None
        self.rsvp.guest_names = None
        post_resp = mock.Mock()
        post_resp.json.return_value = 'resp'
        expected_body = '''\
Name: Name
Email: Email
Number of Guests: None
Guest Names: None
Note: Note

QR Code Used: True
Manual Code Used: True
''' % self.rsvp.__dict__

        with mock.patch('ournewballandchain.utils.requests.post') as post, \
                mock.patch('ournewballandchain.utils.handle_mandrill_response') as handler:
            
            post.return_value = post_resp
            ournewballandchain.utils.notify_us(
                self.rsvp,
                'api_key',
                ['jonathan.halcrow@gmail.com',]
            )

            post.assert_called_once()
            self.assertEquals(post.call_args[0][0], 'https://mandrillapp.com/api/1.0/messages/send.json')
            mesg = json.loads(post.call_args[1]['data'])
            self.assertEquals(mesg['key'], 'api_key')
            self.assertEquals(mesg['message']['text'].strip(), expected_body.strip())
            self.assertEquals(mesg['message']['to'], [{'email': 'jonathan.halcrow@gmail.com'}])
            self.assertEquals(mesg['message']['subject'], 'Wedding RSVP: Name is not attending')

            handler.assert_called_once_with('resp')
  
    def test_handle_normal_response(self):
        resp = \
        [
            {
                "email": "recipient.email@example.com",
                "status": "sent",
                "_id": "abc123abc123abc123abc123abc123"
            }
        ]

        with mock.patch('ournewballandchain.utils.logger') as logger:
            ournewballandchain.utils.handle_mandrill_response(resp)
            logger.info.assert_called_once_with(
                "Notification sent to recipient.email@example.com, status: sent, _id: abc123abc123abc123abc123abc123"
            )

    def test_handle_api_key_error(self):

        resp = {
            "status": "error",
            "code": -1,
            "name": "Invalid_Key",
            "message": "Invalid API key"
        }


        with mock.patch('ournewballandchain.utils.logger') as logger:
            ournewballandchain.utils.handle_mandrill_response(resp)
            logger.error.assert_called_once_with(
                "Error sending response %(status)s %(name)s - %(message)s", resp
            )


    def test_handle_rejected_response(self):
        resp = \
        [
            {
                "email": "recipient.email@example.com",
                "status": "rejected",
                "_id": "abc123abc123abc123abc123abc123"
            }
        ]

        with mock.patch('ournewballandchain.utils.logger') as logger:
            ournewballandchain.utils.handle_mandrill_response(resp)
            logger.error.assert_called_once_with(
                "Error sending to %(email)s, status: %(status)s, _id: %(_id)s", resp[0]
            )

    def test_handle_invalid_response(self):
        resp = \
        [
            {
                "email": "recipient.email@example.com",
                "status": "invalid",
                "_id": "abc123abc123abc123abc123abc123"
            }
        ]

        with mock.patch('ournewballandchain.utils.logger') as logger:
            ournewballandchain.utils.handle_mandrill_response(resp)
            logger.error.assert_called_once_with(
                "Error sending to %(email)s, status: %(status)s, _id: %(_id)s", resp[0]
                )