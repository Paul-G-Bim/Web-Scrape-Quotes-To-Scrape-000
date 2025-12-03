import requests
from bs4 import BeautifulSoup
import pandas as pd
# no need for time in this case since script only hits the page once
# import time
# in terms of automating the script you might want to store the automatically
# generated files in a specific folder so import os
import os
# to ensure each automated file has a different name make a timestamp
import datetime

# --- CONFIGURATION ---

# website to be scraped
url = "https://quotes.toscrape.com/"

# define output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'scraped_quotes')

# generate unique filenames
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
FILENAME = f'quotes_{timestamp}.csv'

# combine directory and filename
OUTPUT_PATH = os.path.join(OUTPUT_DIR, FILENAME)

# user agent string
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- SCRIPT EXECUTION ---

# create output directory if it does not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# request the page
response = requests.get(url, headers=headers, timeout=15)

# check request success
if response.status_code == 200:
    # parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the container for the quotes
    # found in <div class="quote"
    quotes_list = soup.find_all('div', class_='quote')

    data = []

    # loop through each quote container to extract info
    for quote in quotes_list:
        text = quote.find('span', class_='text').get_text()
        author = quote.find('small', class_='author').get_text()

        # store in a dictionary
        data.append({
            'Quote': text,
            'Author': author
        })

    # save to csv using pandas, using the dynamic OUTPUT_PATH
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Success! Saved quotes to my_quotes.csv")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")