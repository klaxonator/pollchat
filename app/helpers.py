from app import app, db
from datetime import datetime, timedelta, date
import json
import requests
from app.models import User, Post, District, Hashtag, Url


# Time for functions always uses reference date/time of previous midnight UTC
def stringtime(time_delta):
    if time_delta == None:
        time_delta = "7"
    today = datetime.combine(date.today(), datetime.min.time())
    time_range = today - timedelta(days=int(time_delta))
    str_time_range = time_range.strftime('%Y-%m-%d')
    return str_time_range

def get_tweet_datetime(stringtime, format='%Y-%m-%d %H:%M:%S'):
    datetime_version = datetime.strptime(stringtime, format)
    return datetime_version



def get_tweet(post_id, omit_script=True, hide_media=True):
    url = 'https://api.twitter.com/1.1/statuses/oembed.json'
    params= {'id': post_id,
             'omit_script': omit_script,
             'hide_media': hide_media}

    r = requests.get(url, params=params)
    if r.status_code != 200:
            return _("Error: the call to Twitter's service failed.")
    return json.loads(r.content.decode('utf-8-sig'))['html']


def check_district_relevance(db_tweet):

    #Search district associations with post
    db_tweet = db_tweet

    referenced_districts = db.session.query(District.district_name).\
    join(Post.districts).\
    filter(Post.post_id == db_tweet[0]).all()

    # Create list of districts associated with post - generally only one,
    # but someitmes multiple mentions

    district_list = []

    for distref in referenced_districts:
        district_list.append(distref[0])

    # print(district_list)

    # iterate through district_list, get dist_aliases from dictionary,

    for named_district in district_list:
        # print(distdict[named_district])

        for district_alias in distdict_short[named_district]:

    # check if any of district aliases are included in tweet text;
            # if finds a match, return True

            #NOTE: too many variations of search found by twitter in scr_name
            # if district_alias in db_tweet[1].lower() or \
            #   district_alias in db_tweet[4].lower():
            #     return False

            if db_tweet[7]:
                if district_alias in db_tweet[7].lower():
                    return True
            else:
                if district_alias in db_tweet[6].lower():
                    return True
    #
    #if no match found, return False

    return False

    # return True

def check_district_relevance_st(tweet_texts):

    #Incoming db object has Post_id, Post.text, Post.original_text

    #Search district associations with post
    tweet_texts = tweet_texts

    referenced_districts = db.session.query(District.district_name).\
    join(Post.districts).\
    filter(Post.post_id == tweet_texts[0]).all()

    # Create list of districts associated with post - generally only one,
    # but someitmes multiple mentions

    district_list = []

    for distref in referenced_districts:
        district_list.append(distref[0])

    # print(district_list)

    # iterate through district_list, get dist_aliases from dictionary,

    for named_district in district_list:
        # print(distdict[named_district])

        # check if any of district aliases are included in tweet text;
        # if finds a match, return True
        for district_alias in distdict_short[named_district]:

            if tweet_texts[2]:
                if district_alias in tweet_texts[2].lower():
                    return True
            else:
                if district_alias in tweet_texts[1].lower():
                    return True

    # if no match found, return False

    return False






def get_tweet_list_ids(db_search_object):

    # produce list of top retweeted ids for fill. Db object is
    # Post_post_id, Post.original_tweet_id, Post.retweet_count

    most_retweeted_tweets = db_search_object
    seen_tweets = []                    #list of tweets used to avoid duplicates
    tweet_id_list = []                   #list of retweets to return
    count = 0

    skipped_tweets = []
    for db_tweet in most_retweeted_tweets:

        #if the tweet id/original tweet_id has already been seen, skip

        if db_tweet[0] in seen_tweets or db_tweet[1] in seen_tweets:
            continue

        # Add IDs to seen_tweets list

        seen_tweets.append(db_tweet[0])
        if db_tweet[1]:
            seen_tweets.append(db_tweet[1])


        #Get text items for comparison

        tweet_texts = db.session.query(Post.post_id, Post.text, Post.original_text,\
        User.user_scrname, Post.tweet_html, Post.original_tweet_id, \
        Post.original_author_scrname).\
        join(Post.user).\
        filter(Post.post_id==db_tweet[0]).first()

        check = check_district_relevance_st(tweet_texts)


        if check == False:
            # print("skipping tweet_id {0}, \ntext: {1}\n full_text: {2}\nscreen name: {3}\n\n".\
            # format(tweet_texts[0], tweet_texts[1], tweet_texts[2], tweet_texts[3]))

            skipped_tweets.append(tweet_texts[0])

            continue



        # List: Post_id, orig author name, retweet count, tweet_html, orig ID
        if tweet_texts[6]:
            tweet_id_list.append([db_tweet[0], tweet_texts[6], \
            db_tweet[2], tweet_texts[4], tweet_texts[5]])

        # List: Post_id, base post author, retweet count, tweet_html, orig ID
        else:
            tweet_id_list.append([db_tweet[0], tweet_texts[3], \
            db_tweet[2], tweet_texts[4], tweet_texts[5]])

        count += 1
        # print("The Seen_Tweets list has {} items".format(len(seen_tweets)))
        # print("The Skipped_Tweets list has {} items".format(len(skipped_tweets)))
        if count == 20:
            return tweet_id_list
    return tweet_id_list


