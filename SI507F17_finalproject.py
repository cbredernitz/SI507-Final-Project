import json
import psycopg2
import psycopg2.extras
import requests
import requests.auth
from reddit_secret import client_id, client_secret, username, password
import sys
import os, datetime
import plotly as py
import plotly.graph_objs as go
import webbrowser

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

CACHE_DICTION = {}

##### Setting up the database connection #####
try:
    conn = psycopg2.connect("dbname = '507_Final_Project_2' user = 'Chris'")
    print("Success connecting to the database")

except:
    print("Unable to connect to the database")
    sys.exit(1)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

##### Seting up the database #####
def setup_database():
    cur.execute("""CREATE TABLE IF NOT EXISTS Subreddits(
                ID SERIAL PRIMARY KEY,
                Name VARCHAR(128) UNIQUE NOT NULL
                )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS Postings(
                ID SERIAL PRIMARY KEY,
                Title VARCHAR(255) NOT NULL,
                Score INTEGER NOT NULL,
                Created_Time VARCHAR(128) NOT NULL,
                Subreddit_ID INTEGER REFERENCES Subreddits(ID),
                Gilded INTEGER NOT NULL,
                Permalink TEXT,
                Kind TEXT)""")

    conn.commit()

##### Caching function from Project 2 #####
def check_cache_time():
    t = os.path.getctime('cache_contents.json')
    created_time = datetime.datetime.fromtimestamp(t)
    now = datetime.datetime.now()

    # subtracting two datetime objects gives you a timedelta object
    delta = now - created_time
    delta_in_days = delta.days

    # now that we have days as integers, we can just use comparison
    # and decide if the token has expired or not
    if delta_in_days <= 1:
        return False
    else:
        return True

def load_cache():
    global CACHE_DICTION
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
        cur.execute("DELETE FROM Postings")
        conn.commit()
        if check_cache_time():
            CACHE_DICTION = {}
            os.remove('cache_contents.json')
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

#  Authenticates and creates an instance of authentication to call to
def start_reddit_session():
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
    headers = {"User-Agent": "test script by /u/" + username}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    cred = json.loads(response.text)
    save_token(cred)


def make_request(subreddit):
    token = get_saved_token()

    if check_token_time():
        start_reddit_session()

    else:
        headers = {"Authorization": "bearer "+ token, "User-Agent": "test script by /u/Inept_P_Hacker"}
        params = {}
        response2 = requests.get("https://oauth.reddit.com/r/" + subreddit, headers=headers, params = {'sort': 'top', 't': 'day'})
        return json.loads(response2.text)


class Post(object):
    """Organizing data of each reddit post"""
    def __init__(self, post_dict):
        self.title = post_dict['data']['title'][:255]
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

    def get_subreddit(self):
        return {'subreddit': self.subreddit}

    def __contains__(self):
        pass

    def __repr__(self):
        pass


def get_cache_or_live_data(subreddit):
    if subreddit not in CACHE_DICTION:
        print("-- Fetching new content for the day's activity for " + subreddit + " --")
        response = make_request(subreddit)
        CACHE_DICTION[subreddit] = response
        save_cache()
    else:
        print('-- Pulling data on '+ subreddit +' from cache --')
        results = CACHE_DICTION
    return CACHE_DICTION[subreddit]


def searching(subreddit):
    response = get_cache_or_live_data(subreddit)
    for post_dict in response['data']['children']:
        post_obj = Post(post_dict)
        cur.execute("""INSERT INTO
            Subreddits(Name)VALUES(%(subreddit)s)on CONFLICT DO NOTHING RETURNING ID""", post_obj.get_subreddit())

        conn.commit()

        try:
            subreddit_id = cur.fetchone()
            subreddit_id = subreddit_id['id']

        except:
            cur.execute("SELECT Subreddits.ID FROM Subreddits WHERE Subreddits.Name = %s", (post_obj.subreddit,))
            subreddit_id = cur.fetchone()
            subreddit_id = subreddit_id['id']

        cur.execute("""INSERT INTO Postings(subreddit_id, title, score, created_time, gilded, permalink, kind) VALUES(%s, %s, %s, %s, %s, %s, %s) on conflict do nothing""", (subreddit_id, post_obj.title, post_obj.score, post_obj.time_created, post_obj.gilded, post_obj.permalink, post_obj.kind))

        conn.commit()

def run_search_on_default():
    default_subreddits = ['art', 'AskReddit', 'askscience', 'aww',
                    'blog', 'books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries',
                    'EarthPorn', 'explainlikeimfive', 'food', 'funny', 'Futurology',
                    'gadgets', 'gaming', 'GetMotivated', 'gifs', 'history', 'IAmA',
                    'InternetIsBeautiful', 'Jokes', 'LifeProTips', 'listentothis',
                    'mildlyinteresting', 'movies', 'Music', 'news', 'nosleep',
                    'nottheonion', 'OldSchoolCool', 'personalfinance', 'philosophy',
                    'photoshopbattles', 'pics', 'science', 'Showerthoughts',
                    'space', 'sports', 'television', 'tifu', 'todayilearned',
                    'UpliftingNews', 'videos', 'worldnews']
    for sub in default_subreddits:
        searching(sub.lower())

def plot():
    cur.execute("""SELECT Subreddits.Name, sum(Postings.score) FROM Postings INNER JOIN Subreddits on Subreddits.ID = Postings.subreddit_id GROUP BY Subreddits.Name""")
    dic = cur.fetchall()
    subreddits = []
    scores = []
    for subreddit in dic:
        subreddits.append(subreddit[0])
        scores.append(subreddit[1])

    data = [go.Bar(
            x=subreddits,
            y=scores,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]
    layout = go.Layout(
            title = 'Cumulative Scores of Top 24 Hour Postings Per Subreddit Page',
            xaxis=dict(
                tickfont=dict(
                    size=12,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='Cumulative Daily Scores',
                titlefont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=12,
                    color='rgb(107, 107, 107)'
                )
            )
        )
    print('opening...')
    fig = go.Figure(data = data, layout = layout)
    py.offline.plot(fig, filename="subreddit_analysis.html")

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
        run_search_on_default()

    elif command == 'plot':
        plot()