# Imports
print('Importing packages...')
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

print('Initialising...')
fights_dict= {
    "Date":[],
    "Winner":[],
    "Method":[],
    "Referee":[],
    "Format":[],
    "Weight_class":[],
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
    "Fight_link":[],
    "R_link":[],
    "B_link":[]
}

# Set the user agent string for the HTTP headers
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
fighter_df = pd.read_csv('data/raw/fighter_data.csv')
fighter_urls = fighter_df['Link']

@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
def get_fight_rows(fighter_url):

    # Create a session object to maintain state across multiple requests
    session = requests.Session()

    # Update the session headers with the user agent string
    session.headers.update({"User-Agent": user_agent})

    # Send a GET request to the main URL using the session
    fighter_response = session.get(fighter_url)

    # Create a BeautifulSoup object from the main response content using the 'lxml' parser
    fighter_soup = BeautifulSoup(fighter_response.content, "lxml")

    # Find all the fight rows on the page, excluding the first two rows (header rows)
    fight_rows = fighter_soup.find_all('tr', class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        fight_details = list(executor.map(lambda row: get_fight_details(row), fight_rows))
        
    return fight_details

@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
# Initialise a requests session and updating its headers
def get_fight_details(fight_row):

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    
    fight_dict = {}

    # Add the fight date to the fight dictionary
    date = fight_row.find_all('p', class_="b-fight-details__table-text")[12].text.strip()
    fight_dict["Date"] = date

    # Extract the fight URL from the 'data-link' key in the fight dictionary
    fight_url = fight_row['data-link']
    print(f'Scraping fight data from: \n{fight_url}')
        
    # Send a GET request to the fight URL
    fight_response = requests.get(fight_url, headers={"User-Agent": user_agent})
    
    # Create a BeautifulSoup object from the fight response content
    fight_soup = BeautifulSoup(fight_response.content, "lxml")

    # Check if the fight details are available
    valid_check = fight_soup.find('section', class_="b-fight-details__section js-fight-section")
    
    # If specific fight stats are not available, scrape what is available
    if valid_check.text.strip() == "Round-by-round stats not currently available.":
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
        format = info[2][1].strip()
        fight_dict['W_round'] = w_round
        fight_dict['W_round_time'] = w_round_time
        fight_dict['Format'] = format

        # Extract weight class:
        weight_class = fight_soup.find('i', class_='b-fight-details__fight-title').text.strip()
        fight_dict['Weight_class'] = weight_class

        # Retrieve the names of the red and blue fighters
        fighters = fight_soup.find_all('a', class_="b-link b-fight-details__person-link")
        r_fighter = fighters[0].text
        b_fighter = fighters[1].text
        fight_dict['R_fighter'] = r_fighter
        fight_dict['B_fighter'] = b_fighter
        r_link = fighters[0]['href']
        b_link = fighters[1]['href']
        fight_dict['R_link'] = r_link
        fight_dict['B_link'] = b_link

        fight_dict['R_KD'] = None
        fight_dict['B_KD'] = None
        fight_dict['R_total_str'] = None
        fight_dict['B_total_str'] = None
        fight_dict['R_TD'] = None
        fight_dict['B_TD'] = None
        fight_dict['R_sub_att'] = None
        fight_dict['B_sub_att'] = None
        fight_dict['R_rev'] = None
        fight_dict['B_rev'] = None
        fight_dict['R_ctrl'] = None
        fight_dict['B_ctrl'] = None
        fight_dict['R_sig_str'] = None
        fight_dict['B_sig_str'] = None
        fight_dict['R_sig_str_head'] = None
        fight_dict['B_sig_str_head'] = None
        fight_dict['R_sig_str_body'] = None
        fight_dict['B_sig_str_body'] = None
        fight_dict['R_sig_str_leg'] = None
        fight_dict['B_sig_str_leg'] = None
        fight_dict['R_sig_str_dist'] = None
        fight_dict['B_sig_str_dist'] = None
        fight_dict['R_sig_str_clinch'] = None
        fight_dict['B_sig_str_clinch'] = None
        fight_dict['R_sig_str_ground'] = None
        fight_dict['B_sig_str_ground'] = None
    
        # Add the link to the fight data to the fight dictionary
        fight_dict['Fight_link'] = fight_url

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
    format = info[2][1].strip()
    fight_dict['W_round'] = w_round
    fight_dict['W_round_time'] = w_round_time
    fight_dict['Format'] = format

    # Extract weight class:
    weight_class = fight_soup.find('i', class_='b-fight-details__fight-title').text.strip()
    fight_dict['Weight_class'] = weight_class

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
    
    
    # Add the link to the fight data to the fight dictionary
    fight_dict['Fight_link'] = fight_url

    fighter_links = fight_soup.find_all('a', class_ = "b-link b-fight-details__person-link")
    r_link = fighter_links[0]['href']
    b_link = fighter_links[1]['href']
    fight_dict["R_link"] = r_link
    fight_dict["B_link"] = b_link

    # Return the populated fight dictionary
    return fight_dict

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    fight_details_futures = {executor.submit(get_fight_rows, fighter_url) for fighter_url in fighter_urls}
    for future in concurrent.futures.as_completed(fight_details_futures):
        fight_details = future.result()
        
        # Add the fighter details to the dictionary
        for fight_detail in fight_details:
            for key, value in fight_detail.items():
                fights_dict[key].append(value)

# Export data
print('Exporting...')
fights_df = pd.DataFrame(fights_dict)
fights_df.to_csv('data/raw/fight_data.csv')

print('Done!')
print(f'Scraped data from {len(fights_df)} fights')