def populate_tweet_list(tweet_list):

    # tweet_list is list of 20 tweets, with each row including:
    # [Post.post_id, relevant screen name, retweet_count, tweet_html (if exists),
    # original_tweet_id]
    populated_list = []

    for item in tweet_list:
        tweet = []

        # LIST POSITION [0]: Base post ID
        tweet.append(item[0])                               # Post.post_id

        # LIST POSITION [1]: Screen name
        tweet.append(item[1])                               # relevant screen name

        # LIST POSITION [2]: Retweet Count
        tweet.append(item[2])                               # retweet_count

        # LIST POSITION [3]: Post HTML for Tweet display
        if item[3]:
            tweet.append(item[3])                           # tweet_html
        else:
            if item[4]:
                try:
                    tweet_html = get_tweet(item[4])         # get html of original tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Can't retrieve Tweet")

            #if not RT (no original_tweet_id), use post ID
            else:
                try:
                    tweet_html = get_tweet(item[0])         # get html of base tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Can't retrieve Tweet")

        # LIST POSITION [4]: User Botscore
        botscore = db.session.query(User.user_cap_perc).\
        filter(User.user_scrname==tweet[1]).first()

        if botscore:
            tweet.append(botscore[0])                       # append botscore
        else:
            tweet.append("Not yet in database")

        populated_list.append(tweet)

    return populated_list


def get_tweet_list(db_search_object):

    # produce list of (Post.post_id, Post.original_author_scrname, \
    # Post.retweet_count, Post.original_tweet_id, User.user_scrname, \
    # Post.tweet_html, Post.text)

    # db_object in order Post_id, original_author_scrname, retweet_count,\
    # original_tweet_idk, user_scrname, tweet_html, text, original_text

    most_retweeted_tweets = db_search_object
    seen_tweets = []                #list of tweets used to avoid duplicates
    most_retweeted_tweet_list = []      #list of retweets for site
    count = 0                           #count to get total of 5

    for db_tweet in most_retweeted_tweets:

        #if the tweet id/original tweet_id has already been seen, skip

        if db_tweet[3] in seen_tweets or db_tweet[0] in seen_tweets:
            continue
        seen_tweets.append(db_tweet[0])
        if db_tweet[3]:
            seen_tweets.append(db_tweet[3])

        #Check if district name is in text
        check = check_district_relevance(db_tweet)

        if check == False:
            # print("Skipping tweet_id {}".format(db_tweet[0]))
            # print("Screenname was: {}".format(db_tweet[4]))
            continue



        #create actual tweet list
        tweet = []

        # LIST POSITION [0]: Post.post_id
        tweet.append(db_tweet[0])           # post_id: list [db_tweet0]

        # LIST POSITION [1]: Author screen name (orig author if RT)
        if db_tweet[1]:                     #if retweet
            tweet.append(db_tweet[1])           # post original author

        else:                               # or if original tweet
            tweet.append(db_tweet[4])       # User.user_scrname

        # LIST POSITION [2]: Retweet Count
        tweet.append(db_tweet[2])


        # LIST POSITION [3]: Botscore
            # Get botscore for original poster using the tweet[1] of this list:
            # either original_author (if RT) or post author (if not RT)
        botscore = db.session.query(User.user_cap_perc).\
        filter(User.user_scrname==tweet[1]).first()

        if botscore:
            tweet.append(botscore[0])           # append botscore
        else:
            tweet.append("Not yet in database")


        # LIST POSITION [4]: Post HTML (to call Tweet)
            #if loop: if tweet_html already exists
        if db_tweet[5]:
            tweet.append(db_tweet[5])         #tweet_html

            #if no tweet_html, then get HTML from Twitter
        else:
            #if RT (if original_tweet_id exists)
            if db_tweet[3]:
                try:
                    tweet_html = get_tweet(db_tweet[3]) # get html of original tweet
                    tweet.append(tweet_html)            # add tweet_text
                except:
                    tweet.append("Can't retrieve Tweet")

            #if not RT (no original_tweet_id), use post ID
            else:
                try:
                    tweet_html = get_tweet(db_tweet[0])     # get html of base tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Can't retrieve Tweet")


        most_retweeted_tweet_list.append(tweet)
        count += 1
        if count == 5:
            break

    return most_retweeted_tweet_list

