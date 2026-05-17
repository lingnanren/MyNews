from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from config import load_config


class EmailConfigTest(unittest.TestCase):
    def test_email_config_reads_recipient_list(self) -> None:
        env = {
            "SMTP_USER": "sender@example.com",
            "SMTP_PASSWORD": "secret",
            "RECIPIENT_EMAILS": "a@example.com,b@example.com",
        }
        with patch.dict(os.environ, env, clear=False):
            config = load_config()
        self.assertEqual(config.smtp_user, "sender@example.com")
        self.assertEqual(config.recipients, ("a@example.com", "b@example.com"))


if __name__ == "__main__":
    unittest.main()
