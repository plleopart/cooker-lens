from app.config import ALLOWED_MEDIA_ORIGINS_LIST
from app.downloader.downloader import Downloader
from app.downloader.tiktok_downloader import TikTokDownloader


class MediaDownloader(Downloader):
    def __init__(self, url: str):
        self.url = url
        self.allowed_origins = ALLOWED_MEDIA_ORIGINS_LIST

        if not any(origin in url for origin in self.allowed_origins):
            raise ValueError(f"URL origin not allowed. Allowed origins are: {self.allowed_origins}")

        self.downloader = self.get_downloader()

    def get_description(self) -> str:
        return self.downloader.get_description()

    def download(self):
        return self.downloader.download()

    def get_downloader(self) -> Downloader:
        if "tiktok" in self.url:
            return TikTokDownloader(self.url)
        elif "instagram" in self.url:
            raise NotImplementedError("Instagram downloader is not implemented yet.")
