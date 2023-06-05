# Imports and Pandas settings
print('Importing packages...')
from bs4 import BeautifulSoup
import concurrent.futures
import copy
import pandas as pd
import requests
pd.options.display.max_columns = None

# Initialise empty dict
print('Initialising...')
ufc_dict= {
    "Date":[],
    "Winner":[],
    "Method":[],
    "Referee":[],
    "N_rounds":[],
    "W_round":[],
    "W_round_time":[],
    "R_fighter":[],
    "B_fighter":[],
    "R_KD":[],
    "B_KD":[],
    "R_total_str":[],
    "B_total_str":[],
    "R_TD":[],
    "B_TD":[],
    "R_sub_att":[],
    "B_sub_att":[],
    "R_rev":[],
    "B_rev":[],
    "R_ctrl":[],
    "B_ctrl":[],
    "R_sig_str":[],
    "B_sig_str":[],
    "R_sig_str_head":[],
    "B_sig_str_head":[],
    "R_sig_str_body":[],
    "B_sig_str_body":[],
    "R_sig_str_leg":[],
    "B_sig_str_leg":[],
    "R_sig_str_dist":[],
    "B_sig_str_dist":[],
    "R_sig_str_clinch":[],
    "B_sig_str_clinch":[],
    "R_sig_str_ground":[],
    "B_sig_str_ground":[],
}

# Set the user agent string for the HTTP headers
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"

# Define the main URL to fetch completed events
main_url = 'http://ufcstats.com/statistics/events/completed?page=all'

# Create a session object to maintain state across multiple requests
session = requests.Session()

# Update the session headers with the user agent string
session.headers.update({"User-Agent": user_agent})

# Send a GET request to the main URL using the session
main_response = session.get(main_url)

# Create a BeautifulSoup object from the main response content using the 'lxml' parser
main_soup = BeautifulSoup(main_response.content, "lxml")

# Find all the event rows on the page, excluding the first two rows (header rows)
events = main_soup.find_all('tr', class_="b-statistics__table-row")[2:]


