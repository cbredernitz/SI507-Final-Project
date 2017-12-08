import json
import webbrowser
import sys
import psycopg2
import psycopg2.extras
import requests
import requests.auth
# from flask import Flask, render_template
from reddit_secret import client_id, client_secret, username, password
import csv
import sys
import os, datetime

CACHE_FNAME = 'cache_contents.json'
CACHE_CREDS = 'creds.json'

CLIENT_ID = client_id
CLIENT_SECRET = client_secret
PASSWORD = password
USERNAME = username

REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'
AUTHORIZATION_URL = 'https://ssl.reddit.com/api/v1/authorize'
TOKEN_URL = 'https://www.reddit.com/api/v1/access_token'
SCOPE_STRING = ['identity', 'edit', 'flair', 'history', 'mysubreddits', 'privatemessages', 'read', 'report', 'save', 'submit', 'subscribe', 'vote', 'wikiedit', 'wikiread']
DURATION =  'temporary'

##### CACHING FUNCTIONS #####

try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

#  Gets the saved token from the cache
def get_saved_token():
    with open(CACHE_CREDS, 'r') as creds:
        token_json = creds.read()
        token_dict = json.loads(token_json)
        return token_dict['access_token']

#  Saves token from authentication
def save_token(token_dict):
    with open(CACHE_CREDS, 'w') as creds:
        token_json = json.dumps(token_dict)
        creds.write(token_json)

def check_token_time():
    t = os.path.getctime('creds.json')
    created_time = datetime.datetime.fromtimestamp(t)
    now = datetime.datetime.now()

    # subtracting two datetime objects gives you a timedelta object
    delta = now - created_time
    delta_in_seconds = delta.seconds

    # now that we have days as integers, we can just use comparison
    # and decide if the token has expired or not
    if delta_in_seconds <= 3600:
        return False
    else:
        return True

##### Setting up the database connection #####
# try:
#     conn = psycopg2.connect("dbname = 'brederni_507_final_project' user = 'Chris'")
#     print("Success connecting to the database")
#
# except:
#     print("Unable to connect to the database")
#     sys.exit(1)
#
# cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

##### Seting up the database #####
def setup_database():
    ##### ADJUST TO ID AND SUBREDDIT NAME #####
    cur.execute("""CREATE TABLE IF NOT EXISTS States(
                ID SERIAL PRIMARY KEY NOT NULL,
                Name VARCHAR(128) UNIQUE NOT NULL
                )""")

    ##### ADJUST TO POSTS INFORMATION #####
    cur.execute("""CREATE TABLE IF NOT EXISTS Sites(
                ID SERIAL NOT NULL,
                Name VARCHAR(128) UNIQUE NOT NULL,
                Type VARCHAR(128),
                State_ID INTEGER REFERENCES States(ID),
                Location VARCHAR(225),
                Description TEXT)""")

    conn.commit()

#  Authenticates and creates an instance of authentication to call to
def start_reddit_session():
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
    headers = {"User-Agent": "test script by /u/" + username}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    cred = json.loads(response.text)

    save_token(cred)

def make_request(subreddit):
    try:
        token = get_saved_token()
        if check_token_time():
            start_reddit_session()
        else:
            pass
    except FileNotFoundError:
        token = None

    if not token:
        start_reddit_session()

    else:
        headers = {"Authorization": "bearer "+ token, "User-Agent": "test script by /u/Inept_P_Hacker"}
        params = {}
        response2 = requests.get("https://oauth.reddit.com/r/" + subreddit, headers=headers, params = {'sort': 'top', 't': 'day'})
        return json.loads(response2.text)


class Post(object):
    """Organizing data of each reddit post"""
    def __init__(self, post_dict):
        self.title = post_dict['data']['title']
        self.time_created = post_dict['data']['created_utc']
        self.permalink = post_dict['data']['permalink']
        self.gilded = post_dict['data']['gilded']
        self.domain = post_dict['data']['domain']
        self.upvotes = post_dict['data']['ups']
        self.score = post_dict['data']['score']
        if post_dict['kind'] == 't1':
            self.kind = 'Comment'
        elif post_dict['kind'] == 't2':
            self.kind = 'Account'
        elif post_dict['kind'] == 't3':
            self.kind = 'Link'
        elif post_dict['kind'] == 't4':
            self.kind = 'Message'
        elif post_dict['kind'] == 't5':
            self.kind = 'Subreddit'
        elif post_dict['kind'] == 't6':
            self.kind = 'Award'

default_subreddits = ['announcements', 'Art', 'AskReddit', 'askscience', 'aww',
                    'blog', 'books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries',
                    'EarthPorn', 'explainlikeimfive', 'food', 'funny', 'Futurology',
                    'gadgets', 'gaming', 'GetMotivated', 'gifs', 'history', 'IAmA',
                    'InternetIsBeautiful', 'Jokes', 'LifeProTips', 'listentothis',
                    'mildlyinteresting', 'movies', 'Music', 'news', 'nosleep',
                    'nottheonion', 'OldSchoolCool', 'personalfinance', 'philosophy',
                    'photoshopbattles', 'pics', 'science', 'Showerthoughts',
                    'space', 'sports', 'television', 'tifu', 'todayilearned',
                    'UpliftingNews', 'videos', 'worldnews']

# default_responses = []
# for x in default_subreddits:
#     default_responses.append(make_request(x))
#
post_inst = []
example1 = make_request('pics')
# print(example1)
for post in example1['data']['children']:
    post_inst.append(Post(post))



#  Testing csv output
# with open('testing.csv', 'w', newline = '') as test:
#     test_writer = csv.writer(test, delimiter = ',')
#     test_writer.writerow(['title',
#                         'permalink',
#                         'domain',
#                         'score',
#                         'kind'])
#     for info in post_inst:
#         test_writer.writerow([info.title,
#                             info.permalink,
#                             info.domain,
#                             info.score,
#                             info.upvotes,
#                             info.downvotes,
#                             info.kind])
# test.close()

# ____________________________________________
#   Things to do:
    #  Add function to add subreddits to the list if the user so chooses.
    #  Add function to remove a subreddit from the list of global subreddits

    #  Write database that has timestamp. This would be the best idea since we want to drop tables every day so we can write current data into the database.
        # Talk with Ethan about this one and see what he came up with about storing stock data.

    #  Adjust milestones on Github to reflect what I am doing now.
    #  Add function to plot and sort all the data into tables.
        #  Maybe look into having this be a flask application to show the data.

    #  The overall goal of this assignment is to look at the most engaged subreddit of the day using the 'top' of that subreddit for the past 24 hours when looking at the default subreddits.

    #  Have an if __name__ == '__main__': have take in system arguments so that it can the user can setup the database, add, subtract, and finially plot.
