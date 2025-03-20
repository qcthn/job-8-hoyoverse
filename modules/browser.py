import tempfile
import shutil

class BrowserProfileManager:
    """Manages temporary browser profiles."""

    def __init__(self):
        self.profiles = []

    def create_profile(self):
        """
        Create a new temporary browser profile directory.

        Returns:
            str: Path to the profile directory.
        """
        profile_dir = tempfile.mkdtemp()
        self.profiles.append(profile_dir)
        return profile_dir

    def cleanup(self):
        """Remove all temporary profile directories."""
        for profile_dir in self.profiles:
            try:
                shutil.rmtree(profile_dir)
            except Exception as e:
                print(f"Error cleaning up {profile_dir}: {e}")
        self.profiles.clear()