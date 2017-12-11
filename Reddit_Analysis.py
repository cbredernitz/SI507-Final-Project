import json
import sys
import psycopg2
import psycopg2.extras
import requests
import requests.auth
from reddit_secret import client_id, client_secret, username, password
import sys
import os, datetime
import plotly

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

##### CACHING FUNCTIONS #####

try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}

##### Caching function from Project 2 #####

def load_cache():
    global CACHE_DICTION
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

def save_cache():
    full_text = json.dumps(CACHE_DICTION)
    cache_file_ref = open(CACHE_FNAME,"w")
    cache_file_ref.write(full_text)
    cache_file_ref.close()

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

    # now that we have seconds as integers, we can just use comparison
    # and decide if the token has expired or not
    if delta_in_seconds <= 3600:
        return False
    else:
        return True

##### Setting up the database connection #####
try:
    conn = psycopg2.connect("dbname = '507_Final_Project' user = 'Chris'")
    print("Success connecting to the database")

except:
    print("Unable to connect to the database")
    sys.exit(1)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

##### Seting up the database #####
def setup_database():
    cur.execute("""CREATE TABLE IF NOT EXISTS Subreddits(
                ID SERIAL PRIMARY KEY NOT NULL,
                Name VARCHAR(128) UNIQUE NOT NULL
                )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Postings(
                ID SERIAL NOT NULL,
                Title VARCHAR(128) NOT NULL,
                Score INTEGER NOT NULL,
                Created_Time VARCHAR(128) NOT NULL,
                Subreddit_ID INTEGER REFERENCES Subreddits(ID),
                Guilded INTEGER NOT NULL,
                Permalink VARCHAR(128),
                Kind TEXT)""")

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
    # try:
    token = get_saved_token()

    if check_token_time():
        start_reddit_session()

    # except FileNotFoundError:
    #     token = None
    #
    # if not token:
    #     start_reddit_session()

    else:
        headers = {"Authorization": "bearer "+ token, "User-Agent": "test script by /u/Inept_P_Hacker"}
        params = {}
        response2 = requests.get("https://oauth.reddit.com/r/" + subreddit, headers=headers, params = {'sort': 'top', 't': 'day'})
        return json.loads(response2.text)


class Post(object):
    """Organizing data of each reddit post"""
    def __init__(self, post_dict):
        self.title = post_dict['data']['title']
        self.subreddit = post_dict['data']['subreddit']
        self.time_created = post_dict['data']['created_utc']
        self.permalink = post_dict['data']['permalink']
        self.gilded = post_dict['data']['gilded']
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

    def get_subreddit():
        return {'subreddit': self.subreddit}

    def get_posting_dict():
        return {
            'title': self.title,
            'time_created': self.time_created,
            'permalink': self.permalink,
            'gilded': self.gilded,
            'score': self.score,
            'kind': self.kind
            }

    def __contains__():
        pass
    def __repr__():
        pass

default_subreddits = ['Art', 'AskReddit', 'askscience', 'aww',
                    'blog', 'books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries',
                    'EarthPorn', 'explainlikeimfive', 'food', 'funny', 'Futurology',
                    'gadgets', 'gaming', 'GetMotivated', 'gifs', 'history', 'IAmA',
                    'InternetIsBeautiful', 'Jokes', 'LifeProTips', 'listentothis',
                    'mildlyinteresting', 'movies', 'Music', 'news', 'nosleep',
                    'nottheonion', 'OldSchoolCool', 'personalfinance', 'philosophy',
                    'photoshopbattles', 'pics', 'science', 'Showerthoughts',
                    'space', 'sports', 'television', 'tifu', 'todayilearned',
                    'UpliftingNews', 'videos', 'worldnews']

#  adds a subreddit to the list to be analysed
def addSubreddit(subreddit):
    return default_subreddits.append(subreddit)

#  removes a subreddit from the list being analysed
def subtractSubreddit(subreddit):
    if subreddit not in default_subreddits:
        return False
    else:
        return default_subreddits.remove(subreddit)

def cache():
    try:
        t = os.path.getctime('cache_contents.json')
        created_time = datetime.datetime.fromtimestamp(t)
        now = datetime.datetime.now()

        # subtracting two datetime objects gives you a timedelta object
        delta = now - created_time
        delta_in_days = delta.days

        # now that we have days as integers, we can just use comparison
        # and decide if the token has expired or not
        if delta_in_days <= 1:
            print('-- Pulling from cache --')
            load_cache()
            results = CACHE_DICTION
    except:
        print("-- Fetching new content for the day's activity --")
        for sub in default_subreddits:
            if sub not in CACHE_DICTION:
                response = make_request(sub)
                CACHE_DICTION[sub] = response
                save_cache()
        results = CACHE_DICTION
    ls = []
    for sub_dict in CACHE_DICTION:
        value = CACHE_DICTION[sub_dict]
        ls.append(Post(value['data']['children']))
    print(ls)

cache()
# def write_database():
#     results = cache()
#     for data in results[]

# default_responses = []
# for x in default_subreddits:
#     default_responses.append(make_request(x))

# post_inst = []
# example1 = make_request('pics')
# # print(example1)
# for post in example1['data']['children']:
#     post_inst.append(Post(post))

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
#                             info.kind])
# test.close()

# ____________________________________________

if __name__ == "__main__":
    command = None
    subreddit = None
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if len(sys.argv) > 2:
            subreddit = sys.argv[2]

    if command == 'setup':
        setup_database()
        print('-- Setting up database --')

    elif command == 'token':
        start_reddit_session()

    elif command == 'write':
        load_cache()
        print('-- Writting database --')
        write_database()

    elif command == 'add':
        print('-- Adding ' + subreddit + ' to Analysis --')
        addSubreddit(subreddit)

    elif command == 'remove':
        if not subtractSubreddit(subreddit):
            print(subreddit + " doesn't appear to be in the analysis")
        else:
            print('-- Removing ' + subreddit + ' from Analysis --')
            subtractSubreddit(subreddit)

    # elif command == 'plot':
        # run plotting function