# Define scraping function
def get_fight_details(fight, date):
    fight_dict = {}

    # Extract the fight URL from the 'data-link' key in the fight dictionary
    fight_url = fight['data-link']
        
    # Send a GET request to the fight URL
    fight_response = requests.get(fight_url, headers={"User-Agent": user_agent})
    
    # Create a BeautifulSoup object from the fight response content
    fight_soup = BeautifulSoup(fight_response.content, "lxml")

    # Check if the fight details are available
    valid_check = fight_soup.find('section', class_="b-fight-details__section js-fight-section")
    
    # If fight details are not available, return an empty dictionary
    if valid_check.text.strip() == "Round-by-round stats not currently available.":
        return fight_dict

    winner = None
    win_lose = fight_soup.find_all('div', class_="b-fight-details__person")
    
    # Find the winner of the fight by parsing the relevant information
    for fighter in win_lose:
        txt = fighter.text.strip().replace('\n', '').split('  ')
        if txt[0] == 'W':
            winner = txt[1]
        elif txt[0] == 'D':
            winner = 'Draw'
    fight_dict['Winner'] = winner

    # Retrieve the method of victory from the fight details
    method = fight_soup.find('i', class_="b-fight-details__text-item_first").find('i', attrs={'style':"font-style: normal"}).text.strip()
    fight_dict['Method'] = method

    # Extract various information items from the fight details
    info_items = fight_soup.find_all('i', class_="b-fight-details__text-item")
    info = [items.text.strip().split('\n', maxsplit=1) for items in info_items]
    
    try:    
        referee = info[3][1].strip()
    except:
        referee = None
    fight_dict['Referee'] = referee

    w_round = info[0][1].strip()
    w_round_time = info[1][1].strip()
    n_rounds = info[2][1].strip()[0]
    fight_dict['W_round'] = w_round
    fight_dict['W_round_time'] = w_round_time
    fight_dict['N_rounds'] = n_rounds

    # Retrieve the names of the red and blue fighters
    r_fighter = fight_soup.find('i', class_="b-fight-details__charts-name b-fight-details__charts-name_pos_left js-chart-name", attrs={'data-color':'red'}).text.strip()
    b_fighter = fight_soup.find('i', class_="b-fight-details__charts-name b-fight-details__charts-name_pos_right js-chart-name", attrs={'data-color':'blue'}).text.strip()
    fight_dict['R_fighter'] = r_fighter
    fight_dict['B_fighter'] = b_fighter


    # Extract total strike statistics from the fight details
    tbl_items = fight_soup.find_all('tbody', class_="b-fight-details__table-body")
    total_str_stats = tbl_items[0]
    sig_str_stats = tbl_items[2]

    total_str_items = total_str_stats.find('tr', class_="b-fight-details__table-row").text.split('\n')
    total_str_items = [item.strip() for item in total_str_items if item.strip()]

    r_kd = total_str_items[2]
    b_kd = total_str_items[3]
    fight_dict['R_KD'] = r_kd
    fight_dict['B_KD'] = b_kd

    r_total_str = total_str_items[8]
    b_total_str = total_str_items[9]
    fight_dict['R_total_str'] = r_total_str
    fight_dict['B_total_str'] = b_total_str

    r_td = total_str_items[10]
    b_td = total_str_items[11]
    fight_dict['R_TD'] = r_td
    fight_dict['B_TD'] = b_td

    r_sub_att = total_str_items[14]
    b_sub_att = total_str_items[15]
    fight_dict['R_sub_att'] = r_sub_att
    fight_dict['B_sub_att'] = b_sub_att

    r_rev = total_str_items[16]
    b_rev = total_str_items[17]
    fight_dict['R_rev'] = r_rev
    fight_dict['B_rev'] = b_rev

    r_ctrl = total_str_items[18]
    b_ctrl = total_str_items[19]
    fight_dict['R_ctrl'] = r_ctrl
    fight_dict['B_ctrl'] = b_ctrl

    # Extract significant strike statistics from the fight details
    sig_str_items = sig_str_stats.find('tr', class_="b-fight-details__table-row").text.split('\n')
    sig_str_items = [item.strip() for item in sig_str_items if item.strip()]

    r_sig_str = sig_str_items[2]
    b_sig_str = sig_str_items[3]
    fight_dict['R_sig_str'] = r_sig_str
    fight_dict['B_sig_str'] = b_sig_str

    r_sig_str_head = sig_str_items[6]
    b_sig_str_head = sig_str_items[7]
    fight_dict['R_sig_str_head'] = r_sig_str_head
    fight_dict['B_sig_str_head'] = b_sig_str_head

    r_sig_str_body = sig_str_items[8]
    b_sig_str_body = sig_str_items[9]
    fight_dict['R_sig_str_body'] = r_sig_str_body
    fight_dict['B_sig_str_body'] = b_sig_str_body

    r_sig_str_leg = sig_str_items[10]
    b_sig_str_leg = sig_str_items[11]
    fight_dict['R_sig_str_leg'] = r_sig_str_leg
    fight_dict['B_sig_str_leg'] = b_sig_str_leg

    r_sig_str_dist = sig_str_items[12]
    b_sig_str_dist = sig_str_items[13]
    fight_dict['R_sig_str_dist'] = r_sig_str_dist
    fight_dict['B_sig_str_dist'] = b_sig_str_dist

    r_sig_str_clinch = sig_str_items[14]
    b_sig_str_clinch = sig_str_items[15]
    fight_dict['R_sig_str_clinch'] = r_sig_str_clinch
    fight_dict['B_sig_str_clinch'] = b_sig_str_clinch

    r_sig_str_ground = sig_str_items[16]
    b_sig_str_ground = sig_str_items[17]
    fight_dict['R_sig_str_ground'] = r_sig_str_ground
    fight_dict['B_sig_str_ground'] = b_sig_str_ground
    
    # Add the fight date to the fight dictionary
    fight_dict["Date"] = date

    # Return the populated fight dictionary
    return fight_dict

# Iterate over each event in the events list
print('Scraping...')
for event in events:
    # Extract the date of the event
    date = event.find('span', class_="b-statistics__date").text.strip()
    
    # Extract the event URL
    event_url = event.find('a', class_="b-link b-link_style_black")['href']

    # Print updates to terminal
    print(f'Now scraping fights from: {event_url}')
    
    # Send a GET request to the event URL
    event_response = session.get(event_url)
    
    # Create a BeautifulSoup object from the event response content
    event_soup = BeautifulSoup(event_response.content, "lxml")
    
    # Find all the fights in the event
    fights = event_soup.find_all('tr', class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
    
    # Use ThreadPoolExecutor for concurrent execution of get_fight_details function on each fight
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the get_fight_details function to each fight in the fights list and store the results in fight_details
        fight_details = list(executor.map(lambda fight: get_fight_details(fight, date), fights))
    
    # Iterate over each fight detail in the fight_details list
    for fight_detail in fight_details:
        # Iterate over each key-value pair in the fight_detail dictionary
        for key, value in fight_detail.items():
            # Append the value to the corresponding key in the ufc_dict
            ufc_dict[key].append(value)

# Export data
ufc_df = pd.DataFrame(ufc_dict)
ufc_df.to_csv('data/raw/fight_data.csv')

print('Done!')