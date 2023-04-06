import pandas as pd
import requests
import json
from datetime import datetime
from datetime import timedelta
from datetime import date

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pretty_html_table import build_table

if date.today().weekday() == 6:
    # --------- Request details ----------

    # Web page
    url = 'https://api.seatgeek.com/2/events'

    # My details
    Client_id = 'MzE2OTE3Njd8MTY3NTAzNTM4My44NjYxMDQ2'
    Secret= '111bd39e7406db3b640812eb23e3c3a5968521dbd20f0b7e740a30bb80c1e007'

    # Venue Location
    venue_cities = ['Brooklyn','New-York']

    # Venue ID
    MSG = ''
    Barclays = '7546'

    # Dates
    now = datetime.now()
    future_days = 7
    one_week = now +timedelta(days=future_days)

    date_initial = now.strftime("%Y-%m-%d ")
    date_final= one_week.strftime("%Y-%m-%d ")

    # Filter details
    max_price = 50
    min_ticket_count = 2
    home_team = ''
    team2 = ''

    entries_returned = 100

    # --------- API Request -----------
    dfs = []
    # Info required
    cols = ['type','short_title','venue.name','datetime_utc','url']


    for i in range(len(venue_cities)):
        response_city = requests.get(f'{url}?per_page={entries_returned}&datetime_utc.gte={date_initial}&datetime_utc.lte={date_final}&venue.city={venue_cities[i]}&lowest_price.lte={max_price}&listing_count.gt={min_ticket_count-1}&client_id={Client_id}')
        r_city = json.loads(response_city.text)
        df_city = pd.json_normalize(r_city['events'])

        if df_city.any().any():
            # Group by required columns
            df = df_city.groupby(by=cols,as_index=False).agg({'stats.lowest_price': 'min'})

            # Make date into datetime object for ordering, then back to nice string
            df['datetime_utc'] = df['datetime_utc'].apply(lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'))
            df.sort_values('datetime_utc',inplace=True)
            df['datetime_utc'] = df['datetime_utc'].apply(lambda x: datetime.strftime(x,"%m/%d"))

            # Styling
            df.columns = ['Type','Title','Venue','Date','url','Lowest Price']
            df['Lowest Price'] = '$' + df['Lowest Price'].astype(str)
            df = df[['Type','Title','Lowest Price','Venue','Date','url']]

            #dfs.append(df)

            ### ------------ Email ---------------

            sender = '******************'
            recipients = ['******************']
            pw = '******************'


            body = build_table(df, 'blue_light')


            message = MIMEMultipart()
            message['Subject'] = f"""Events Under ${max_price} in {venue_cities[i]} for the next {future_days} days"""
            message['From'] = sender
            #message['To'] = ", ".join(recipients)

            body_content = body
            message.attach(MIMEText(body, "html"))
            msg_body = message.as_string()

            server = SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(message['From'], pw)
            server.sendmail(message['From'], recipients, msg_body)
            server.quit()
