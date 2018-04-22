import os.path
from datetime import datetime
from lib.Bocsar import Bocsar
from lib.ExcelParser import ExcelParser


class ImportResponse:
    def __init__(self):
        self.USED_TO_UPDATED_BEFORE = 10
        self.UPDATE_SUCCESSFULLY = 11
        self.LGA_HAS_NO_DATA = 20

    def get(self, lga):
        assumedDirectory = './storage/' + lga.replace(' ', '').lower() + 'lga.xlsx'
        if os.path.isfile(assumedDirectory):
            return self.USED_TO_UPDATED_BEFORE, 'LGA data used to be updated before', \
                   datetime.fromtimestamp(os.path.getmtime(assumedDirectory))
        else:
            bocsar = Bocsar()
            file = bocsar.downloadLgaExcel(lga.replace(' ', '').lower())
            if file:
                parser = ExcelParser(file)
                parser.write()
                return self.UPDATE_SUCCESSFULLY, 'LGA data update successfully', \
                       datetime.fromtimestamp(os.path.getmtime(file))
            else:
                return self.LGA_HAS_NO_DATA, 'LGA has no data', datetime.now()
