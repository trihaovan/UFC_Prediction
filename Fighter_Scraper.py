# Imports
print('Importing Packages...')
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

print('Initialising...')
# Create a list of all lowercase english letters
letters = [chr(i) for i in range(ord('a'), ord('z')+1)]

# Define user-agent for requests
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"


# Define a function to scrape fighter details
@retry(stop=stop_after_attempt(8), wait=wait_fixed(2))
def get_fighter_rows(letter):
    # Initialise a requests session and updating its headers
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    # Define the URL
    main_url = f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'
    
    # Make a GET request to the URL
    main_response = session.get(main_url)
    
    # Parse the HTML response
    main_soup = BeautifulSoup(main_response.content, 'lxml')
    
    # Find all the rows of fighter stats
    fighter_rows = main_soup.find_all('tr', class_="b-statistics__table-row")[2:]
    
    # Use ThreadPoolExecutor to concurrently run get_fighter_details function on all rows
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        fighter_details = list(executor.map(lambda row: get_fighter_details(row), fighter_rows))
        
    return fighter_details

# Define a function to scrape fighter details from a row
@retry(stop=stop_after_attempt(8), wait=wait_fixed(2))
def get_fighter_details(fighter_row):
    # Initialise a requests session and updating its headers
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})

    # Define a dictionary to hold fighter details
    fighter_items_dict = {}

    # Findthe URL of the fighter's detail page
    fighter_url = fighter_row.find('a', class_="b-link b-link_style_black")['href']
    
    # Add the URL to the dictionary
    fighter_items_dict['Link'] = fighter_url
    print(f'Scraping fighter details from: {fighter_url}')

    # Make a GET request to the fighter's detail page
    fighter_response = session.get(fighter_url)
    
    # Parse the HTML response
    fighter_soup = BeautifulSoup(fighter_response.content, 'lxml')
    
    # Find all the items of fighter stats
    fighter_items = fighter_soup.find_all('li', class_ = "b-list__box-list-item b-list__box-list-item_type_block")
    
    # Extract the stats text and splitting it into key and value
    fighter_items = [item.text.strip().split('\n', maxsplit=1) for item in fighter_items]

    # Extract the fighter's name, height, reach, stance and date of birth
    name = fighter_soup.find('span', class_="b-content__title-highlight").text.strip()
    height = fighter_items[0][1].strip()
    weight = fighter_items[1][1].strip().replace('.','')
    reach = fighter_items[2][1].strip()
    try:
        stance = fighter_items[3][1].strip()
    except:
        stance = None
    dob = fighter_items[4][1].strip()

    # Add the extracted details to the dictionary
    fighter_items_dict['Name'] = name
    fighter_items_dict['Height'] = height
    fighter_items_dict['Weight'] = weight
    fighter_items_dict['Reach'] = reach
    fighter_items_dict['Stance'] = stance
    fighter_items_dict['DOB'] = dob

    return fighter_items_dict

# Define a dictionary to hold all fighters' details
fighter_dict = {
      'Name':[],
      'Height':[],
      'Weight':[],
      'Reach':[],
      'Stance':[],
      'DOB':[],
      'Link':[]
}

# Use ThreadPoolExecutor to concurrently run get_fighter_rows function on all letters
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    fighter_details_futures = {executor.submit(get_fighter_rows, letter) for letter in letters}
    for future in concurrent.futures.as_completed(fighter_details_futures):
        fighter_details = future.result()
        
        # Add the fighter details to the dictionary
        for fighter_detail in fighter_details:
            for key, value in fighter_detail.items():
                fighter_dict[key].append(value)

# Export the DataFrame to a CSV file
print('Exporting...')
fighter_df = pd.DataFrame(fighter_dict)
fighter_df.to_csv('data/raw/fighter_data.csv')
print('Done!')
print(f'Scraped data from {len(fighter_df)} fighters')