from playwright.sync_api import sync_playwright
import random
import string

class RegistrationHandler:
    """Handles the registration process using Playwright."""

    def __init__(self, proxy, profile_dir):
        """
        Initialize the browser with proxy and profile.

        Args:
            proxy (dict): Proxy configuration.
            profile_dir (str): Browser profile directory.
        """
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            proxy={
                "server": f"http://{proxy['ip']}:{proxy['port']}",
                "username": proxy['username'],
                "password": proxy['password']
            },
            headless=True
        )
        self.page = self.context.new_page()

    def generate_password(self):
        """Generate a random 12-character password."""
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))

    def register_account(self, email, captcha_solver):
        """
        Register a Hoyoverse account.

        Args:
            email (str): Gmail alias for registration.
            captcha_solver (CaptchaSolver): Instance to solve CAPTCHAs.

        Returns:
            tuple: (email, password) if successful, else raises an exception.
        """
        try:
            self.page.goto("https://account.hoyoverse.com/register")  # Hypothetical URL
            self.page.fill('input[name="email"]', email)  # Adjust selector as needed
            password = self.generate_password()
            self.page.fill('input[name="password"]', password)
            self.page.fill('input[name="confirm_password"]', password)

            # Handle CAPTCHA if present
            if self.page.is_visible('.g-recaptcha'):  # Adjust selector
                sitekey = self.page.query_selector('.g-recaptcha').get_attribute('data-sitekey')
                token = captcha_solver.solve_recaptcha(sitekey, self.page.url)
                self.page.evaluate(f"document.getElementById('g-recaptcha-response').innerHTML = '{token}';")

            self.page.click('button[type="submit"]')
            self.page.wait_for_load_state('networkidle', timeout=30000)
            return email, password
        except Exception as e:
            raise Exception(f"Registration failed: {e}")

    def activate_account(self, link):
        """
        Activate the account by visiting the confirmation link.

        Args:
            link (str): Activation URL from the email.
        """
        self.page.goto(link)
        self.page.wait_for_load_state('networkidle', timeout=30000)

    def close(self):
        """Close the browser context and Playwright instance."""
        self.context.close()
        self.playwright.stop()