# README for BitmexFundingRateFetcher.py

## Overview
BitmexFundingRateFetcher.py is a Python script designed to fetch and record the funding rate data for a specified asset from the BitMEX cryptocurrency trading platform. The script allows users to set a specific date range for the data retrieval.

## Dependencies
To run this script, you will need to have the following Python libraries installed:

- `requests`: For making API requests to the BitMEX API.
- `csv`: To write the fetched data into a CSV file.
- `time`: For handling time-related functions and API request throttling.
- `datetime`: To manage and format dates and times.
- `xlsxwriter`: To create and manage Excel files, if the user wishes to export data in Excel format.

I recommend using a conda environment to manage your Python libraries. 

## Usage

Before running the script, configure the following parameters in the script:

- `asset`: The trading pair for which you want to fetch the funding rate (e.g., "ETHUSD").
-  `start_date`: The start date for the data retrieval, in the format "YYYY-MM-DD HH:MM" (e.g., "2022-01-01 00:00").
- `end_date`: The end date for the data retrieval, in the format "YYYY-MM-DD HH:MM" (e.g., "2022-01-01 00:00").

Run the script using Python: 
```bash
python BitmexFundingRateFetcher.py
```
