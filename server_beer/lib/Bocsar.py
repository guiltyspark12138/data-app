from lib.HttpGet import HttpGet
import urllib.request
import re


class Bocsar:
    def __init__(self):
        url = 'http://www.bocsar.nsw.gov.au/Pages/bocsar_crime_stats/bocsar_lgaexceltables.aspx'
        response = urllib.request.urlopen(url)
        self.excels = re.findall('href=\"(.*?\.xlsx)+?\"', response.read().decode('utf-8'))

    def downloadLgaExcel(self, targetLga):
        for lga in self.excels:
            if '/' + targetLga.replace(' ', '').lower() + 'lga.xlsx' in lga.lower():
                excelUrl = 'http://www.bocsar.nsw.gov.au' + lga
                down = HttpGet(excelUrl)
                return down.lastDownloadedFilePath
        return False
