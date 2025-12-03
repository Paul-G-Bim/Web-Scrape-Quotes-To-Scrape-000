import requests
from bs4 import BeautifulSoup
import pandas as pd
# no need for time in this case since script only hits the page once
# import time

# website to be scraped
url = "https://quotes.toscrape.com/"

# appear human
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# request the page
response = requests.get(url, headers=headers)

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

    # save to csv using pandas
    df = pd.DataFrame(data)
    df.to_csv('my_quotes.csv', index=False)

    print("Success! Saved quotes to my_quotes.csv")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")