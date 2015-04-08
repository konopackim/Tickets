__author__ = 'Dell'
import sqlalchemy
from scrap_artist_page import *
from scrap_ticket_page import *
import pandas as pd
from datetime import datetime
import sqlite3
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    eng = sqlalchemy.create_engine('sqlite:///tickets.db')
    # eng = sqlite3.connect("tickets.db")
    # print eng.table_names()
    d_artists = {'One Direction': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/One-Direction-Tickets',
                 'Katy Perry': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/Katy-Perry-Tickets',
                 'U2': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/U2-Tickets',
                 'Michael Buble': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/Michael-Buble-Tickets',
                 'Madonna': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/Madonna-Tickets',
                 'Eric Clapton': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/Eric-Clapton-Tickets',
                 'Paul McCartney': 'http://www.viagogo.com/ww/Concert-Tickets/Rock-and-Pop/Paul-McCartney-Tickets',
                 'Kana Nishino': 'http://www.viagogo.com/ww/Concert-Tickets/J-Pop/Kana-Nishino-Tickets'
                 }

    # Get all info about events
    # and add them to the database
    df_events = pd.read_sql('events', eng, index_col='event_id')
    df_events_today = pd.DataFrame()
    for s_name, url in d_artists.iteritems():
        logging.info('%s %s' % (s_name, url))
        df_event = scrap_artist_page(s_name, url)
        if df_event is None:
            continue
        logging.info(df_event.count())
        # if len(df_events_today) == 0:
        #     df_events_today = df_event
        # else:
        df_events_today = df_events_today.append(df_event)
    df_events.append(df_events_today)
    df_events.drop_duplicates()
    # df_events.reset_index().sort_index(by=['event_name', 'event_id'], ascending=[True, True]).set_index('event_id', inplace=True)
    # logging.info(df_events)
    # events_navigate = df_events[['event_name', 'data_navigate']].unique()
    df_events.to_sql('events', eng, if_exists='replace', index=True)
    df_events.to_csv('logs\events_%s.csv' % datetime.today().date(), encoding='utf-8')

    tickets_today = pd.DataFrame()
    for index, event in df_events_today.iterrows():
        logging.info('%s %s %s' % (event['event_name'], event['datetime'], datetime.now().time()))
        e_url = event['data_navigate']
        tickets = scrap_ticket_page('http://' + e_url)
        # logging.info(tickets)
        tickets_today = tickets_today.append(tickets)
    logging.info(tickets_today.count())
    logging.info(tickets_today.dtypes)
    logging.info('%s: Started: Sending tickets data into database' % datetime.now().time())
    tickets_today.to_sql('tickets', eng, if_exists='append', index=True)
    logging.info('%s: Finished: Sending tickets data into database' % datetime.now().time())


if __name__ == "__main__":
    main()