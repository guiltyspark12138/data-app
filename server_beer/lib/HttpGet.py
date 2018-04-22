import urllib.request
import shutil


class HttpGet:
    def __init__(self, url, saveDirectory='./storage/', saveName=None, toLower=True, autoDownload=True):
        self.url = url
        self.saveDirectory = saveDirectory
        self.saveName = url.split('/')[-1] if saveName is None else saveName
        if toLower and saveName is None:
            self.saveName = self.saveName.lower()
        self.lastDownloadedFilePath = None
        if autoDownload:
            self.download()

    def download(self):
        with urllib.request.urlopen(self.url) as response, open(self.saveDirectory + self.saveName, 'wb') as file:
            shutil.copyfileobj(response, file)
        self.lastDownloadedFilePath = self.saveDirectory + self.saveName
