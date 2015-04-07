# -*- coding: utf-8 -*-
# __author__ = 'Dell'
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from lxml import etree
from datetime import datetime
import pandas as pd
import logging

def ajax_complete(driver):
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass



def scrap_artist_page(s_name, url):
    browser = webdriver.PhantomJS(executable_path=
                              'c:\Users\Dell\Downloads\phantomjs-1.9.8-windows\phantomjs-1.9.8-windows\phantomjs.exe')

    # browser = webdriver.Firefox()
    browser.get(url)

    do_click = True
    while do_click:
        try:
            elem = browser.find_element_by_xpath('//*[@id="grid"]/div[2]')
        except :
            logging.warning('Button Next missing')
            break

        if elem.text:
            elem.click()
            WebDriverWait(browser, 10).until(
                ajax_complete,  "Timeout waiting for page to load")
        else:
            do_click = False

    htmlparser = etree.HTMLParser()
    my_tree = etree.fromstring(browser.page_source, htmlparser)
    browser.quit()
    # Create list of all entries with unparsed concert data
    elem_list = my_tree.xpath('//*[@id="grid"]/table/tbody/tr')
    if len(elem_list) == 0:
        return None
    event_list = []
    # print len(elem_list)
    for element in elem_list:
        event_data = dict()
        event_data['event_name'] = s_name
        event_data['event_id'] = element.attrib['data-id']
        event_data['data_navigate'] = 'www.viagogo.com' + element.attrib['data-navigate']
        event_data['datetime'] = datetime.strptime(element.xpath('td[1]/time')[0].attrib['datetime'], '%Y-%m-%dT%H:%M:%S')
        event_data['city'] = element.xpath('td[2]/span[1]/span[1]/span[1]')[0].text
        event_data['country'] = element.xpath('td[2]/span[1]/span[1]/span[2]')[0].text
        event_data['location'] = element.xpath('td[2]/span[1]/span[2]')[0].text
        soon_element = element.xpath('td[3]/div')
        if soon_element:
            # print soon_element
            if u'Soon' in soon_element[0].text:
                # If the are no tickets: On Sale Soon
                continue
        event_list.append(event_data)

    dFrame = pd.DataFrame(event_list, columns=['event_id',
                                               'event_name',
                                               'datetime',
                                               'city',
                                               'country',
                                               'location',
                                               'data_navigate'])
    dFrame.set_index('event_id', inplace=True)

    return dFrame