dists = [
('az01', 'Arizona 01'),
('az02', 'Arizona 02'),
('az06', 'Arizona  06'),
('az09', 'Arizona 09'),
('ar02', 'Arkansas 02'),
('ca04', 'California 04'),
('ca07', 'California 07'),
('ca10', 'California 10'),
('ca21', 'California 21'),
('ca25', 'California 25'),
('ca39', 'California 39'),
('ca45', 'California 45'),
('ca48', 'California 48'),
('ca49', 'California 49'),
('ca50', 'California 50'),
('co06', 'Colorado 06'),
('ct05', 'Connecticut 05'),
('fl07', 'Florida 07'),
('fl15', 'Florida 15'),
('fl16', 'Florida 16'),
('fl18', 'Florida 18'),
('fl25', 'Florida 25'),
('fl26', 'Florida 26'),
('fl27', 'Florida 27'),
('ga06', 'Georgia 06'),
('ga07', 'Georgia 07'),
('ia01', 'Iowa 01'),
('ia03', 'Iowa 03'),
('il06', 'Illinois 06'),
('il12', 'Illinois 12'),
('il13', 'Illinois 13'),
('il14', 'Illinois 14'),
('in02', 'Indiana 02'),
('ks02', 'Kansas 02'),
('ks03', 'Kansas 03'),
('ky06', 'Kansas 06'),
('me02', 'Maine 02'),
('mi01', 'Michigan 01'),
('mi06', 'Michigan 06'),
('mi07', 'Michigan 07'),
('mi08', 'Michigan 08'),
('mi11', 'Michigan 11'),
('mn01', 'Minnesota  01'),
('mn02', 'Minnesota  02'),
('mn03', 'Minnesota  03'),
('mn07', 'Minnesota  07'),
('mn08', 'Minnesota  08'),
('mo02', 'Missouri 02'),
('mt00', 'Montana 00'),
('nc02', 'North Carolina 02'),
('nc08', 'North Carolina 08'),
('nc09', 'North Carolina 09'),
('nc13', 'North Carolina 13'),
('ne02', 'Nevada 02'),
('nh01', 'New Hampshire 01'),
('nh02', 'New Hampshire 02'),
('nj02', 'New Jersey 02'),
('nj03', 'New Jersey 03'),
('nj05', 'New Jersey 05'),
('nj07', 'New Jersey 07'),
('nj11', 'New Jersey 11'),
('nm02', 'New Mexico 02'),
('nv03', 'Nevada 03'),
('nv04', 'Nevada 04'),
('ny01', 'New York 01'),
('ny11', 'New York 11'),
('ny19', 'New York 19'),
('ny22', 'New York 22'),
('ny24', 'New York 24'),
('oh01', 'Ohio 01'),
('oh10', 'Ohio 10'),
('oh12', 'Ohio 12'),
('oh14', 'Ohio 14'),
('oh15', 'Ohio 15'),
('pa01', 'Pennsylvania 01'),
('pa05', 'Pennsylvania 05'),
('pa06', 'Pennsylvania 06'),
('pa07', 'Pennsylvania 07'),
('pa08', 'Pennsylvania 08'),
('pa10', 'Pennsylvania 10'),
('pa14', 'Pennsylvania 14'),
('pa16', 'Pennsylvania 16'),
('pa17', 'Pennsylvania 17'),
('sc01', 'South Carolina 01'),
('sc05', 'South Carolina 05'),
('tx07', 'Texas 07'),
('tx21', 'Texas 21'),
('tx23', 'Texas 23'),
('tx32', 'Texas 32'),
('ut04', 'Utah 04'),
('va02', 'Virginia 02'),
('va05', 'Virginia 05'),
('va07', 'Virginia 07'),
('va10', 'Virginia 10'),
('wa03', 'Washington 03'),
('wa05', 'Washington 05'),
('wa08', 'Washington 08'),
('wi01', 'Wisconsin 01'),
('wi03', 'Wisconsin 03'),
('wi06', 'Wisconsin 06'),
('wi07', 'Wisconsin 07'),
('wv03', 'West Virginia 03')
]

