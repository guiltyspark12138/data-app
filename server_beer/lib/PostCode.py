import pandas as pd


class PostCode:
    def __init__(self):
        lga = pd.read_excel('./storage/Australian LGA postcode mappings (2011 data).xlsx')
        self.nsw = lga[lga['State'] == 'New South Wales']

    def getLgasByCode(self, code):
        lgaList = []
        lgas = self.nsw[self.nsw['Postcode'] == code]
        for index, lga in lgas.iterrows():
            lgaList.append(lga['LGA region'])
        return lgaList

    def getCodesByLga(self, lga):
        codeList = []
        for index in range(self.nsw.shape[0]):
            if self.nsw.iloc[index, 1].replace(' ', '').lower() == lga.replace(' ', '').lower():
                codeList.append(str(self.nsw.iloc[index, 2]))
        return codeList
