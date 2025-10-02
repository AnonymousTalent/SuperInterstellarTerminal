import json
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path to allow importing the app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notification_app.main import app

class BankWebhookTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client for the Flask application."""
        self.app = app.test_client()
        self.app.testing = True
        # Set environment variables for testing
        os.environ['BANK_CTBC_CODE'] = '822'
        os.environ['BANK_CTBC_ACCOUNT'] = '484540302460'

    @patch('notification_app.main.notify_all')
    def test_successful_transaction(self, mock_notify_all: MagicMock):
        """Test a successful bank transfer webhook call."""
        payload = {
            "bank_code": "822",
            "account": "484540302460",
            "amount": 10000,
            "from_bank": "Test Bank"
        }
        response = self.app.post('/bank_webhook',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('my_share', data)
        self.assertIn('system_share', data)
        self.assertEqual(data['my_share'], 2500.0)  # 10000 * 0.25
        self.assertEqual(data['system_share'], 7500.0) # 10000 * 0.75

        # Verify that the notification function was called
        mock_notify_all.assert_called_once()
        call_args = mock_notify_all.call_args[0][0]
        self.assertIn("Lightning Empire 金流入帳確認", call_args)
        self.assertIn("你的收益 25% → 2,500.0", call_args)
        self.assertIn("系統保管 75% → 7,500.0", call_args)


    @patch('notification_app.main.notify_all')
    def test_incorrect_account_number(self, mock_notify_all: MagicMock):
        """Test a transaction with an incorrect account number."""
        payload = {
            "bank_code": "822",
            "account": "000000000000", # Incorrect account
            "amount": 5000,
            "from_bank": "Test Bank"
        }
        response = self.app.post('/bank_webhook',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data, {"status": "error"})

        # Verify that the notification function was called with an error message
        mock_notify_all.assert_called_once()
        call_args = mock_notify_all.call_args[0][0]
        self.assertIn("❌ 帳戶不符", call_args)

    @patch('notification_app.main.notify_all')
    def test_unknown_bank_code(self, mock_notify_all: MagicMock):
        """Test a transaction with an unknown bank code."""
        payload = {
            "bank_code": "999", # Unknown bank
            "account": "484540302460",
            "amount": 5000,
            "from_bank": "Test Bank"
        }
        response = self.app.post('/bank_webhook',
                                 data=json.dumps(payload),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data, {"status": "error"})

        # Verify that the notification function was called with an error message
        mock_notify_all.assert_called_once()
        call_args = mock_notify_all.call_args[0][0]
        self.assertIn("❌ 帳戶不符", call_args)

if __name__ == '__main__':
    unittest.main()