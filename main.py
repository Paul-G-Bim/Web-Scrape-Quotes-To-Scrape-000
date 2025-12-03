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
# handle graceful exit on critical error
import sys

# --- CONFIGURATION ---

# website to be scraped
url = "https://quotes.toscrape.com/"

# define output directory, use absolute to improve reliability in scheduled tasks
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_quotes')

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

print(f"Starting quote scraper at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- Directory Setup for Error Handling ---

try:
    # create output directory if it does not exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory confirmed: {OUTPUT_DIR}")
except OSError as e:
    # Handles issues like permission errors or invalid path
    print(f"CRITICAL ERROR: Could not create output directory {OUTPUT_DIR}. Error: {e}")
    sys.exit(1)  # Exit the script if output can't be saved

# --- Network Request/Handling Error

try:
    # request the page
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
    print(f"Successfully retrieved page (Status: {response.status_code})")
except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error occurred: {errh}")
    sys.exit(1)
except requests.exceptions.ConnectionError as errc:
    print(f"Connection Error occurred: {errc} (Check network or URL)")
    sys.exit(1)
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error occurred: {errt}")
    sys.exit(1)
except requests.exceptions.RequestException as err:
    # Catches all other requests exceptions
    print(f"An unexpected Request Error occurred: {err}")
    sys.exit(1)

# --- Parsing and Data Extraction Error Handling ---

# check request success
try:
    # parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the container for the quotes
    # found in <div class="quote"
    quotes_list = soup.find_all('div', class_='quote')

    if not quotes_list:
        print("WARNING: Could not find any quotes. Website structure may have changed.")
        # Proceed, but the output file will be empty or only contain headers

    data = []

    # loop through each quote container to extract info
    for quote in quotes_list:
        try:
            # Check for the existence of elements before calling .get_text(
            text_span = quote.find('span', class_='text')
            author_small = quote.find('small', class_='author')

            # Use a default value if the element is missing
            text = text_span.get_text() if text_span else "N/A - Missing Text"
            author = author_small.get_text() if author_small else "N/A - Missing Author"

            # store in a dictionary
            data.append({
                'Quote': text,
                'Author': author
            })

        except Exception as e:
            # Handles unexpected errors within the parsing loop
            print(f"Error processing a single quote block: {e}")
            continue  # Skip this broken quote and continue with the next one

except Exception as e:
    print(f"CRITICAL ERROR: Failed during HTML parsing or data compilation: {e}")
    sys.exit(1)

# --- 4. File Saving Error Handling ---
if data:
    try:
        # save to csv using pandas, using the dynamic OUTPUT_PATH
        df = pd.DataFrame(data)
        df.to_csv(OUTPUT_PATH, index=False)

        print(f"Success! Saved {len(data)} quotes to {OUTPUT_PATH}")

    except Exception as e:
        print(f"CRITICAL ERROR: Failed to save data to CSV file. Error: {e}")
        sys.exit(1)

else:
    print("Script finished. No data was scraped, CSV file was not created.")

print("Script finished successfully.")