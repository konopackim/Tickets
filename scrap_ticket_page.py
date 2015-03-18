
import json
import requests
from datetime import datetime
import os.path
import csv
import cStringIO
import codecs

import pandas as pd

# Get Data from url
def scrap_ticket_page(url):
    payload = {'method': 'GetGridData'}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = r.json()

    if not data['Items']:
        return
    # Save Data to dataframe
    for item in data['Items']:
        item['ScrapDate'] = str(datetime.now().replace(second=0, microsecond=0))
        item[u'QuantityRange'] = item[u'AvailableQuantities'][-1]

    dFrame = pd.DataFrame(data['Items'])
    dFrame = dFrame.set_index(['ScrapDate', 'Id'])
    dFrame = dFrame.drop(['CssPostFix', 'Currency', 'Description',
                          'TicketClass', 'SectionMapName', 'RowMapName',
                          'Seats', 'Row', 'Price',
                          'Package', 'PackageTitle', 'IsRationalizedListing', 'Notes'], 1)
    # Open previous dataframe
    fName = 'tickets_details.csv'
    if os.path.isfile(fName):
        dFrame_old = pd.read_csv(fName, parse_dates=[0], index_col=['ScrapDate', 'Id'], encoding='utf-8')
        dFrame_old = dFrame_old.append(dFrame)
        dFrame_old = dFrame_old.reset_index().drop_duplicates(subset=['ScrapDate', 'Id']).set_index(['ScrapDate', 'Id'])
        # dFrame_old.groupby().first()
    else:
        dFrame_old = dFrame

    dFrame_old.sortlevel(inplace=True)
    dFrame_old.to_csv(fName, encoding='utf-8')

    # print dFrame_old.index