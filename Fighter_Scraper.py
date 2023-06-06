# importing required libraries
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

# creating a list of all lowercase english letters
letters = [chr(i) for i in range(ord('a'), ord('z')+1)]

# defining user-agent for requests
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"

# initializing a requests session and updating its headers
session = requests.Session()
session.headers.update({"User-Agent": user_agent})

# defining a function to scrape fighter details
@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def get_fighter_rows(letter, session):
    # defining the URL
    main_url = f'http://ufcstats.com/statistics/fighters?char={letter}&page=all'
    
    # making a GET request to the URL
    main_response = session.get(main_url)
    
    # parsing the HTML response
    main_soup = BeautifulSoup(main_response.content, 'lxml')
    
    # finding all the rows of fighter stats
    fighter_rows = main_soup.find_all('tr', class_="b-statistics__table-row")[2:]
    
    # using ThreadPoolExecutor to concurrently run get_fighter_details function on all rows
    with concurrent.futures.ThreadPoolExecutor() as executor:
        fighter_details = list(executor.map(lambda row: get_fighter_details(row, session), fighter_rows))
        
    return fighter_details

# defining a function to scrape fighter details from a row
@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def get_fighter_details(fighter_row, session):
    # defining a dictionary to hold fighter details
    fighter_items_dict = {}

    # finding the URL of the fighter's detail page
    fighter_url = fighter_row.find('a', class_="b-link b-link_style_black")['href']
    
    # adding the URL to the dictionary
    fighter_items_dict['Link'] = fighter_url

    # making a GET request to the fighter's detail page
    fighter_response = session.get(fighter_url)
    
    # parsing the HTML response
    fighter_soup = BeautifulSoup(fighter_response.content)
    
    # finding all the items of fighter stats
    fighter_items = fighter_soup.find_all('li', class_ = "b-list__box-list-item b-list__box-list-item_type_block")
    
    # extracting the stats text and splitting it into key and value
    fighter_items = [item.text.strip().split('\n', maxsplit=1) for item in fighter_items]

    # extracting the fighter's name, height, reach, stance and date of birth
    name = fighter_soup.find('span', class_="b-content__title-highlight").text.strip()
    height = fighter_items[0][1].strip()
    reach = fighter_items[2][1].strip()
    try:
        stance = fighter_items[3][1].strip()
    except:
        stance = None
    dob = fighter_items[4][1].strip()

    # adding the extracted details to the dictionary
    fighter_items_dict['Name'] = name
    fighter_items_dict['Height'] = height
    fighter_items_dict['Reach'] = reach
    fighter_items_dict['Stance'] = stance
    fighter_items_dict['DOB'] = dob

    return fighter_items_dict

# defining a dictionary to hold all fighters' details
fighter_dict = {
      'Name':[],
      'Height':[],
      'Reach':[],
      'Stance':[],
      'DOB':[],
      'Link':[]
}

# using ThreadPoolExecutor to concurrently run get_fighter_rows function on all letters
with concurrent.futures.ThreadPoolExecutor() as executor:
    fighter_details_futures = {executor.submit(get_fighter_rows, letter, session) for letter in letters}
    for future in concurrent.futures.as_completed(fighter_details_futures):
        fighter_details = future.result()
        
        # adding the fighter details to the dictionary
        for fighter_detail in fighter_details:
            for key, value in fighter_detail.items():
                fighter_dict[key].append(value)

# converting the dictionary to a DataFrame
fighter_df = pd.DataFrame(fighter_dict)

# saving the DataFrame to a CSV file
fighter_df.to_csv('data/raw/fighter_data.csv')