distlist = ['az01', 'az02', 'az06', 'az09', 'ar02', 'ca04', 'ca07', 'ca10',
 'ca21', 'ca25', 'ca39', 'ca45', 'ca48', 'ca49', 'ca50', 'co06', 'ct05',
 'fl07', 'fl15', 'fl16', 'fl18', 'fl25', 'fl26', 'fl27', 'ga06', 'ga07',
 'ia01', 'ia03', 'il06', 'il12', 'il13', 'il14', 'in02', 'ks02', 'ks03',
 'ky06', 'me02', 'mi01', 'mi06', 'mi07', 'mi08', 'mi11', 'mn01', 'mn02',
 'mn03', 'mn07', 'mn08', 'mo02', 'mt00', 'nc02', 'nc08', 'nc09', 'nc13',
 'ne02', 'nh01', 'nh02', 'nj02', 'nj03', 'nj05', 'nj07', 'nj11', 'nm02',
 'nv03', 'nv04', 'ny01', 'ny11', 'ny19', 'ny22', 'ny24', 'oh01', 'oh10',
 'oh12', 'oh14', 'oh15', 'pa01', 'pa05', 'pa06', 'pa07', 'pa08', 'pa10',
 'pa14', 'pa16', 'pa17', 'sc01', 'sc05', 'tx07', 'tx21', 'tx23', 'tx32',
 'ut04', 'va02', 'va05', 'va07', 'va10', 'wa03', 'wa05', 'wa08', 'wi01',
 'wi03', 'wi06', 'wi07', 'wv03' 'az1', 'az2', 'az6', 'az9', 'ar2', 'ca4',
 'ca7', 'co6', 'ct5', 'fl7', 'ga6', 'ga7', 'ia1', 'ia3', 'il6', 'in2', 'ks2',
 'ks3', 'ky6', 'me2', 'mi1', 'mi6', 'mi7', 'mi8', 'mn1', 'mn2', 'mn3', 'mn7',
 'mn8', 'mo2', 'mt0', 'nc2', 'nc8', 'nc9', 'ne2', 'nh1', 'nh2', 'nj2', 'nj3',
 'nj5', 'nj7', 'nm2', 'nv3', 'nv4', 'ny1', 'oh1', 'pa1', 'pa5', 'pa6', 'pa7',
 'pa8', 'sc1', 'sc5', 'tx7', 'ut4', 'va2', 'va5', 'va7', 'wa3', 'wa5', 'wa8',
 'wi1', 'wi3', 'wi6', 'wi7', 'wv3']

a = '''<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">RIGHT. LIKE IT’S JUST BAKING A CAKE AMIRITE? <a href="https://t.co/O9kC1pnDr1">https://t.co/O9kC1pnDr1</a></p>&mdash; Shannon Watts (@shannonrwatts) <a href="https://twitter.com/shannonrwatts/status/1006269046009065473?ref_src=twsrc%5Etfw">June 11, 2018</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'''

b = '''<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Just watching Svalbard, right. <br>

        <br>The man that visibly winced when Serena screamed “this is what a feminist looks like” is one of the reasons I wanted to work with this band. <br>
        <br>Heh heh.</p>&mdash; Becky (@ArrJayEll) <a href="https://twitter.com/ArrJayEll/status/998287358851256320?ref_src=twsrc%5Etfw">May 20, 2018</a>

    </blockquote><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'''

test_insert = [a, b]

test_hashgraph_data = [['Date', 'fl07', 'flapol', 'sayfie', 'faithincongressact', 'ny14'],
 ['May 19', 9, 2, 0, 0, 0],
 ['May 20', 24, 24, 0, 0, 0],
 ['May 21', 10, 10, 0, 0, 0],
 ['May 22', 21, 8, 6, 0, 0],
 ['May 23', 21, 7, 0, 0, 0],
 ['May 24', 20, 16, 12, 6, 0],
 ['May 25', 31, 26, 18, 18, 0],
 ['May 26', 8, 1, 1, 1, 4],
 ['May 27', 9, 9, 9, 1, 0],
 ['May 28', 0, 0, 0, 0, 0]]

test_usergraph_data = [['Date',
  'steveferraramd',
  'CongressRTBot',
  'RavenRothisPink',
  'RedboysF',
  'RepSinema'],
 ['May 19', 2, 0, 0, 0, 0],
 ['May 20', 0, 0, 0, 0, 0],
 ['May 21', 0, 0, 0, 0, 0],
 ['May 22', 1, 0, 0, 0, 0],
 ['May 23', 0, 0, 0, 0, 0],
 ['May 24', 1, 0, 0, 0, 0],
 ['May 25', 6, 1, 2, 1, 1],
 ['May 26', 0, 1, 0, 1, 1],
 ['May 27', 0, 0, 0, 0, 0],
 ['May 28', 0, 0, 0, 0, 0]]


skip_list = [
    "xiaomi",
    "visitkingston",
    "carcamera",
    "dashcrash",
    "hshq",
    "HSHQ",
    "thewarrior",
    "TheWarrior",
    "fl15_official",
    "cumbria",
    "Cumbria"
    ]

