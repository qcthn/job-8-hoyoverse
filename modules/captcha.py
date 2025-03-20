import requests
import time

class CaptchaSolver:
    """Handles CAPTCHA solving using 2Captcha."""

    def __init__(self, api_key):
        """
        Initialize with 2Captcha API key.

        Args:
            api_key (str): 2Captcha API key.
        """
        self.api_key = api_key
        self.base_url = "http://2captcha.com"

    def solve_recaptcha(self, sitekey, url):
        """
        Solve a reCAPTCHA challenge.

        Args:
            sitekey (str): reCAPTCHA site key.
            url (str): Page URL with the CAPTCHA.

        Returns:
            str: CAPTCHA solution token.

        Raises:
            Exception: If solving fails after retries.
        """
        # Submit CAPTCHA request
        response = requests.get(
            f"{self.base_url}/in.php",
            params={
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": sitekey,
                "pageurl": url,
                "json": 1
            }
        ).json()

        if response["status"] != 1:
            raise Exception(f"CAPTCHA submission failed: {response['request']}")

        captcha_id = response["request"]

        # Poll for solution
        for _ in range(20):  # Max 100 seconds
            result = requests.get(
                f"{self.base_url}/res.php",
                params={"key": self.api_key, "action": "get", "id": captcha_id, "json": 1}
            ).json()
            if result["status"] == 1:
                return result["request"]
            time.sleep(5)
        raise Exception("CAPTCHA solving timed out.")