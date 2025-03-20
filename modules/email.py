import imaplib
import email
from bs4 import BeautifulSoup
import time

class EmailHandler:
    """Handles retrieval of confirmation emails from Gmail."""

    def __init__(self, gmail_user, gmail_password):
        """
        Initialize IMAP connection to Gmail.

        Args:
            gmail_user (str): Gmail address.
            gmail_password (str): Gmail app-specific password.
        """
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.mail.login(gmail_user, gmail_password)
        self.mail.select("inbox")

    def get_activation_link(self, email_alias, timeout=120):
        """
        Retrieve the activation link from a confirmation email.

        Args:
            email_alias (str): Gmail alias to search for.
            timeout (int): Max seconds to wait for the email.

        Returns:
            str: Activation URL, or None if not found.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.mail.recent()  # Check for new emails
            status, messages = self.mail.search(None, f'(TO "{email_alias}" FROM "noreply@hoyoverse.com")')
            if status == "OK" and messages[0]:
                for num in messages[0].split():
                    status, msg_data = self.mail.fetch(num, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/html":
                                        html = part.get_payload(decode=True).decode(errors='ignore')
                                        soup = BeautifulSoup(html, 'html.parser')
                                        link_tag = soup.find('a', string=lambda t: "activate" in t.lower())
                                        if link_tag:
                                            return link_tag['href']
            time.sleep(5)
        return None

    def close(self):
        """Close the IMAP connection."""
        self.mail.logout()