# UFC Fight Outcome Predictor

This project aims to predict the outcome of UFC fights using historical fight data. The data is scraped directly from the official UFC statistics website (ufcstats.com) using a custom-built Python web scraper.

## How It Works

A Python script that scrapes data from the UFC statistics website and saves it in CSV format. The script scrapes detailed statistics about each fight including:

- Fighter names
- Fight outcomes
- Number of knockdowns
- Total strikes attempted and landed
- Takedowns attempted and landed
- Submissions attempted
- Reversals
- Control time
- Significant strikes attempted and landed, split by target (head, body, leg) and position (at distance, in the clinch, on the ground)

As the project progresses, additional Jupyter notebooks will be added that walk through the exploratory data analysis (EDA), modeling, and evaluation stages of the project. 

## Current Files

### Scripts

- `UFC_Scraper.py`: A Python script that scrapes fight data from ufcstats.com.

### Data

- `data/raw/fight_data.csv`: The raw output file from `UFC_Scraper.py`, containing detailed fight statistics.

## Requirements

This project requires Python, along with several Python libraries:

- BeautifulSoup: A library for pulling data out of HTML and XML files.
- Requests: A library for making HTTP requests.
- Pandas: A powerful data manipulation and analysis library.
- Concurrent.futures: A module to execute concurrent computation.

## Future Updates

Keep an eye on this README for updates as this project progresses. Additional Jupyter notebooks and Python scripts will be added to guide you through the exploratory data analysis, modeling, and evaluation stages of this project.