distdict_short =  {'az09': ['az09', 'az-09', '#az09', '#az-09', '#az9'],
             'ca07': ['ca07', 'ca-07', '#ca07', '#ca-07', '#ca7'],
             'ct05': ['ct05', 'ct-05', '#ct05', '#ct-05', '#ct5'],
             'fl07': ['fl07', 'fl-07', '#fl07', '#fl-07', '#fl7'],
             'mn07': ['mn07', 'mn-07', '#mn07', '#mn-07', '#mn7'],
             'nh02': ['nh02', 'nh-02', '#nh02', '#nh-02', '#nh2'],
             'nj05': ['nj05', 'nj-05', '#nj05', '#nj-05', '#nj5'],
             'nv04': ['nv04', 'nv-04', '#nv04', '#nv-04', '#nv4'],
             'pa05': ['pa05', 'pa-05', '#pa05', '#pa-05', '#pa5'],
             'pa06': ['pa06', 'pa-06', '#pa06', '#pa-06', '#pa6'],
             'pa08': ['pa08', 'pa-08', '#pa08', '#pa-08', '#pa8'],
             'wi03': ['wi03', 'wi-03', '#wi03', '#wi-03', '#wi3'],
             'az01': ['az01', 'az-01', '#az01', '#az-01', '#az1'],
             'az02': ['az02', 'az-02', '#az02', '#az-02', '#az2'],
             'ca39': ['ca39', 'ca-39', '#ca39', '#ca-39'],
             'ca49': ['ca49', 'ca-49', '#ca49', '#ca-49'],
             'fl27': ['fl27', 'fl-27', '#fl27', '#fl-27'],
             'nh01': ['nh01', 'nh-01', '#nh01', '#nh-01', '#nh1'],
             'nj02': ['nj02', 'nj-02', '#nj02', '#nj-02', '#nj2'],
             'nv03': ['nv03', 'nv-03', '#nv03', '#nv-03', '#nv3'],
             'pa07': ['pa07', 'pa-07', '#pa07', '#pa-07', '#pa7'],
             'mn01': ['mn01', 'mn-01', '#mn01', '#mn-01', '#mn1'],
             'mn08': ['mn08', 'mn-08', '#mn08', '#mn-08', '#mn8'],
             'ca10': ['ca10', 'ca-10', '#ca10', '#ca-10'],
             'ca25': ['ca25', 'ca-25', '#ca25', '#ca-25'],
             'ca48': ['ca48', 'ca-48', '#ca48', '#ca-48'],
             'co06': ['co06', 'co-06', '#co06', '#co-06', '#co6'],
             'fl26': ['fl26', 'fl-26', '#fl26', '#fl-26'],
             'ia01': ['ia01', 'ia-01', '#ia01', '#ia-01', '#ia1'],
             'il06': ['il06', 'il-06', '#il06', '#il-06', '#il6'],
             'il12': ['il12', 'il-12', '#il12', '#il-12'],
             'mi11': ['mi11', 'mi-11', '#mi11', '#mi-11'],
             'mn02': ['mn02', 'mn-02', '#mn02', '#mn-02', '#mn2'],
             'mn03': ['mn03', 'mn-03', '#mn03', '#mn-03', '#mn3'],
             'ne02': ['ne02', 'ne-02', '#ne02', '#ne-02', '#ne2'],
             'nj07': ['nj07', 'nj-07', '#nj07', '#nj-07', '#nj7'],
             'nj11': ['nj11', 'nj-11', '#nj11', '#nj-11'],
             'ny19': ['ny19', 'ny-19', '#ny19', '#ny-19'],
             'ny22': ['ny22', 'ny-22', '#ny22', '#ny-22'],
             'oh12': ['oh12', 'oh-12', '#oh12', '#oh-12'],
             'pa01': ['pa01', 'pa-01', '#pa01', '#pa-01', '#pa1'],
             'pa17': ['pa17', 'pa-17', '#pa17', '#pa-17'],
             'tx07': ['tx07', 'tx-07', '#tx07', '#tx-07', '#tx7'],
             'va10': ['va10', 'va-10', '#va10', '#va-10'],
             'wa08': ['wa08', 'wa-08', '#wa08', '#wa-08', '#wa8'],
             'ar02': ['ar02', 'ar-02', '#ar02', '#ar-02', '#ar2'],
             'ca21': ['ca21', 'ca-21', '#ca21', '#ca-21'],
             'ca45': ['ca45', 'ca-45', '#ca45', '#ca-45'],
             'fl18': ['fl18', 'fl-18', '#fl18', '#fl-18'],
             'ga06': ['ga06', 'ga-06', '#ga06', '#ga-06', '#ga6'],
             'ia03': ['ia03', 'ia-03', '#ia03', '#ia-03', '#ia3'],
             'il14': ['il14', 'il-14', '#il14', '#il-14'],
             'ks02': ['ks02', 'ks-02', '#ks02', '#ks-02'],
             'ks03': ['ks03', 'ks-03', '#ks03', '#ks-03'],
             'ky06': ['ky06', 'ky-06', '#ky06', '#ky-06', '#ky6'],
             'me02': ['me02', 'me-02', '#me02', '#me-02', '#me2'],
             'mi08': ['mi08', 'mi-08', '#mi08', '#mi-08'],
             'nc09': ['nc09', 'nc-09', '#nc09', '#nc-09', '#nc9'],
             'nc13': ['nc13', 'nc-13', '#nc13', '#nc-13'],
             'nj03': ['nj03', 'nj-03', '#nj03', '#nj-03', '#nj3'],
             'nm02': ['nm02', 'nm-02', '#nm02', '#nm-02', '#nm2'],
             'ny11': ['ny11', 'ny-11', '#ny11', '#ny-11'],
             'oh01': ['oh01', 'oh-01', '#oh01', '#oh-01', '#oh1'],
             'tx23': ['tx23', 'tx-23', '#tx23', '#tx-23'],
             'tx32': ['tx32', 'tx-32', '#tx32', '#tx-32'],
             'ut04': ['ut04', 'ut-04', '#ut04', '#ut-04', '#ut4'],
             'va02': ['va02', 'va-02', '#va02', '#va-02', '#va2'],
             'va05': ['va05', 'va-05', '#va05', '#va-05', '#va5'],
             'va07': ['va07', 'va-07', '#va07', '#va-07', '#va7'],
             'wa05': ['wa05', 'wa-05', '#wa05', '#wa-05', '#wa5'],
             'wi01': ['wi01', 'wi-01', '#wi01', '#wi-01', '#wi1'],
             'az06': ['az06', 'az-06', '#az06', '#az-06', '#az6'],
             'ca04': ['ca04', 'ca-04', '#ca04', '#ca-04', '#ca4'],
             'ca50': ['ca50', 'ca-50', '#ca50', '#ca-50'],
             'fl15': ['fl15', 'fl-15', '#fl15', '#fl-15'],
             'fl16': ['fl16', 'fl-16', '#fl16', '#fl-16'],
             'fl25': ['fl25', 'fl-25', '#fl25', '#fl-25'],
             'ga07': ['ga07', 'ga-07', '#ga07', '#ga-07', '#ga7'],
             'il13': ['il13', 'il-13', '#il13', '#il-13'],
             'in02': ['in02', 'in-02', '#in02', '#in-02', '#in2'],
             'mi01': ['mi01', 'mi-01', '#mi01', '#mi-01', '#mi1'],
             'mi06': ['mi06', 'mi-06', '#mi06', '#mi-06'],
             'mi07': ['mi07', 'mi-07', '#mi07', '#mi-07', '#mi7'],
             'mo02': ['mo02', 'mo-02', '#mo02', '#mo-02', '#mo2'],
             'mtAL': ['mtAL', 'mt-AL', '#mtAL', '#mt-AL'],
             'mt00': ['mt00', 'mt-00', '#mt00', '#mt-00'],
             'nc02': ['nc02', 'nc-02', '#nc02', '#nc-02', '#nc2'],
             'nc08': ['nc08', 'nc-08', '#nc08', '#nc-08', '#nc8'],
             'ny01': ['ny01', 'ny-01', '#ny01', '#ny-01', '#ny1'],
             'ny24': ['ny24', 'ny-24', '#ny24', '#ny-24'],
             'oh10': ['oh10', 'oh-10', '#oh10', '#oh-10'],
             'oh14': ['oh14', 'oh-14', '#oh14', '#oh-14'],
             'oh15': ['oh15', 'oh-15', '#oh15', '#oh-15'],
             'pa10': ['pa10', 'pa-10', '#pa10', '#pa-10'],
             'pa14': ['pa14', 'pa-14', '#pa14', '#pa-14'],
             'pa16': ['pa16', 'pa-16', '#pa16', '#pa-16'],
             'sc01': ['sc01', 'sc-01', '#sc01', '#sc-01', '#sc1'],
             'sc05': ['sc05', 'sc-05', '#sc05', '#sc-05', '#sc5'],
             'tx21': ['tx21', 'tx-21', '#tx21', '#tx-21'],
             'wa03': ['wa03', 'wa-03', '#wa03', '#wa-03', '#wa3'],
             'wi06': ['wi06', 'wi-06', '#wi06', '#wi-06', '#wi6'],
             'wi07': ['wi07', 'wi-07', '#wi07', '#wi-07', '#wi7'],
             'wv03': ['wv03', 'wv-03', '#wv03', '#wv-03', '#wv3']
             }

