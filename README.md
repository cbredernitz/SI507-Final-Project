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

You will need to select `script` as shown and fill in a name and description.

After that is complete you will have a client_id and client_secret from your app.  Please remember to input these values as strings in the sample file `reddit_secret_sample.py`.  Again, you will need to rename this file afterwards to `reddit_secret.py` as stated above.

On this same file, you will need to unput you Reddit account username and password in the sample file provided.  This is required to make a successful request to the Reddit API.

For complete reddit API documentation, please follow the links below:

[Reddit API Quick Start Steps](https://github.com/reddit/reddit/wiki/OAuth2)
    
[Complete Reddit API Request Types](https://www.reddit.com/dev/api/)

### Creating and Accessing Database

Provided for you is a `config_sample.py` file.  This contains all the required variable inputs to the program.  At the end of these steps, you will need to rename the file `config.py` for correct import.

This program requires database connection using PostgreSQL. For documentation on installing PostgreSQL follow the links below:  

**For Mac**:

Get homebrew:
Go to this link: https://brew.sh/
Copy the one line of code that they have on that page, which is this:

`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Open your Terminal and paste that entire line in. It will run for a while.
It may prompt you for your computer password (or it may not).

After homebrew is installed run:

`brew install postgres`

To start the connection to your database run:

`pg_ctl -D /usr/local/var/postgres start`

After that is complete, you are now connected to your Postgres database.  For simpler visualization, I use TeamSQL which can be downloaded [here](https://teamsql.io/)

**For Windows**:

Follow the documentation provided at the link below:    (https://labkey.org/Documentation/wiki-page.view?name=installPostgreSQLWindows)

 After the above is done, you are now ready to create a database to store all the data the program gathers. Run the following to create a database.  You can name the database whatever you'd like, however just be sure to remember what that is.

 `createdb your_database_name`

 Once you have a database created, you can now being to fill in the provided 'config_sample.py' file. Replace the `db_name` with the name of your database, `db_user` with the user name associated to your database upon installation, and `db_password` if the database you created has a password, if not then leave as an empty string. Once again, you will need to rename the file `config.py` for correct import.

## Running the program

Once all the above has been completed, you are now ready to run the program.  The first step is to check the database connection by running:

```
python3 SI507F17_finalproject.py
```

You should see a readout in your terminal of 'Success connecting to the database'

____________________________________________

To set up the structure of the database, run the following:

```
python3 SI507F17_finalproject.py setup  
```

This `setup` command creates the database tables for storing the data that we pull later on by running the `setup_database()` function.

If you open up TeamSQL and look at the database, it should contain two tables.  One for Subreddits and the other for Postings.

____________________________________________

To get the data from each subreddit written into the database, run the following:

```
python3 SI507F17_finalproject.py write
```

This `write` command runs the `start_reddit_session(), load_cache(), and run_search_on_default()` functions.  The `start_reddit_session()` does, as you would guess, start the reddit request session saving a token in the 'creds.json' file.  The `load_cache()` functions loads the cache into the CACHE_DICTION variable, but if the cache file is older than a day, it deletes the file and makes a new cache_file for the day.  The `run_search_on_default()` function finally pulls all this together and iterates over a static list containing default subreddits that each account is automatically subscribed to when they create a reddit account.  It then checks to see if it is making a new request or pulling from the database for each subreddit and inputing the data into the database.

When the program is pulling from the database, you will see the following in your terminal.

![Pulling](https://user-images.githubusercontent.com/20977403/34009111-a462a054-e0d5-11e7-86dc-5d4806a7f56e.png)

Otherwise, your output will look like this:

![Fetching](https://user-images.githubusercontent.com/20977403/34009123-b31e03fe-e0d5-11e7-892a-c35d254f5f0f.png)

When you have data in your database, you can now run the plotting function as shown below:

The database should look similar to this:

![Postings](https://user-images.githubusercontent.com/20977403/34019080-222ba45c-e0fb-11e7-8164-53754e8c79bc.png)

![Subreddits](https://user-images.githubusercontent.com/20977403/34019069-0e230ef0-e0fb-11e7-832a-f3a841c6e4e4.png)

____________________________________________

To create a plot, run the following command in your terminal

```
python3 SI507F17_finalproject.py plot
```

The `plot` command runs the `plot()` function.  Connection and storage of data into the database is required for this function to work.  The function runs an SQL query collecting the sum of each post's score, inner joining the tables on their foreign key (ID and subreddit_id), and grouping the sum by the Subreddit's name.  After running a .fetchall(), we are left with a list containing the sum of scores and the subreddit name associated.  After unpacking the list, we then use Plotly to create a visual of the data collected.

The bar chart should open automatically in Google Chrome, however, if that doesn't appear to be the case, go into the directory and open the file `subreddit_analysis.html` in your webbrowser.

Example output after running `plot`:

![ExamplePlot](https://user-images.githubusercontent.com/20977403/34006220-8f7d7dda-e0cb-11e7-8554-d726378acf04.png)

____________________________________________

Running the program each time will require a `write` command followed by a `plot` command.  Write to get all data into the database, and plot to plot the data.

## Running the tests

The SI507F17_finalproject_tests.py file included contains all test cases for this program.  If you are having issues with getting through the installation steps, please run these tests.  It will give you an idea of what where the issue is.

Provided for you is a sample post json file `sample_reddit_post.json`.  This needs to be in your folder for some of the test functions.

## Built With

[Plotly](https://plot.ly/) - Data visualization

[Requests](http://docs.python-requests.org/en/master/) - Sending requests to Reddit API

[Psycopg2](http://initd.org/psycopg/) - PostgreSQL adapter for python

[Reddit API](https://www.reddit.com/dev/api/) - Where the data came from

## Contributing

* Caching help from Project 2
* Help with SQL insert executes from section week 10 `itunes_database.py`
* Special thanks to @anandpdoshi and @aerenchyma for the help with this project and for a great semester!

## Author

* **Christopher Bredernitz**

## Acknowledgments

This program heavily relies on the database.  If connection is lost then the program will not run.

If, for some reason, there is an issue with a subreddit returning a ''Check the subreddit name' in the terminal, change the capitalization in the `default_subreddits` list under the run_search_on_default() function.  I noticed that some random calls would throw this error randomly.  Originally, I though that using a .lower() in the for loop would work, but sometimes that also threw the error.  

To add more or take away subreddits in this visualization, just add/subtract them from the `default_subreddits` list in the `run_search_on_subreddits()` function.
