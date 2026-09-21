from django.conf import settings
from django.test import TestCase, Client

from home.models import OTP


class AuthFlowTests(TestCase):
    def test_local_hosts_are_allowed_for_dev_and_tests(self):
        self.assertIn('localhost', settings.ALLOWED_HOSTS)
        self.assertIn('127.0.0.1', settings.ALLOWED_HOSTS)
        self.assertIn('testserver', settings.ALLOWED_HOSTS)

    def test_login_and_otp_flow_redirects_to_home(self):
        client = Client()

        response = client.post('/', {'mobile': '9999999999'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/verify-otp/')

        otp_obj = OTP.objects.filter(mobile='9999999999').order_by('-created_at').first()
        self.assertIsNotNone(otp_obj)

        verify_response = client.post('/verify-otp/', {'otp': otp_obj.otp})
        self.assertEqual(verify_response.status_code, 302)
        self.assertEqual(verify_response.url, '/home/')