distdict = {'ar02': ['ar02', 'ar-02', '#ar02', '#ar-02', '#ar2', 'ar2'],
            'az01': ['az01', 'az-01', '#az01', '#az-01', '#az1', 'az1'],
            'az02': ['az02', 'az-02', '#az02', '#az-02', '#az2', 'az2'],
            'az06': ['az06', 'az-06', '#az06', '#az-06', '#az6', 'az6'],
            'az09': ['az09', 'az-09', '#az09', '#az-09', '#az9', 'az9'],
            'ca04': ['ca04', 'ca-04', '#ca04', '#ca-04', '#ca4', 'ca4'],
            'ca07': ['ca07', 'ca-07', '#ca07', '#ca-07', '#ca7', 'ca7'],
            'ca10': ['ca10', 'ca-10', '#ca10', '#ca-10'],
            'ca21': ['ca21', 'ca-21', '#ca21', '#ca-21'],
            'ca25': ['ca25', 'ca-25', '#ca25', '#ca-25'],
            'ca39': ['ca39', 'ca-39', '#ca39', '#ca-39'],
            'ca45': ['ca45', 'ca-45', '#ca45', '#ca-45'],
            'ca48': ['ca48', 'ca-48', '#ca48', '#ca-48'],
            'ca49': ['ca49', 'ca-49', '#ca49', '#ca-49'],
            'ca50': ['ca50', 'ca-50', '#ca50', '#ca-50'],
            'co06': ['co06', 'co-06', '#co06', '#co-06', '#co6', 'co6'],
            'ct05': ['ct05', 'ct-05', '#ct05', '#ct-05', '#ct5', 'ct5'],
            'fl07': ['fl07', 'fl-07', '#fl07', '#fl-07', '#fl7', 'fl7'],
            'fl15': ['fl15', 'fl-15', '#fl15', '#fl-15'],
            'fl16': ['fl16', 'fl-16', '#fl16', '#fl-16'],
            'fl18': ['fl18', 'fl-18', '#fl18', '#fl-18'],
            'fl25': ['fl25', 'fl-25', '#fl25', '#fl-25'],
            'fl26': ['fl26', 'fl-26', '#fl26', '#fl-26'],
            'fl27': ['fl27', 'fl-27', '#fl27', '#fl-27'],
            'ga06': ['ga06', 'ga-06', '#ga06', '#ga-06', '#ga6', 'ga6'],
            'ga07': ['ga07', 'ga-07', '#ga07', '#ga-07', '#ga7', 'ga7'],
            'ia01': ['ia01', 'ia-01', '#ia01', '#ia-01', '#ia1', 'ia1'],
            'ia03': ['ia03', 'ia-03', '#ia03', '#ia-03', '#ia3', 'ia3'],
            'il06': ['il06', 'il-06', '#il06', '#il-06', '#il6', 'il6'],
            'il12': ['il12', 'il-12', '#il12', '#il-12'],
            'il13': ['il13', 'il-13', '#il13', '#il-13'],
            'il14': ['il14', 'il-14', '#il14', '#il-14'],
            'in02': ['in02', 'in-02', '#in02', '#in-02', '#in2', 'in2'],
            'ks02': ['ks02', 'ks-02', '#ks02', '#ks-02'],
            'ks03': ['ks03', 'ks-03', '#ks03', '#ks-03'],
            'ky06': ['ky06', 'ky-06', '#ky06', '#ky-06', '#ky6', 'ky6'],
            'me02': ['me02', 'me-02', '#me02', '#me-02', '#me2', 'me2'],
            'mi01': ['mi01', 'mi-01', '#mi01', '#mi-01', '#mi1', 'mi1'],
            'mi06': ['mi06', 'mi-06', '#mi06', '#mi-06'],
            'mi07': ['mi07', 'mi-07', '#mi07', '#mi-07', '#mi7', 'mi7'],
            'mi08': ['mi08', 'mi-08', '#mi08', '#mi-08'],
            'mi11': ['mi11', 'mi-11', '#mi11', '#mi-11'],
            'mn01': ['mn01', 'mn-01', '#mn01', '#mn-01', '#mn1', 'mn1'],
            'mn02': ['mn02', 'mn-02', '#mn02', '#mn-02', '#mn2', 'mn2'],
            'mn03': ['mn03', 'mn-03', '#mn03', '#mn-03', '#mn3', 'mn3'],
            'mn07': ['mn07', 'mn-07', '#mn07', '#mn-07', '#mn7', 'mn7'],
            'mn08': ['mn08', 'mn-08', '#mn08', '#mn-08', '#mn8', 'mn8'],
            'mo02': ['mo02', 'mo-02', '#mo02', '#mo-02', '#mo2', 'mo2'],
            'mtAL': ['mtAL', 'mt-AL', '#mtAL', '#mt-AL'],
            'nc02': ['nc02', 'nc-02', '#nc02', '#nc-02', '#nc2', 'nc2'],
            'nc08': ['nc08', 'nc-08', '#nc08', '#nc-08', '#nc8', 'nc8'],
            'nc09': ['nc09', 'nc-09', '#nc09', '#nc-09', '#nc9', 'nc9'],
            'nc13': ['nc13', 'nc-13', '#nc13', '#nc-13'],
            'ne02': ['ne02', 'ne-02', '#ne02', '#ne-02', '#ne2', 'ne2'],
            'nh01': ['nh01', 'nh-01', '#nh01', '#nh-01', '#nh1', 'nh1'],
            'nh02': ['nh02', 'nh-02', '#nh02', '#nh-02', '#nh2', 'nh2'],
            'nj02': ['nj02', 'nj-02', '#nj02', '#nj-02', '#nj2', 'nj2'],
            'nj03': ['nj03', 'nj-03', '#nj03', '#nj-03', '#nj3', 'nj3'],
            'nj05': ['nj05', 'nj-05', '#nj05', '#nj-05', '#nj5', 'nj5'],
            'nj07': ['nj07', 'nj-07', '#nj07', '#nj-07', '#nj7', 'nj7'],
            'nj11': ['nj11', 'nj-11', '#nj11', '#nj-11'],
            'nm02': ['nm02', 'nm-02', '#nm02', '#nm-02', '#nm2', 'nm2'],
            'nv03': ['nv03', 'nv-03', '#nv03', '#nv-03', '#nv3', 'nv3'],
            'nv04': ['nv04', 'nv-04', '#nv04', '#nv-04', '#nv4', 'nv4'],
            'ny01': ['ny01', 'ny-01', '#ny01', '#ny-01', '#ny1', 'ny1'],
            'ny11': ['ny11', 'ny-11', '#ny11', '#ny-11'],
            'ny19': ['ny19', 'ny-19', '#ny19', '#ny-19'],
            'ny22': ['ny22', 'ny-22', '#ny22', '#ny-22'],
            'ny24': ['ny24', 'ny-24', '#ny24', '#ny-24'],
            'oh01': ['oh01', 'oh-01', '#oh01', '#oh-01', '#oh1', 'oh1'],
            'oh10': ['oh10', 'oh-10', '#oh10', '#oh-10'],
            'oh12': ['oh12', 'oh-12', '#oh12', '#oh-12'],
            'oh14': ['oh14', 'oh-14', '#oh14', '#oh-14'],
            'oh15': ['oh15', 'oh-15', '#oh15', '#oh-15'],
            'pa01': ['pa01', 'pa-01', '#pa01', '#pa-01', '#pa1', 'pa1'],
            'pa05': ['pa05', 'pa-05', '#pa05', '#pa-05', '#pa5', 'pa5'],
            'pa06': ['pa06', 'pa-06', '#pa06', '#pa-06', '#pa6', 'pa6'],
            'pa07': ['pa07', 'pa-07', '#pa07', '#pa-07', '#pa7', 'pa7'],
            'pa08': ['pa08', 'pa-08', '#pa08', '#pa-08', '#pa8', 'pa8'],
            'pa10': ['pa10', 'pa-10', '#pa10', '#pa-10'],
            'pa14': ['pa14', 'pa-14', '#pa14', '#pa-14'],
            'pa16': ['pa16', 'pa-16', '#pa16', '#pa-16'],
            'pa17': ['pa17', 'pa-17', '#pa17', '#pa-17'],
            'sc01': ['sc01', 'sc-01', '#sc01', '#sc-01', '#sc1', 'sc1'],
            'sc05': ['sc05', 'sc-05', '#sc05', '#sc-05', '#sc5', 'sc5'],
            'tx07': ['tx07', 'tx-07', '#tx07', '#tx-07', '#tx7', 'tx7'],
            'tx21': ['tx21', 'tx-21', '#tx21', '#tx-21'],
            'tx23': ['tx23', 'tx-23', '#tx23', '#tx-23'],
            'tx32': ['tx32', 'tx-32', '#tx32', '#tx-32'],
            'ut04': ['ut04', 'ut-04', '#ut04', '#ut-04', '#ut4', 'ut4'],
            'va02': ['va02', 'va-02', '#va02', '#va-02', '#va2', 'va2'],
            'va05': ['va05', 'va-05', '#va05', '#va-05', '#va5', 'va5'],
            'va07': ['va07', 'va-07', '#va07', '#va-07', '#va7', 'va7'],
            'va10': ['va10', 'va-10', '#va10', '#va-10'],
            'wa03': ['wa03', 'wa-03', '#wa03', '#wa-03', '#wa3', 'wa3'],
            'wa05': ['wa05', 'wa-05', '#wa05', '#wa-05', '#wa5', 'wa5'],
            'wa08': ['wa08', 'wa-08', '#wa08', '#wa-08', '#wa8', 'wa8'],
            'wi01': ['wi01', 'wi-01', '#wi01', '#wi-01', '#wi1', 'wi1'],
            'wi03': ['wi03', 'wi-03', '#wi03', '#wi-03', '#wi3', 'wi3'],
            'wi06': ['wi06', 'wi-06', '#wi06', '#wi-06', '#wi6', 'wi6'],
            'wi07': ['wi07', 'wi-07', '#wi07', '#wi-07', '#wi7', 'wi7'],
            'wv03': ['wv03', 'wv-03', '#wv03', '#wv-03', '#wv3', 'wv3']}
