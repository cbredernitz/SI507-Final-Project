# Default Subreddit Top Daily Score Visualization

![Python](https://img.shields.io/badge/python-v3.6-blue.svg)

This project utilizes the Reddit API for pulling the 'top 24 hours' page of each default subreddit.  The data from these requests are then cached and written into a database containing two separate tables.  After a day, the cache is deleted and the database is re-written to contain new data showing the live data.  Final output of the program is a bar chart accumulating each subreddit's total score of the 'top 24 hour' page.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. The requirements.txt file included in the repository holds all packages needed to run this program.  Run the following command in your terminal to pip install requirements.

```
pip install -r requirements.txt

or

pip3 install -r requirements.txt
```

Provided in the repository are two sample files named `reddit_secret_sample.py` and `config_sample.py`.  These files contain the variables you will need to fill in for data extraction through the Reddit API and connecting to the database you specify.

### Getting Credentials from Reddit

To get a client_id and client_secret for Reddit, please go to [reddit.com](https://www.reddit.com/) and create an account. If you already have an account you can skip this step and log into you account.

Once you have an account, go into your preferences and click onto the 'apps' tab.  Scroll to the bottom and click 'create another app...'.  This will create a new box:
![ExampleCreate](https://user-images.githubusercontent.com/20977403/34006157-5a8e252a-e0cb-11e7-8c47-25d6c83ab6a8.png)

[Complete Reddit API Documentation](https://www.reddit.com/dev/api/)

### Creating and Accessing Database



## Running the program
Step 1:


```
Give the example
```

And repeat

```
until finished
```

Example output after running `plot` as shown in step ______:
![ExamplePlot](https://user-images.githubusercontent.com/20977403/34006220-8f7d7dda-e0cb-11e7-8554-d726378acf04.png)

## Running the tests

The SI507F17_finalproject_tests.py file included contains all test cases for this program.  If you are having issues with getting through the installation steps, please run these tests.  It will give you an idea of what where the issue is.

## Built With


## Contributing


## Authors


## Acknowledgments
