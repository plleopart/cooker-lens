from app.config import TEMP_BASE_DIR

import os


class Garbage:
    def __init__(self, post: str):
        self.post = post

    def clean(self):
        """
        Clean up the temporary files.
        """
        try:
            for file in os.listdir(TEMP_BASE_DIR):
                if file.startswith(self.post):
                    os.remove(os.path.join(TEMP_BASE_DIR, file))
        except Exception as e:
            raise Exception(f"Error while cleaning up: {e}")
