import os
import shutil

from app.config import TEMP_BASE_DIR
from app.downloader.downloader import Downloader
import instaloader
import re


class InstagramDownloader(Downloader):
    def __init__(self, url):
        self.url = url
        self.loader = instaloader.Instaloader()
        self.mp4_file = None
        self.miniature_file = None
        self.description = None

    def get_shortcode_from_url(self):
        """
        Extracts the shortcode from an Instagram URL.
        Example: https://www.instagram.com/p/CzYw2bPq8aJ/ -> CzYw2bPq8aJ
        """
        match = re.search(r"/(p|reel|tv)/([A-Za-z0-9_-]+)/?", self.url)
        if match:
            return match.group(2)
        else:
            raise ValueError("Invalid URL or shortcode not found.")

    def get_description(self):
        return self.description

    def get_miniature(self) -> str | None:
        return self.miniature_file

    def download(self):
        shortcode = self.get_shortcode_from_url()
        post = instaloader.Post.from_shortcode(self.loader.context, shortcode)

        self.description = post.caption

        current_dir = os.getcwd()
        try:
            os.chdir(TEMP_BASE_DIR)
            self.loader.download_post(post, target=shortcode)

            created_folder = os.path.join(TEMP_BASE_DIR, shortcode)
            for filename in os.listdir(created_folder):
                src = os.path.join(created_folder, filename)

                final_filename = f"{shortcode}_{filename}"
                target = os.path.join(TEMP_BASE_DIR, final_filename)
                if filename.endswith(".mp4"):
                    self.mp4_file = final_filename
                elif filename.endswith(".jpg"):
                    self.miniature_file = target

                shutil.move(src, target)

            shutil.rmtree(created_folder)

        finally:
            os.chdir(current_dir)

        return self.mp4_file
