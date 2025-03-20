import random
import string

class GmailAliasGenerator:
    """Generates unique Gmail aliases by appending random characters with dots."""

    def __init__(self, base_email):
        self.username, self.domain = base_email.split('@')

    def generate_aliases(self, num_aliases):
        """
        Generate a specified number of Gmail aliases.

        Args:
            num_aliases (int): Number of aliases to generate.

        Returns:
            list: List of unique Gmail aliases.
        """
        aliases = []
        for _ in range(num_aliases):
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            alias = f"{self.username}.{suffix}@{self.domain}"
            aliases.append(alias)
        return aliases