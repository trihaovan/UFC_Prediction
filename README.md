# UFC Fight Outcome Predictor

This project aims to predict the outcome of UFC fights using historical fight data. The data is scraped directly from the official UFC statistics website (ufcstats.com) using custom-built Python web scrapers.

## How It Works

The Python scripts in this project scrape data from the UFC statistics website and save it in CSV format. The scripts collect detailed statistics about each fight and each fighter, which include:

### Fight Data

- Fighter names
- Fight outcomes
- Number of knockdowns
- Total strikes attempted and landed
- Takedowns attempted and landed
- Submissions attempted
- Reversals
- Control time
- Significant strikes attempted and landed, split by target (head, body, leg) and position (at distance, in the clinch, on the ground)

### Fighter Data

- Fighter name
- Fighter's height
- Fighter's reach
- Fighter's stance
- Fighter's date of birth
- Link to fighter's detail page

As the project progresses, additional Jupyter notebooks will be added that walk through the exploratory data analysis (EDA), modelling, and evaluation stages of the project.

## Current Files

### Notebooks

- `Cleaning_And_Processing.ipynb`: A notebook going through the joining of the fight and fighter datasets, cleaning of the data, some EDA, and some preprocessing of the data.
- `Feature_Extraction_And_Engineering.ipynb` (Work in progress): Covers the creation of new features to be considered by the machine learning models.

### Scripts

- `UFC_Scraper.py`: A Python script that scrapes fight data from ufcstats.com.
- `Fighter_Scraper.py`: A Python script that scrapes individual fighter data from ufcstats.com.

### Data

- `data/raw/fight_data.csv`: The raw output file from `UFC_Scraper.py`, containing detailed fight statistics.
- `data/raw/fighter_data.csv`: The raw output file from `Fighter_Scraper.py`, containing detailed individual fighter statistics.

- `data/outputs/cleaned_and_processed.csv`: The output from 'Cleaning_And_Processing.ipynb', containing a cleaned and processed version of the joined fight_data and fighter_data datasets.

## Requirements

This project requires Python, along with several Python libraries:

- BeautifulSoup: A library for pulling data out of HTML and XML files.
- Requests: A library for making HTTP requests.
- Pandas: A data manipulation and analysis library.
- Concurrent.futures: A module to execute concurrent computation.
- Tenacity: A library for making robust functions with built-in retry and wait mechanisms.
- Seaborn: A data visualization library based on Matplotlib. 
- Matplotlib: A plotting library for the Python programming language and its numerical mathematics extension NumPy.

## Future Updates

Keep an eye on this README for updates as this project progresses. Additional Jupyter notebooks and Python scripts will be added to guide you through the exploratory data analysis, modelling, and evaluation stages of this project.
