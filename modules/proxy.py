class ProxyManager:
    """Manages a list of proxies for IP rotation."""

    def __init__(self, proxy_list):
        """
        Initialize with a list of proxy strings.

        Args:
            proxy_list (list): List of proxies in format 'IP:Port:Username:Password'.
        """
        self.proxies = [self._parse_proxy(p.strip()) for p in proxy_list if p.strip()]
        self.index = 0
        self.accounts_per_proxy = {}  # Tracks accounts per proxy IP

    def _parse_proxy(self, proxy_str):
        """
        Parse a proxy string into a dictionary.

        Args:
            proxy_str (str): Proxy in format 'IP:Port:Username:Password'.

        Returns:
            dict: Proxy configuration.
        """
        ip, port, username, password = proxy_str.split(':')
        return {'ip': ip, 'port': port, 'username': username, 'password': password}

    def get_next_proxy(self):
        """
        Get the next available proxy, cycling through the list.

        Returns:
            dict: Proxy configuration.

        Raises:
            ValueError: If no proxies are available.
        """
        if not self.proxies:
            raise ValueError("No proxies provided.")
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        self.accounts_per_proxy.setdefault(proxy['ip'], 0)
        return proxy