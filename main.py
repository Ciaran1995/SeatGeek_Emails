""" 
Author: Ciaran McDonnell, 2023

Notes: This code is currently run on the PythonAnywhere free cloud servers. The code is run every day (no choice) at a chosen time. 
My friends and I only wanted to receive emails once a week, hence the first if statement, but this can be changed to anyone's liking.
"""


# Import libraries
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

# Only run on Sundays
if date.today().weekday() == 6:
    # --------- Request details ----------

    # Web page
    url = 'https://api.seatgeek.com/2/events'

    # SeatGeek API client details
    Client_id = '**************************'
    Secret= '*************************************************'

    # Venue Location
    venue_cities = ['Brooklyn','New-York']

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

    # Info required
    cols = ['type','short_title','venue.name','datetime_utc','url']

    # Will loop through each of the cities of interest. Sending one email per city/region.
    for i in range(len(venue_cities)):
        # API request
        response_city = requests.get(f'{url}?per_page={entries_returned}&datetime_utc.gte={date_initial}&datetime_utc.lte={date_final}&venue.city={venue_cities[i]}&lowest_price.lte={max_price}&listing_count.gt={min_ticket_count-1}&client_id={Client_id}')
        # Extract data to JSON format
        r_city = json.loads(response_city.text)
        # Extract JSON data to pandas DataFrame
        df_city = pd.json_normalize(r_city['events'])

        # Only want to work with dataframes when non-zero amount of events are returned
        if df_city.any().any():
            # Group by required columns
            df = df_city.groupby(by=cols,as_index=False).agg({'stats.lowest_price': 'min'})

            # Make date into datetime object for ordering, then back to nice string
            df['datetime_utc'] = df['datetime_utc'].apply(lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'))
            df.sort_values('datetime_utc',inplace=True)
            df['datetime_utc'] = df['datetime_utc'].apply(lambda x: datetime.strftime(x,"%m/%d"))

            # Styling of dataframe for the email
            df.columns = ['Type','Title','Venue','Date','url','Lowest Price']
            df['Lowest Price'] = '$' + df['Lowest Price'].astype(str)
            df = df[['Type','Title','Lowest Price','Venue','Date','url']]


            # ------------ Email ---------------

            # Email account to send from
            sender = '******************'
            # List of emails to send events to
            recipients = ['******************','******************']
            # App password created in email acoount.
            pw = '******************'

            # Building html table of the pandas dataframe for current city.
            body = build_table(df, 'blue_light')

            # Build the email message object
            message = MIMEMultipart()
            message['Subject'] = f"""Events Under ${max_price} in {venue_cities[i]} for the next {future_days} days"""
            message['From'] = sender
            message.attach(MIMEText(body, "html"))
            
            msg_body = message.as_string()
            
            # Send email using SMTP
            server = SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(message['From'], pw)
            server.sendmail(message['From'], recipients, msg_body)
            server.quit()
