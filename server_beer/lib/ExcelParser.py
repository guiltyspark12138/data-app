import pandas as pd
from pymongo import MongoClient
import re


class ExcelParser:
    def __init__(self, excelPath):
        self.client = MongoClient('mongodb://as2:9321as2@ds249299.mlab.com:49299/nsw')
        self.path = excelPath
        self.yearColumns = list(pd.read_excel(self.path, skiprows=5).head(0))
        self.df = pd.read_excel(self.path, skiprows=6, skip_footer=14)
        self.columns = list(self.df)
        self.lga = self.path.split('/')[-1].split('lga.xlsx')[0]
        # print(self.columns)
        # with pd.option_context('display.width', 10000, 'display.max_columns', 20):
        #     print(self.df)

    @staticmethod
    def filter(value):
        value = str(value)
        return re.findall('^(.*?)[\^\* ]*$', value)[0]

    def createGroup(self, fromRow, toRow):
        group = {
            'Offence group': self.filter(self.df.iloc[fromRow, 0]),
            'Offence type': []
        }
        for rowId in range(fromRow, toRow):
            row = {self.filter(self.columns[1]): self.filter(self.df.iloc[rowId, 1]),
                   self.filter(self.columns[12]): self.filter(self.df.iloc[rowId, 12]),
                   self.filter(self.columns[13]): self.filter(self.df.iloc[rowId, 13]),
                   self.filter(self.columns[14]): self.filter(self.df.iloc[rowId, 14])}
            for index in range(2, 11, 2):
                row[self.filter(self.yearColumns[index][-4:])] = {
                    'Number of incidents': self.filter(self.df.iloc[rowId, index]),
                    'Rate per 100,000 population': self.filter(self.df.iloc[rowId, index + 1])
                }
            group['Offence type'].append(row)
        return group

    def write(self):
        typeIndex = []
        for i in range(self.df.shape[0]):
            if not pd.isnull(self.df.iloc[i, 0]):
                typeIndex.append(i)
        typeIndex.append(typeIndex[-1] + 1)

        data = []
        for i in range(len(typeIndex) - 1):
            data.append(self.createGroup(typeIndex[i], typeIndex[i + 1]))

        collection = self.client.nsw[self.lga]
        collection.delete_many({})
        collection.insert_many(data)

