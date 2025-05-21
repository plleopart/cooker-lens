from abc import ABC, abstractmethod


class Downloader(ABC):
    """
    Abstract base class for downloading files.
    """

    @abstractmethod
    def __init__(self, url: str):
        """
        Initialize the downloader with a URL.
        """
        self.url = url

    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of the post.
        """
        pass

    @abstractmethod
    def download(self) -> str:
        """
        Download the file and return filename.
        """
        pass
