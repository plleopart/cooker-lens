import os
import shutil

import pyktok as pyk

from app.config import TEMP_BASE_DIR
from app.downloader.downloader import Downloader


class TikTokDownloader(Downloader):
    def __init__(self, url: str):
        self.url = url

        # pyk.specify_browser(PYKTOK_BROWSER)

        try:
            self.content = pyk.alt_get_tiktok_json(url)
            self.struct = self.content.get('__DEFAULT_SCOPE__').get('webapp.video-detail').get('itemInfo').get(
                'itemStruct')
            self.description = self.struct.get('desc')
        except:
            raise ValueError("Invalid TikTok URL or unable to fetch content.")

    def get_description(self) -> str:
        return self.description

    def download(self) -> str:
        origin_path = os.getcwd()
        target_path = TEMP_BASE_DIR
        print(pyk.save_tiktok(self.url, True, ""))
        files = os.listdir(origin_path)
        latest_file = max([os.path.join(origin_path, f) for f in files], key=os.path.getctime)
        latest_filename = os.path.basename(latest_file)
        print(f"Moving {latest_file} to {target_path}/{latest_filename}")
        shutil.copy2(latest_file, os.path.join(target_path, latest_filename))
        os.remove(latest_file)
        return latest_filename

    def get_miniature(self) -> str | None:
        return None
