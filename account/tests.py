from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils.translation import gettext_lazy as _


class EmailsTestCase(TestCase):
    def test_send_welcome_email(self):
        user = get_user_model().objects.create_user(
            email="peter.pan@dpsg1300.de",
            first_name="Peter",
            last_name="Pan",
        )

        user.send_welcome_email()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, _('Welcome'))
        self.assertIn('Peter', mail.outbox[0].body)
