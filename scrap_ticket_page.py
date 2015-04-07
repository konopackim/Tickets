
import json
import requests
import datetime
import os.path
import csv
import cStringIO
import codecs
import logging

import pandas as pd

# Get Data from url
def scrap_ticket_page(url):
    payload = {'method': 'GetGridData'}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    # logging.info(r)
    data = r.json()

    if not data['Items']:
        return
    # Save Data to dataframe
    for item in data['Items']:
        item['ScrapDate'] = datetime.datetime.now().replace(second=0, microsecond=0)
        item[u'QuantityRange'] = item[u'AvailableQuantities'][-1]

    dFrame = pd.DataFrame(data['Items'])

    dFrame = dFrame.drop(['CssPostFix', 'Currency', 'Description',
                          'TicketClass', 'SectionMapName', 'RowMapName',
                          'Seats', 'Row', 'Price',
                          'Package', 'PackageTitle', 'IsRationalizedListing', 'Notes', 'BuyUrl'], 1)
    dFrame['ETicketType'] = dFrame['ETicketType'].astype(bool)
    dFrame['EventAllowPublicPurchase'] = dFrame['EventAllowPublicPurchase'].astype(bool)
    dFrame[u'AvailableQuantities'] = dFrame[u'AvailableQuantities'].astype(unicode)
    dFrame = dFrame.set_index(['ScrapDate', 'Id'])


    return dFrame