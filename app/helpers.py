from app import app, db
from datetime import datetime, timedelta, date
import json
import requests
from app.models import *
import sys
import tweepy
import app.tweepy_cred_mf as cred
import csv
import sys
import time
from textblob import TextBlob
from sqlalchemy import exc, func
import urllib.request



class Logger(object):
    def __init__(self, logfile):
        self.terminal = sys.stdout
        self.log = open(logfile, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #put extra behavior here?
        pass

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
    "Cumbria",
    "dog",
    "lost",
    "widnes",
    "cronton",
    "cheshire",
    "stillmissing",
    "sausage",
    "hshq",
    "spursofficial",
    "teamspeak",
    "asiangames",
    "asus_rog",
    "giveaway",
    "gaming"
    ]

def today():
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight

def str_today():
    #Set beginning of searches at midnight, so have full-day comparisons
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight

    str_today = today.strftime("%Y-%m-%d %H:%M:%S")         # string version of midnight
    return str_today

# Time for functions always uses reference date/time of previous midnight UTC
# Means that 1-day search will be 24 hours plus however many hours into day it is
def stringtime(time_delta):
    if time_delta == None:
        time_delta = "7"
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight
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

    #incoming db object in order: Post_id, original_author_scrname, retweet_count,\
    # original_tweet_id, user_scrname, tweet_html, text, original_text

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

        for district_keyword in distdict_short[named_district]:

    # check if any of district aliases are included in tweet text;
            # if finds a match, return True

            if db_tweet[7]:
                if district_keyword in db_tweet[7].lower():
                    return True
            else:
                if district_keyword in db_tweet[6].lower():
                    return True
    #
    #if no match found, return False

    return False

    # return True

def check_district_relevance_st(tweet_texts):

    #Incoming db object has Post_id, Post.text, Post.original_text

    #if from get_tweet_list_ids, tweet_texts is: Post.post_id, Post.text, Post.original_text,\
    # User.user_scrname, Post.tweet_html, Post.original_tweet_id,

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

    #print(district_list)

    # iterate through district_list, get dist_aliases from dictionary (distdict_short)

    for named_district in district_list:

        # check if any of district aliases are included in tweet text;
        # if finds a match, return True
        for district_keyword in distdict_short[named_district]:

            if tweet_texts[2]:
                if district_keyword in tweet_texts[2].lower():
                    #print(district_keyword)
                    return True
            else:
                if district_keyword in tweet_texts[1].lower():
                    #print(district_keyword)
                    return True

    # if no match found, return False

    return False






def get_tweet_list_ids(db_search_object):

    # produce list of top retweeted ids for fill. Db object is
    # Post_post_id, Post.original_tweet_id, Post.retweet_count, District.dist_type

    most_retweeted_tweets = db_search_object
    seen_tweets = []                    #list of tweets used to avoid duplicates
    tweet_id_list = []                   #list of retweets to return
    count = 0

    skipped_tweets = []
    for db_tweet in most_retweeted_tweets:

        #if the tweet id/original tweet_id has already been seen, skip
        print(db_tweet[0], db_tweet[3])

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

        if tweet_texts[3] in skip_list or tweet_texts[6] in skip_list:
            continue

        # check district relevance
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
                    tweet.append("Tweet unavailable")

            #if not RT (no original_tweet_id), use post ID
            else:
                try:
                    tweet_html = get_tweet(item[0])         # get html of base tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Tweet unavailable")

        # LIST POSITION [4]: User Botscore
        botscore = db.session.query(User.user_cap_perc).\
        filter(User.user_scrname==tweet[1]).first()

        if botscore:
            tweet.append(botscore[0])                       # append botscore
        else:
            tweet.append("Not yet in database")

        populated_list.append(tweet)

    return populated_list


def get_tweet_list(db_search_object, distname):

    # produce list of (Post.post_id, Post.original_author_scrname, \
    # Post.retweet_count, Post.original_tweet_id, User.user_scrname, \
    # Post.tweet_html, Post.text)

    # db_object in order 0)Post_id, 1)original_author_scrname, 2)retweet_count,\
    # 3)original_tweet_id, 4) user_scrname, 5) tweet_html, 6)text, 7)original_text

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

        #If original_author in skiplist, skip
        if db_tweet[1]:
            if db_tweet[1].lower() in skip_list:
                continue

        #Check if district name is in text; skip if Senate district

        #if distname[2:5] != 'Sen':
        check = check_district_relevance(db_tweet)

        if check == False:
            # print("Skipping tweet_id {}".format(db_tweet[0]))
            # print("Screenname was: {}".format(db_tweet[4]))
            continue



        # create actual tweet list: [post_id, scrname, retweet_count, botscore,
        # post_html, ]
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
                    tweet.append("Tweet unavailable")

            #if not RT (no original_tweet_id), use post ID
            else:
                try:
                    tweet_html = get_tweet(db_tweet[0])     # get html of base tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Tweet unavailable")


        most_retweeted_tweet_list.append(tweet)
        count += 1
        if count == 5:
            break

    return most_retweeted_tweet_list



def get_tweet_list_inperiod(db_search_object):

    '''Gets list of tweets with info to pass to template, using list of tweets
    produced by most_retweeted_inperiod. db_search_object is ordered list of original_id,
    count(original_id)

    Want to return post_id, name, count, botscore, html'''

    most_retweeted_inperiod_list = []
    count = 0
    for tweet in db_search_object:
        holding_list = []

        user_info = db.session.query(User.user_scrname, User.user_cap_perc, \
        Post.text).\
        join(Post.user).\
        filter(Post.post_id==tweet[0]).first()

        if user_info:
            if user_info[0].lower() in skip_list:
                continue
        else:
            print("gonna add that missing tweet")

            # if referenced tweet isn't in database, get it
            try:
                check = add_tweet(tweet[0])

            # if tweet not accessible, handle Tweepy error
            except tweepy.error.TweepError as err:
                check = False

            if check == False:
                continue
            print("added it in, gonna look for it again")

            user_info = db.session.query(User.user_scrname, User.user_cap_perc, \
            Post.text).\
            join(Post.user).\
            filter(Post.post_id==tweet[0]).first()


        #ADD RELEVANCE SEARCH

        try:
            tweet_html = get_tweet(tweet[0])
        except:
            tweet_html = "Tweet unavailable"

        # list position [0]: post_id
        holding_list.append(tweet[0])
        # list position [1]: user_scrname
        if user_info:
            holding_list.append(user_info[0])
        else:
            holding_list.append("Original post not yet in database")

        # list position [2]: post count
        holding_list.append(tweet[1])

        # list position [3]: user_cap_perc
        if user_info:
            holding_list.append(user_info[1])
        else:
            holding_list.append("Original post not yet in database")

        # list position [4]: tweet_html
        holding_list.append(tweet_html)

        print(holding_list)

        most_retweeted_inperiod_list.append(holding_list)
        count += 1
        if count == 5:
            break

    return most_retweeted_inperiod_list



def get_tweet_list_nodist(db_search_object):

    # ROLE produce list of [Post.post_id, Post.original_author_scrname, \
    # Post.retweet_count, Post.original_tweet_id,  \
    # Post.tweet_html, Post.text)

    # db_object in order: 0)Post_id, 1)original_author_scrname, 2)retweet_count,\
    # 3)original_tweet_id, 4)tweet_html, 5)text, 6)original_text

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

        if db_tweet[1]:
            if db_tweet[1].lower() in skip_list:
                continue

        #Check if district name is in text; skip if Senate district

        #NOTE: FIND ANOTHER WAY TO CHECK RELEVANCE
        # check = check_district_relevance(db_tweet)
        #
        # if check == False:
        #     # print("Skipping tweet_id {}".format(db_tweet[0]))
        #     # print("Screenname was: {}".format(db_tweet[4]))
        #     continue



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
        # if db_tweet[4]:
        #     tweet.append(db_tweet[4])         #tweet_html
        #
        #     #if no tweet_html, then get HTML from Twitter
        # else:
        #     #if RT (if original_tweet_id exists)
        if db_tweet[3]:
            try:
                tweet_html = get_tweet(db_tweet[3]) # get html of original tweet
                tweet.append(tweet_html)            # add tweet_text
            except:
                tweet.append("Tweet unavailable")

        #if not RT (no original_tweet_id), use post ID
        else:
            try:
                tweet_html = get_tweet(db_tweet[0])     # get html of base tweet
                tweet.append(tweet_html)                # add tweet_text
            except:
                tweet.append("Tweet unavailable")


        most_retweeted_tweet_list.append(tweet)
        count += 1
        if count == 5:
            break

    return most_retweeted_tweet_list

def get_tweet_list_dated(db_search_object, time_delta):

    # produce list of (Post.post_id, Post.original_author_scrname, \
    # Post.retweet_count, Post.original_tweet_id, User.user_scrname, \
    # Post.tweet_html, Post.text)

    # db_object in order Post_id, original_author_scrname, retweet_count,\
    # original_tweet_id, user_scrname, tweet_html, text, original_text

    most_retweeted_tweets = db_search_object
    seen_tweets = []                #list of tweets used to avoid duplicates
    most_retweeted_tweet_list = []      #list of retweets for site
    count = 0                           #count to get total of 5
    time_check = stringtime(time_delta)

    for db_tweet in most_retweeted_tweets:



        #if the tweet id/original tweet_id has already been seen, skip

        if db_tweet[3] in seen_tweets or db_tweet[0] in seen_tweets:
            continue
        seen_tweets.append(db_tweet[0])
        if db_tweet[3]:
            seen_tweets.append(db_tweet[3])

        if db_tweet[1]:
            if db_tweet[1].lower() in skip_list:
                continue

        #Check if district name is in text
        check = check_district_relevance(db_tweet)

        if check == False:
            # print("Skipping tweet_id {}".format(db_tweet[0]))
            # print("Screenname was: {}".format(db_tweet[4]))
            continue

        # Get original tweet's created at date
        orig_tweet = db.session.query(Post.post_id, Post.created_at).\
        filter(Post.post_id==db_tweet[3]).first()

        # If orig tweet in database...
        if orig_tweet:

            # if original tweet date < time_delta, skip

            if orig_tweet[1] < time_check:
                continue

        # Otherwise skip
        else:
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
                    tweet.append("Tweet unavailable")

            #if not RT (no original_tweet_id), use post ID
            else:
                try:
                    tweet_html = get_tweet(db_tweet[0])     # get html of base tweet
                    tweet.append(tweet_html)                # add tweet_text
                except:
                    tweet.append("Tweet unavailable")


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
('co03', 'Colorado 03'),
('co06', 'Colorado 06'),
('ct05', 'Connecticut 05'),
('fl06', 'Florida 06'),
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
('mi03', 'Michigan 03'),
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
('ny21', 'New York 21'),
('ny22', 'New York 22'),
('ny24', 'New York 24'),
('ny25', 'New York 25'),
('ny27', 'New York 27'),
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
('tx31', 'Texas 31'),
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

sen_dists = [
('AZSen', 'Arizona'),
('FLSen', 'Florida'),
('INSen', 'Indiana'),
('MISen', 'Michigan'),
('MNSen', 'Minnesota'),
('MSSen', 'Mississippi'),
('MOSen', 'Missouri'),
('MTSen', 'Montana'),
('NESen', 'Nebraska'),
('NVSen', 'Nevada'),
('NJSen', 'New Jersey'),
('NDSen', 'North Dakota'),
('OHSen', 'Ohio'),
('PASen', 'Pennsylvania'),
('TNSen', 'Tennessee'),
('TXSen', 'Texas'),
('WVSen', 'West Virginia'),
('WISen', 'Wisconsin')
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
 'wi1', 'wi3', 'wi6', 'wi7', 'wv3', 'OHSen', 'INSen', 'NDSen', 'WVSen', 'NVSen',
 'TXSen', 'NESen', 'MSSen', 'MTSen','NJSen', 'PASen', 'TNSen', 'MISen', 'MOSen',
 'MNSen', 'WISen', 'AZSen', 'FLSen', 'ohsen', 'insen', 'ndsen', 'wvsen', 'nvsen',
 'txsen', 'nesen', 'mssen', 'mtsen','njsen', 'pasen', 'tnsen', 'misen', 'mosen',
 'mnsen', 'wisen', 'azsen', 'flsen','ny27','fl06', 'co03', 'ny25','tx31', 'mtal'
 'mi03', 'ny21']




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




distdict_short_old =  {'az09': ['az09', 'az-09', '#az09', '#az-09', '#az9', 'az 09'],
             'ca07': ['ca07', 'ca-07', '#ca07', '#ca-07', '#ca7', 'ca 07'],
             'ct05': ['ct05', 'ct-05', '#ct05', '#ct-05', '#ct5', 'ct 05'],
             'fl07': ['fl07', 'fl-07', '#fl07', '#fl-07', '#fl7', 'fl 07'],
             'mn07': ['mn07', 'mn-07', '#mn07', '#mn-07', '#mn7', 'mn 07'],
             'nh02': ['nh02', 'nh-02', '#nh02', '#nh-02', '#nh2', 'nh 02'],
             'nj05': ['nj05', 'nj-05', '#nj05', '#nj-05', '#nj5', 'nj 05'],
             'nv04': ['nv04', 'nv-04', '#nv04', '#nv-04', '#nv4', 'nv 04'],
             'pa05': ['pa05', 'pa-05', '#pa05', '#pa-05', '#pa5', 'pa 05'],
             'pa06': ['pa06', 'pa-06', '#pa06', '#pa-06', '#pa6', 'pa 06'],
             'pa08': ['pa08', 'pa-08', '#pa08', '#pa-08', '#pa8', 'pa 08'],
             'wi03': ['wi03', 'wi-03', '#wi03', '#wi-03', '#wi3', 'wi 03'],
             'az01': ['az01', 'az-01', '#az01', '#az-01', '#az1', 'az 01'],
             'az02': ['az02', 'az-02', '#az02', '#az-02', '#az2', 'az 02'],
             'ca39': ['ca39', 'ca-39', '#ca39', '#ca-39', 'ca 39'],
             'ca49': ['ca49', 'ca-49', '#ca49', '#ca-49', 'ca 49'],
             'fl27': ['fl27', 'fl-27', '#fl27', '#fl-27', 'fl 27'],
             'nh01': ['nh01', 'nh-01', '#nh01', '#nh-01', '#nh1', 'nh 01'],
             'nj02': ['nj02', 'nj-02', '#nj02', '#nj-02', '#nj2', 'nj 02'],
             'nv03': ['nv03', 'nv-03', '#nv03', '#nv-03', '#nv3', 'nv 03'],
             'pa07': ['pa07', 'pa-07', '#pa07', '#pa-07', '#pa7', 'pa 07'],
             'mn01': ['mn01', 'mn-01', '#mn01', '#mn-01', '#mn1', 'mn 01'],
             'mn08': ['mn08', 'mn-08', '#mn08', '#mn-08', '#mn8', 'mn 08'],
             'ca10': ['ca10', 'ca-10', '#ca10', '#ca-10', 'ca 10'],
             'ca25': ['ca25', 'ca-25', '#ca25', '#ca-25', 'ca 25'],
             'ca48': ['ca48', 'ca-48', '#ca48', '#ca-48', 'ca 48'],
             'co06': ['co06', 'co-06', '#co06', '#co-06', '#co6', 'co 06'],
             'fl26': ['fl26', 'fl-26', '#fl26', '#fl-26', 'fl 26'],
             'ia01': ['ia01', 'ia-01', '#ia01', '#ia-01', '#ia1', 'ia 01'],
             'il06': ['il06', 'il-06', '#il06', '#il-06', '#il6', 'il 06'],
             'il12': ['il12', 'il-12', '#il12', '#il-12', 'il 12'],
             'mi11': ['mi11', 'mi-11', '#mi11', '#mi-11', 'mi 11'],
             'mn02': ['mn02', 'mn-02', '#mn02', '#mn-02', '#mn2', 'mn 02'],
             'mn03': ['mn03', 'mn-03', '#mn03', '#mn-03', '#mn3', 'mn 03'],
             'ne02': ['ne02', 'ne-02', '#ne02', '#ne-02', '#ne2', 'ne 02'],
             'nj07': ['nj07', 'nj-07', '#nj07', '#nj-07', '#nj7', 'nj 07'],
             'nj11': ['nj11', 'nj-11', '#nj11', '#nj-11', 'nj 11'],
             'ny19': ['ny19', 'ny-19', '#ny19', '#ny-19', 'ny 19'],
             'ny21': ['ny21', 'ny-21', '#ny21', '#ny-21', 'ny 21'],
             'ny22': ['ny22', 'ny-22', '#ny22', '#ny-22', 'ny 22'],
             'oh12': ['oh12', 'oh-12', '#oh12', '#oh-12', 'oh 12'],
             'pa01': ['pa01', 'pa-01', '#pa01', '#pa-01', '#pa1', 'pa 01'],
             'pa17': ['pa17', 'pa-17', '#pa17', '#pa-17', 'pa 17'],
             'tx07': ['tx07', 'tx-07', '#tx07', '#tx-07', '#tx7', 'tx 07'],
             'va10': ['va10', 'va-10', '#va10', '#va-10', 'va 10'],
             'wa08': ['wa08', 'wa-08', '#wa08', '#wa-08', '#wa8', 'wa 08'],
             'ar02': ['ar02', 'ar-02', '#ar02', '#ar-02', '#ar2', 'ar 02'],
             'ca21': ['ca21', 'ca-21', '#ca21', '#ca-21', 'ca 21'],
             'ca45': ['ca45', 'ca-45', '#ca45', '#ca-45', 'ca 45'],
             'fl18': ['fl18', 'fl-18', '#fl18', '#fl-18', 'fl 18'],
             'ga06': ['ga06', 'ga-06', '#ga06', '#ga-06', '#ga6', 'ga 06'],
             'ia03': ['ia03', 'ia-03', '#ia03', '#ia-03', '#ia3', 'ia 03'],
             'il14': ['il14', 'il-14', '#il14', '#il-14', 'il 14'],
             'ks02': ['ks02', 'ks-02', '#ks02', '#ks-02', 'ks 02'],
             'ks03': ['ks03', 'ks-03', '#ks03', '#ks-03', 'ks 03'],
             'ky06': ['ky06', 'ky-06', '#ky06', '#ky-06', '#ky6', 'ky 06'],
             'me02': ['me02', 'me-02', '#me02', '#me-02', '#me2', 'me 02'],
             'mi08': ['mi08', 'mi-08', '#mi08', '#mi-08', 'mi 08'],
             'nc09': ['nc09', 'nc-09', '#nc09', '#nc-09', '#nc9', 'mc 09'],
             'nc13': ['nc13', 'nc-13', '#nc13', '#nc-13', 'nc 13'],
             'nj03': ['nj03', 'nj-03', '#nj03', '#nj-03', '#nj3', 'nj 03'],
             'nm02': ['nm02', 'nm-02', '#nm02', '#nm-02', '#nm2', 'nm 02'],
             'ny11': ['ny11', 'ny-11', '#ny11', '#ny-11', 'ny 11'],
             'oh01': ['oh01', 'oh-01', '#oh01', '#oh-01', '#oh1', 'oh 01'],
             'tx23': ['tx23', 'tx-23', '#tx23', '#tx-23', 'tx 23'],
             'tx32': ['tx32', 'tx-32', '#tx32', '#tx-32', 'tx 32'],
             'ut04': ['ut04', 'ut-04', '#ut04', '#ut-04', '#ut4', 'ut 04'],
             'va02': ['va02', 'va-02', '#va02', '#va-02', '#va2', 'va 02'],
             'va05': ['va05', 'va-05', '#va05', '#va-05', '#va5', 'va 05'],
             'va07': ['va07', 'va-07', '#va07', '#va-07', '#va7', 'va 07'],
             'wa05': ['wa05', 'wa-05', '#wa05', '#wa-05', '#wa5', 'wa 05'],
             'wi01': ['wi01', 'wi-01', '#wi01', '#wi-01', '#wi1', 'wi 01'],
             'az06': ['az06', 'az-06', '#az06', '#az-06', '#az6', 'az 06'],
             'ca04': ['ca04', 'ca-04', '#ca04', '#ca-04', '#ca4', 'ca 04'],
             'ca50': ['ca50', 'ca-50', '#ca50', '#ca-50', 'ca 50'],
             'fl15': ['fl15', 'fl-15', '#fl15', '#fl-15', 'fl 15'],
             'fl16': ['fl16', 'fl-16', '#fl16', '#fl-16', 'fl 16'],
             'fl25': ['fl25', 'fl-25', '#fl25', '#fl-25', 'fl 25'],
             'ga07': ['ga07', 'ga-07', '#ga07', '#ga-07', '#ga7', 'ga 07'],
             'il13': ['il13', 'il-13', '#il13', '#il-13', 'il 13'],
             'in02': ['in02', 'in-02', '#in02', '#in-02', '#in2', 'in 02'],
             'mi01': ['mi01', 'mi-01', '#mi01', '#mi-01', '#mi1', 'mi 01'],
             'mi03': ['mi03', 'mi-03', '#mi03', '#mi-03', '#mi3', 'mi 03'],
             'mi06': ['mi06', 'mi-06', '#mi06', '#mi-06', 'mi 06'],
             'mi07': ['mi07', 'mi-07', '#mi07', '#mi-07', '#mi7', 'mi 07'],
             'mo02': ['mo02', 'mo-02', '#mo02', '#mo-02', '#mo2', 'mo 02'],
             'mtAL': ['mtal', 'mt-al', '#mtal', '#mt-al', 'mt al'],
             'mt00': ['mt00', 'mt-00', '#mt00', '#mt-00', 'mt 00'],
             'nc02': ['nc02', 'nc-02', '#nc02', '#nc-02', '#nc2', 'nc 02'],
             'nc08': ['nc08', 'nc-08', '#nc08', '#nc-08', '#nc8', 'nc 08'],
             'ny01': ['ny01', 'ny-01', '#ny01', '#ny-01', '#ny1', 'ny 01'],
             'ny24': ['ny24', 'ny-24', '#ny24', '#ny-24', 'ny 24'],
             'oh10': ['oh10', 'oh-10', '#oh10', '#oh-10', 'oh 10'],
             'oh14': ['oh14', 'oh-14', '#oh14', '#oh-14', 'oh 14'],
             'oh15': ['oh15', 'oh-15', '#oh15', '#oh-15', 'oh 15'],
             'pa10': ['pa10', 'pa-10', '#pa10', '#pa-10', 'pa 10'],
             'pa14': ['pa14', 'pa-14', '#pa14', '#pa-14', 'pa 14'],
             'pa16': ['pa16', 'pa-16', '#pa16', '#pa-16', 'pa 16'],
             'sc01': ['sc01', 'sc-01', '#sc01', '#sc-01', '#sc1', 'sc 01'],
             'sc05': ['sc05', 'sc-05', '#sc05', '#sc-05', '#sc5', 'sc 05'],
             'tx21': ['tx21', 'tx-21', '#tx21', '#tx-21', 'tx 21'],
             'wa03': ['wa03', 'wa-03', '#wa03', '#wa-03', '#wa3', 'wa 03'],
             'wi06': ['wi06', 'wi-06', '#wi06', '#wi-06', '#wi6', 'wi 06'],
             'wi07': ['wi07', 'wi-07', '#wi07', '#wi-07', '#wi7', 'wi 07'],
             'wv03': ['wv03', 'wv-03', '#wv03', '#wv-03', '#wv3', 'wv 03'],
             'ny27': ['ny27', 'ny-27', '#ny27', '#ny-27', 'ny 27'],
             'fl06': ['fl06', 'fl-06', '#fl06', '#fl-06', '#fl6', 'fl 06'],
             'co03': ['co03', 'co-03', '#co03', '#co-03', '#co3', 'co 03'],
             'ny25': ['ny25', 'ny-25', '#ny25', '#ny-25', 'ny 25'],
             'tx31': ['tx31', 'tx-31', '#tx31', '#tx-31', 'tx 31'],
             'OHSen': ['ohsen', '#ohsen', 'oh', 'brown', 'ohio', 'renacci'],
             'INSen': ['insen', '#insen', 'in', 'donnelly', 'indiana', 'braun'],
             'NDSen': ['ndsen', '#ndsen', 'nd', 'heitkamp', 'north dakota', 'cramer'],
             'WVSen': ['wvsen', '#wvsen', 'wv', 'manchin', 'west virginia', 'morrisey'],
             'NVSen': ['nvsen', '#nvsen', 'nv', 'rosen', 'nevada', 'heller'],
             'TXSen': ['txsen', '#txsen', 'tx', 'o’rourke', 'texas', 'cruz', 'beto'],
             'NESen': ['nesen', '#nesen', 'ne', 'raybould', 'nebraska', 'fischer'],
             'MSSen': ['mssen', '#mssen', 'ms', 'baria', 'mississippi', 'wicker'],
             'MTSen': ['mtsen', '#mtsen', 'mt', 'tester', 'montana', 'rosendale'],
             'NJSen': ['njsen', '#njsen', 'nj', 'menendez', 'new jersey', 'hugin'],
             'PASen': ['pasen', '#pasen', 'pa', 'casey', 'montana', 'barletta'],
             'TNSen': ['tnsen', '#tnsen', 'tn', 'bredesen', 'tennessee', 'blackburn'],
             'MISen': ['misen', '#misen', 'mi', 'stabenow', 'michigan', 'james'],
             'MOSen': ['mosen', '#mosen', 'mo', 'mccaskill', 'missouri', 'hawley'],
             'MNSen': ['mnsen', '#mnsen', 'mn', 'smith', 'minnesota', 'housley'],
             'WISen': ['wisen', '#wisen', 'wi', 'baldwin', 'wisconsin', 'vukmir'],
             'AZSen': ['azsen', '#azsen', 'az', 'sinema', 'arizona', 'mcsally'],
             'FLSen': ['flsen', '#flsen', 'fl', 'nelson', 'florida', 'scott'],
             }

distdict_short = {'AZSen': ['azsen', '#azsen', 'az', 'sinema', 'arizona', 'mcsally'],
                 'FLSen': ['flsen', '#flsen', 'fl', 'nelson', 'florida', 'scott'],
                 'INSen': ['insen', '#insen', 'in', 'donnelly', 'indiana', 'braun'],
                 'MISen': ['misen', '#misen', 'mi', 'stabenow', 'michigan', 'james'],
                 'MNSen': ['mnsen', '#mnsen', 'mn', 'smith', 'minnesota', 'housley'],
                 'MOSen': ['mosen', '#mosen', 'mo', 'mccaskill', 'missouri', 'hawley'],
                 'MSSen': ['mssen', '#mssen', 'ms', 'baria', 'mississippi', 'wicker'],
                 'MTSen': ['mtsen', '#mtsen', 'mt', 'tester', 'montana', 'rosendale'],
                 'NDSen': ['ndsen', '#ndsen', 'nd', 'heitkamp', 'north dakota', 'cramer'],
                 'NESen': ['nesen', '#nesen', 'ne', 'raybould', 'nebraska', 'fischer'],
                 'NJSen': ['njsen', '#njsen', 'nj', 'menendez', 'new jersey', 'hugin'],
                 'NVSen': ['nvsen', '#nvsen', 'nv', 'rosen', 'nevada', 'heller'],
                 'OHSen': ['ohsen', '#ohsen', 'oh', 'brown', 'ohio', 'renacci'],
                 'PASen': ['pasen', '#pasen', 'pa', 'casey', 'montana', 'barletta'],
                 'TNSen': ['tnsen', '#tnsen', 'tn', 'bredesen', 'tennessee', 'blackburn'],
                 'TXSen': ['txsen', '#txsen', 'tx', 'o’rourke', 'texas', 'cruz'],
                 'WISen': ['wisen', '#wisen', 'wi', 'baldwin', 'wisconsin', 'vukmir'],
                 'WVSen': ['wvsen', '#wvsen', 'wv', 'manchin', 'west virginia', 'morrisey'],
                 'ar02': ['ar02',
                          'ar-02',
                          '#ar02',
                          '#ar-02',
                          '#ar2',
                          'ar 02',
                          'clarketucker',
                          'wendyrogersaz',
                          'arkansas',
                          'tucker',
                          'hill'],
                 'az01': ['az01',
                          'az-01',
                          '#az01',
                          '#az-01',
                          '#az1',
                          'az 01',
                          'tomohalleran',
                          'leapeterson',
                          'arizona',
                          "o'halleran",
                          'rogers'],
                 'az02': ['az02',
                          'az-02',
                          '#az02',
                          '#az-02',
                          '#az2',
                          'az 02',
                          'ann_kirkpatrick',
                          'davidschweikert',
                          'arizona',
                          'kirkpatrick',
                          'peterson'],
                 'az06': ['az06',
                          'az-06',
                          '#az06',
                          '#az-06',
                          '#az6',
                          'az 06',
                          'anitamalik',
                          'steveferraramd',
                          'arizona',
                          'malik',
                          'schweikert'],
                 'az09': ['az09',
                          'az-09',
                          '#az09',
                          '#az-09',
                          '#az9',
                          'az 09',
                          'mayorstanton',
                          'electfrench',
                          'arizona',
                          'stanton',
                          'ferrara'],
                 'ca04': ['ca04',
                          'ca-04',
                          '#ca04',
                          '#ca-04',
                          '#ca4',
                          'ca 04',
                          'morse4america',
                          'tommcclintock',
                          'california',
                          'morse',
                          'mcclintock'],
                 'ca07': ['ca07',
                          'ca-07',
                          '#ca07',
                          '#ca-07',
                          '#ca7',
                          'ca 07',
                          'beraforcongress',
                          'andrewfgrant',
                          'california',
                          'bera',
                          'grant'],
                 'ca10': ['ca10',
                          'ca-10',
                          '#ca10',
                          '#ca-10',
                          'ca 10',
                          'joshua_harder',
                          'jeffdenham',
                          'california',
                          'harder',
                          'denham'],
                 'ca21': ['ca21',
                          'ca-21',
                          '#ca21',
                          '#ca-21',
                          'ca 21',
                          'tjcoxcongress',
                          'dgvaladao',
                          'california',
                          'cox',
                          'valadao'],
                 'ca25': ['ca25',
                          'ca-25',
                          '#ca25',
                          '#ca-25',
                          'ca 25',
                          'katiehill4ca',
                          'teamknight25',
                          'california',
                          'hill',
                          'knight'],
                 'ca39': ['ca39',
                          'ca-39',
                          '#ca39',
                          '#ca-39',
                          'ca 39',
                          'gilcisnerosca',
                          'youngkimcd39',
                          'california',
                          'cisneros',
                          'kim'],
                 'ca45': ['ca45',
                          'ca-45',
                          '#ca45',
                          '#ca-45',
                          'ca 45',
                          'katieporteroc',
                          'mimiwaltersca',
                          'california',
                          'porter',
                          'walters'],
                 'ca48': ['ca48',
                          'ca-48',
                          '#ca48',
                          '#ca-48',
                          'ca 48',
                          'harleyrouda',
                          'danarohrabacher',
                          'california',
                          'rouda',
                          'rohrabacher'],
                 'ca49': ['ca49',
                          'ca-49',
                          '#ca49',
                          '#ca-49',
                          'ca 49',
                          'mikelevinca \u200f',
                          'diane_harkey',
                          'california',
                          'levin',
                          'harkey'],
                 'ca50': ['ca50',
                          'ca-50',
                          '#ca50',
                          '#ca-50',
                          'ca 50',
                          'acampanajjar',
                          'rep_hunter',
                          'california',
                          'campa-najjar',
                          'hunter'],
                 'co03': ['co03',
                          'co-03',
                          '#co03',
                          '#co-03',
                          '#co3',
                          'co 03',
                          'repdmb',
                          'scottrtipton',
                          'colorado',
                          'bush',
                          'tipton'],
                 'co06': ['co06',
                          'co-06',
                          '#co06',
                          '#co-06',
                          '#co6',
                          'co 06',
                          'jasoncrowco6',
                          'coffmanforco',
                          'colorado',
                          'crow',
                          'coffman'],
                 'ct05': ['ct05',
                          'ct-05',
                          '#ct05',
                          '#ct-05',
                          '#ct5',
                          'ct 05',
                          'jahanahayes',
                          'santos4congress',
                          'connecticut',
                          'hayes',
                          'santos'],
                 'fl06': ['fl06',
                          'fl-06',
                          '#fl06',
                          '#fl-06',
                          '#fl6',
                          'fl 06',
                          'nancysoderberg',
                          'michaelgwaltz',
                          'florida',
                          'soderberg',
                          'waltz'],
                 'fl07': ['fl07',
                          'fl-07',
                          '#fl07',
                          '#fl-07',
                          '#fl7',
                          'fl 07',
                          'smurphycongress',
                          'mike_miller_fl',
                          'florida',
                          'murphy',
                          'miller'],
                 'fl15': ['fl15',
                          'fl-15',
                          '#fl15',
                          '#fl-15',
                          'fl 15',
                          'kristenforfl',
                          'rossspano',
                          'florida',
                          'carlson',
                          'spano'],
                 'fl16': ['fl16',
                          'fl-16',
                          '#fl16',
                          '#fl-16',
                          'fl 16',
                          'vern2014',
                          'shapiro4fl16',
                          'florida',
                          'buchanan',
                          'shapiro'],
                 'fl18': ['fl18',
                          'fl-18',
                          '#fl18',
                          '#fl-18',
                          'fl 18',
                          'laurenbaer',
                          'brianmastfl',
                          'florida',
                          'baer',
                          'mast'],
                 'fl25': ['fl25',
                          'fl-25',
                          '#fl25',
                          '#fl-25',
                          'fl 25',
                          'mbfforcongress',
                          'mariodb',
                          'florida',
                          'flores',
                          'diaz-balart'],
                 'fl26': ['fl26',
                          'fl-26',
                          '#fl26',
                          '#fl-26',
                          'fl 26',
                          'debbieforfl',
                          'carloslcurbelo',
                          'florida',
                          'mucarsel-powell',
                          'curbelo'],
                 'fl27': ['fl27',
                          'fl-27',
                          '#fl27',
                          '#fl-27',
                          'fl 27',
                          'donnashalala',
                          'maelvirasalazar',
                          'florida',
                          'shalala',
                          'salazar'],
                 'ga06': ['ga06',
                          'ga-06',
                          '#ga06',
                          '#ga-06',
                          '#ga6',
                          'ga 06',
                          'lucywins2018',
                          'karenhandel',
                          'georgia',
                          'mcbath',
                          'handel'],
                 'ga07': ['ga07',
                          'ga-07',
                          '#ga07',
                          '#ga-07',
                          '#ga7',
                          'ga 07',
                          'carolyn4ga7',
                          'reprobwoodall',
                          'georgia',
                          'bourdeaux',
                          'woodall'],
                 'ia01': ['ia01',
                          'ia-01',
                          '#ia01',
                          '#ia-01',
                          '#ia1',
                          'ia 01',
                          'abby4iowa',
                          'rodblum',
                          'iowa',
                          'finkenauer',
                          'blum'],
                 'ia03': ['ia03',
                          'ia-03',
                          '#ia03',
                          '#ia-03',
                          '#ia3',
                          'ia 03',
                          'axne4congress',
                          'youngforiowa',
                          'iowa',
                          'axne',
                          'young'],
                 'il06': ['il06',
                          'il-06',
                          '#il06',
                          '#il-06',
                          '#il6',
                          'il 06',
                          'seancasten',
                          'teamroskam',
                          'illinois',
                          'casten',
                          'roskam'],
                 'il12': ['il12',
                          'il-12',
                          '#il12',
                          '#il-12',
                          'il 12',
                          'kelly4southrnil',
                          'bostforcongress',
                          'illinois',
                          'kelly',
                          'bost'],
                 'il13': ['il13',
                          'il-13',
                          '#il13',
                          '#il-13',
                          'il 13',
                          'betsyforil',
                          'electrodney',
                          'illinois',
                          'londrigan',
                          'davis'],
                 'il14': ['il14',
                          'il-14',
                          '#il14',
                          '#il-14',
                          'il 14',
                          'lunderwood630',
                          'randyhultgren',
                          'illinois',
                          'underwood',
                          'hultgren'],
                 'in02': ['in02',
                          'in-02',
                          '#in02',
                          '#in-02',
                          '#in2',
                          'in 02',
                          'melforcongress',
                          'jackiewalorski',
                          'indiana',
                          'hall',
                          'walorski'],
                 'ks02': ['ks02',
                          'ks-02',
                          '#ks02',
                          '#ks-02',
                          'ks 02',
                          'pauldavisks',
                          'steve4kansas',
                          'kansas',
                          'davis',
                          'watkins'],
                 'ks03': ['ks03',
                          'ks-03',
                          '#ks03',
                          '#ks-03',
                          'ks 03',
                          'sharicedavids',
                          'kevinyoder',
                          'kansas',
                          'davids',
                          'yoder'],
                 'ky06': ['ky06',
                          'ky-06',
                          '#ky06',
                          '#ky-06',
                          '#ky6',
                          'ky 06',
                          'amymcgrathky',
                          'barrforcongress',
                          'kentucky',
                          'mcgrath',
                          'barr'],
                 'me02': ['me02',
                          'me-02',
                          '#me02',
                          '#me-02',
                          '#me2',
                          'me 02',
                          'golden4congress',
                          'brucepoliquin',
                          'maine',
                          'golden',
                          'poliquin'],
                 'mi01': ['mi01',
                          'mi-01',
                          '#mi01',
                          '#mi-01',
                          '#mi1',
                          'mi 01',
                          'morganformi',
                          'jackbergman_mi1',
                          'michigan',
                          'morgan',
                          'bergman'],
                 'mi03': ['mi03',
                          'mi-03',
                          '#mi03',
                          '#mi-03',
                          '#mi3',
                          'mi 03',
                          'cathy albro',
                          'justinamash',
                          'michigan',
                          'albro',
                          'amash'],
                 'mi06': ['mi06',
                          'mi-06',
                          '#mi06',
                          '#mi-06',
                          'mi 06',
                          'mattlongjohn',
                          'uptonforallofus',
                          'michigan',
                          'longjohn',
                          'upton'],
                 'mi07': ['mi07',
                          'mi-07',
                          '#mi07',
                          '#mi-07',
                          '#mi7',
                          'mi 07',
                          'gdriskell',
                          'teamwalberg',
                          'michigan',
                          'driskell',
                          'walberg'],
                 'mi08': ['mi08',
                          'mi-08',
                          '#mi08',
                          '#mi-08',
                          'mi 08',
                          'elissaslotkin',
                          'electmikebishop',
                          'michigan',
                          'slotkin',
                          'bishop'],
                 'mi11': ['mi11',
                          'mi-11',
                          '#mi11',
                          '#mi-11',
                          'mi 11',
                          'haleylive',
                          'lenaepstein',
                          'michigan',
                          'stevens',
                          'epstein'],
                 'mn01': ['mn01',
                          'mn-01',
                          '#mn01',
                          '#mn-01',
                          '#mn1',
                          'mn 01',
                          'danielfeehan',
                          'jimhagedornmn',
                          'minnesota',
                          'feehan',
                          'hagedorn'],
                 'mn02': ['mn02',
                          'mn-02',
                          '#mn02',
                          '#mn-02',
                          '#mn2',
                          'mn 02',
                          'angiecraigmn',
                          'jason2cd',
                          'minnesota',
                          'craig',
                          'lewis'],
                 'mn03': ['mn03',
                          'mn-03',
                          '#mn03',
                          '#mn-03',
                          '#mn3',
                          'mn 03',
                          'deanbphillips',
                          'erik_paulsen',
                          'minnesota',
                          'phillips',
                          'paulsen'],
                 'mn07': ['mn07',
                          'mn-07',
                          '#mn07',
                          '#mn-07',
                          '#mn7',
                          'mn 07',
                          'collinpeterson',
                          'dhughescongress',
                          'minnesota',
                          'peterson',
                          'hughes'],
                 'mn08': ['mn08',
                          'mn-08',
                          '#mn08',
                          '#mn-08',
                          '#mn8',
                          'mn 08',
                          'joeradinovich',
                          'petestauber',
                          'minnesota',
                          'radinovich',
                          'stauber'],
                 'mo02': ['mo02',
                          'mo-02',
                          '#mo02',
                          '#mo-02',
                          '#mo2',
                          'mo 02',
                          'cortvo',
                          'annlwagner',
                          'missouri',
                          'vanostran',
                          'wagner'],
                 'mt00': ['mt00',
                          'mt-00',
                          '#mt00',
                          '#mt-00',
                          'mt 00',
                          'montana',
                          'williams',
                          'gianforte'],
                 'mtAL': ['mtal',
                          'mt-al',
                          '#mtal',
                          '#mt-al',
                          'mt al',
                          'williamsformt',
                          'gregformontana'],
                 'nc02': ['nc02',
                          'nc-02',
                          '#nc02',
                          '#nc-02',
                          '#nc2',
                          'nc 02',
                          'lindafornc',
                          'georgeholding',
                          'north carolina',
                          'coleman',
                          'holding'],
                 'nc08': ['nc08',
                          'nc-08',
                          '#nc08',
                          '#nc-08',
                          '#nc8',
                          'nc 08',
                          'frank4nc',
                          'richhudson',
                          'north carolina',
                          'mcneill',
                          'hudson'],
                 'nc09': ['nc09',
                          'nc-09',
                          '#nc09',
                          '#nc-09',
                          '#nc9',
                          'mc 09',
                          'mccreadyfornc',
                          'markharrisnc9',
                          'north carolina',
                          'mccready',
                          'harris'],
                 'nc13': ['nc13',
                          'nc-13',
                          '#nc13',
                          '#nc-13',
                          'nc 13',
                          'kathymanningnc',
                          'buddforcongress',
                          'north carolina',
                          'manning',
                          'budd'],
                 'ne02': ['ne02',
                          'ne-02',
                          '#ne02',
                          '#ne-02',
                          '#ne2',
                          'ne 02',
                          'clint4congress',
                          'markamodeinv2',
                          'nevada',
                          'koble',
                          'amodei'],
                 'nh01': ['nh01',
                          'nh-01',
                          '#nh01',
                          '#nh-01',
                          '#nh1',
                          'nh 01',
                          'chrispappasnh',
                          'eddieedwardsnh',
                          'new hampshire',
                          'pappas',
                          'edwards'],
                 'nh02': ['nh02',
                          'nh-02',
                          '#nh02',
                          '#nh-02',
                          '#nh2',
                          'nh 02',
                          'annmclanekuster',
                          'annmclanekuster',
                          'new hampshire',
                          'negron',
                          'kuster'],
                 'nj02': ['nj02',
                          'nj-02',
                          '#nj02',
                          '#nj-02',
                          '#nj2',
                          'nj 02',
                          'vandrewfornj',
                          'grossman4nj',
                          'new jersey',
                          'van drew',
                          'grossman'],
                 'nj03': ['nj03',
                          'nj-03',
                          '#nj03',
                          '#nj-03',
                          '#nj3',
                          'nj 03',
                          'andykimnj',
                          'tmac4congress',
                          'new jersey',
                          'kim',
                          'macarthur'],
                 'nj05': ['nj05',
                          'nj-05',
                          '#nj05',
                          '#nj-05',
                          '#nj5',
                          'nj 05',
                          'joshgottheimer',
                          'realjohnmccann',
                          'new jersey',
                          'gottheimer',
                          'mccann'],
                 'nj07': ['nj07',
                          'nj-07',
                          '#nj07',
                          '#nj-07',
                          '#nj7',
                          'nj 07',
                          'malinowski',
                          'leonardlancenj7',
                          'new jersey',
                          'malinowski',
                          'lance'],
                 'nj11': ['nj11',
                          'nj-11',
                          '#nj11',
                          '#nj-11',
                          'nj 11',
                          'mikiesherrill',
                          'jaywebbernj',
                          'new jersey',
                          'sherrill',
                          'webber'],
                 'nm02': ['nm02',
                          'nm-02',
                          '#nm02',
                          '#nm-02',
                          '#nm2',
                          'nm 02',
                          'xochforcongress',
                          'yvette4congress',
                          'new mexico',
                          'torres small',
                          'herrell'],
                 'nv03': ['nv03',
                          'nv-03',
                          '#nv03',
                          '#nv-03',
                          '#nv3',
                          'nv 03',
                          'susieleenv',
                          'dannytarkanian',
                          'nevada',
                          'lee',
                          'tarkanian'],
                 'nv04': ['nv04',
                          'nv-04',
                          '#nv04',
                          '#nv-04',
                          '#nv4',
                          'nv 04',
                          'stevenhorsford',
                          'cresenthardy',
                          'nevada',
                          'horsford',
                          'hardy'],
                 'ny01': ['ny01',
                          'ny-01',
                          '#ny01',
                          '#ny-01',
                          '#ny1',
                          'ny 01',
                          'perrygershon',
                          'leezeldin',
                          'new york',
                          'gershon',
                          'zeldin'],
                 'ny11': ['ny11',
                          'ny-11',
                          '#ny11',
                          '#ny-11',
                          'ny 11',
                          'maxrose4ny',
                          'dandonovan_ny',
                          'new york',
                          'rose',
                          'donovan'],
                 'ny19': ['ny19',
                          'ny-19',
                          '#ny19',
                          '#ny-19',
                          'ny 19',
                          'delgadoforny19',
                          'johnfasony',
                          'new york',
                          'delgado',
                          'faso'],
                 'ny21': ['ny21',
                          'ny-21',
                          '#ny21',
                          '#ny-21',
                          'ny 21',
                          'tedracobb',
                          'claudiatenney',
                          'new york',
                          'cobb',
                          'stefanik'],
                 'ny22': ['ny22',
                          'ny-22',
                          '#ny22',
                          '#ny-22',
                          'ny 22',
                          'abrindisiny',
                          'elisestefanik',
                          'new york',
                          'brindisi',
                          'tenney'],
                 'ny24': ['ny24',
                          'ny-24',
                          '#ny24',
                          '#ny-24',
                          'ny 24',
                          'dana_balter',
                          'repjohnkatko',
                          'new york',
                          'balter',
                          'katko'],
                 'ny25': ['ny25',
                          'ny-25',
                          '#ny25',
                          '#ny-25',
                          'ny 25',
                          'votemorelle',
                          'drjimmaxwell',
                          'new york',
                          'morelle',
                          'maxwell'],
                 'ny27': ['ny27',
                          'ny-27',
                          '#ny27',
                          '#ny-27',
                          'ny 27',
                          'nate_mcmurray',
                          'collinsny27',
                          'new york',
                          'mcmurray',
                          'collins'],
                 'oh01': ['oh01',
                          'oh-01',
                          '#oh01',
                          '#oh-01',
                          '#oh1',
                          'oh 01',
                          'aftabpureval',
                          'stevechabot',
                          'ohio',
                          'pureval',
                          'chabot'],
                 'oh10': ['oh10',
                          'oh-10',
                          '#oh10',
                          '#oh-10',
                          'oh 10',
                          'gasperforoh10',
                          'miketurneroh',
                          'ohio',
                          'gasper',
                          'turner'],
                 'oh12': ['oh12',
                          'oh-12',
                          '#oh12',
                          '#oh-12',
                          'oh 12',
                          'dannyoconnor1',
                          'troy_balderson',
                          'ohio',
                          'gasper',
                          'balderson'],
                 'oh14': ['oh14',
                          'oh-14',
                          '#oh14',
                          '#oh-14',
                          'oh 14',
                          'betsyraderoh',
                          'davejoyceoh14',
                          'ohio',
                          'rader',
                          'joyce'],
                 'oh15': ['oh15',
                          'oh-15',
                          '#oh15',
                          '#oh-15',
                          'oh 15',
                          'rick_neal',
                          'stevestivers',
                          'ohio',
                          'neal',
                          'stivers'],
                 'pa01': ['pa01',
                          'pa-01',
                          '#pa01',
                          '#pa-01',
                          '#pa1',
                          'pa 01',
                          'scottwallacepa',
                          'brianfitzusa',
                          'pennsylvania',
                          'wallace',
                          'fitzpatrick'],
                 'pa05': ['pa05',
                          'pa-05',
                          '#pa05',
                          '#pa-05',
                          '#pa5',
                          'pa 05',
                          'marygayscanlon',
                          'pearlkimpa',
                          'pennsylvania',
                          'scanlon',
                          'kim'],
                 'pa06': ['pa06',
                          'pa-06',
                          '#pa06',
                          '#pa-06',
                          '#pa6',
                          'pa 06',
                          'houlahanforpa',
                          'mccauley4pa',
                          'pennsylvania',
                          'houlahan',
                          'mccauley'],
                 'pa07': ['pa07',
                          'pa-07',
                          '#pa07',
                          '#pa-07',
                          '#pa7',
                          'pa 07',
                          'wildforcongress',
                          'marty_nothstein',
                          'pennsylvania',
                          'wild',
                          'nothstein'],
                 'pa08': ['pa08',
                          'pa-08',
                          '#pa08',
                          '#pa-08',
                          '#pa8',
                          'pa 08',
                          'cartwrightpa',
                          'johnchrin',
                          'pennsylvania',
                          'cartwright',
                          'chrin'],
                 'pa10': ['pa10',
                          'pa-10',
                          '#pa10',
                          '#pa-10',
                          'pa 10',
                          'gscott4congress',
                          'repscottperry',
                          'pennsylvania',
                          'scott',
                          'perry'],
                 'pa14': ['pa14',
                          'pa-14',
                          '#pa14',
                          '#pa-14',
                          'pa 14',
                          'boerio4congress',
                          'reschenthaler',
                          'pennsylvania',
                          'boerio',
                          'reschenthaler'],
                 'pa16': ['pa16',
                          'pa-16',
                          '#pa16',
                          '#pa-16',
                          'pa 16',
                          'ron_dinicola',
                          'mikekellyforpa',
                          'pennsylvania',
                          'dinicola',
                          'kelly'],
                 'pa17': ['pa17',
                          'pa-17',
                          '#pa17',
                          '#pa-17',
                          'pa 17',
                          'conorlambpa',
                          'keithrothfus',
                          'pennsylvania',
                          'lamb',
                          'rothfus'],
                 'sc01': ['sc01',
                          'sc-01',
                          '#sc01',
                          '#sc-01',
                          '#sc1',
                          'sc 01',
                          'joecunninghamsc',
                          'karringtonsc',
                          'south carolina',
                          'cunningham',
                          'arrington'],
                 'sc05': ['sc05',
                          'sc-05',
                          '#sc05',
                          '#sc-05',
                          '#sc5',
                          'sc 05',
                          'archie4congress',
                          'ralphnorman',
                          'south carolina',
                          'parnell',
                          'norman'],
                 'tx07': ['tx07',
                          'tx-07',
                          '#tx07',
                          '#tx-07',
                          '#tx7',
                          'tx 07',
                          'lizzieforcongress',
                          'johnculberson',
                          'texas',
                          'fletcher',
                          'culberson'],
                 'tx21': ['tx21',
                          'tx-21',
                          '#tx21',
                          '#tx-21',
                          'tx 21',
                          'josephkopser',
                          'chiproytx',
                          'texas',
                          'kopser',
                          'roy'],
                 'tx23': ['tx23',
                          'tx-23',
                          '#tx23',
                          '#tx-23',
                          'tx 23',
                          'ginaortizjones',
                          'willhurd',
                          'texas',
                          'ortiz jones',
                          'hurd'],
                 'tx31': ['tx31',
                          'tx-31',
                          '#tx31',
                          '#tx-31',
                          'tx 31',
                          'mjhegar',
                          'judgejohncarter',
                          'texas',
                          'hegar',
                          'carter'],
                 'tx32': ['tx32',
                          'tx-32',
                          '#tx32',
                          '#tx-32',
                          'tx 32',
                          'colinallredtx',
                          'sessionsfortx32',
                          'texas',
                          'allred',
                          'sessions'],
                 'ut04': ['ut04',
                          'ut-04',
                          '#ut04',
                          '#ut-04',
                          '#ut4',
                          'ut 04',
                          'benmcadams',
                          'miablove',
                          'utah',
                          'mcadams',
                          'love'],
                 'va02': ['va02',
                          'va-02',
                          '#va02',
                          '#va-02',
                          '#va2',
                          'va 02',
                          'elaineluriava',
                          'scotttaylorva',
                          'virginia',
                          'luria',
                          'taylor'],
                 'va05': ['va05',
                          'va-05',
                          '#va05',
                          '#va-05',
                          '#va5',
                          'va 05',
                          'teamcockburn',
                          'denver4va',
                          'virginia',
                          'cockburn',
                          'riggleman'],
                 'va07': ['va07',
                          'va-07',
                          '#va07',
                          '#va-07',
                          '#va7',
                          'va 07',
                          'spanbergerva07',
                          'davebratva7th',
                          'virginia',
                          'spanberger',
                          'brat'],
                 'va10': ['va10',
                          'va-10',
                          '#va10',
                          '#va-10',
                          'va 10',
                          'jenniferwexton',
                          'barbaracomstock',
                          'virginia',
                          'wexton',
                          'comstock'],
                 'wa03': ['wa03',
                          'wa-03',
                          '#wa03',
                          '#wa-03',
                          '#wa3',
                          'wa 03',
                          'electlong',
                          'herrerabeutler',
                          'washington',
                          'long',
                          'beutler'],
                 'wa05': ['wa05',
                          'wa-05',
                          '#wa05',
                          '#wa-05',
                          '#wa5',
                          'wa 05',
                          'lisa4congress',
                          'teamcmr',
                          'washington',
                          'brown',
                          'rodgers'],
                 'wa08': ['wa08',
                          'wa-08',
                          '#wa08',
                          '#wa-08',
                          '#wa8',
                          'wa 08',
                          'drkimschrier',
                          'dinorossiwa',
                          'washington',
                          'schrier',
                          'reichert'],
                 'wi01': ['wi01',
                          'wi-01',
                          '#wi01',
                          '#wi-01',
                          '#wi1',
                          'wi 01',
                          'ironstache',
                          'bryansteilforwi',
                          'wisconsin',
                          'bryce',
                          'steil'],
                 'wi03': ['wi03',
                          'wi-03',
                          '#wi03',
                          '#wi-03',
                          '#wi3',
                          'wi 03',
                          'toftforcongress',
                          'kindforcongress',
                          'wisconsin',
                          'toft',
                          'kind'],
                 'wi06': ['wi06',
                          'wi-06',
                          '#wi06',
                          '#wi-06',
                          '#wi6',
                          'wi 06',
                          'dankohlwi',
                          'grothmanforwi',
                          'wisconsin',
                          'kohl',
                          'grothman'],
                 'wi07': ['wi07',
                          'wi-07',
                          '#wi07',
                          '#wi-07',
                          '#wi7',
                          'wi 07',
                          'vetfordemocracy',
                          'duffy4wisconsin',
                          'wisconsin',
                          'engebretson',
                          'duffy'],
                 'wv03': ['wv03',
                          'wv-03',
                          '#wv03',
                          '#wv-03',
                          '#wv3',
                          'wv 03',
                          'ojeda4congress',
                          'carolmillerwv',
                          'west virginia',
                          'ojeda',
                          'miller']}

distdict_short_old = {'AZSen': ['azsen', '#azsen', 'az', 'sinema', 'arizona', 'mcsally'],
                 'FLSen': ['flsen', '#flsen', 'fl', 'nelson', 'florida', 'scott'],
                 'INSen': ['insen', '#insen', 'in', 'donnelly', 'indiana', 'braun'],
                 'MISen': ['misen', '#misen', 'mi', 'stabenow', 'michigan', 'james'],
                 'MNSen': ['mnsen', '#mnsen', 'mn', 'smith', 'minnesota', 'housley'],
                 'MOSen': ['mosen', '#mosen', 'mo', 'mccaskill', 'missouri', 'hawley'],
                 'MSSen': ['mssen', '#mssen', 'ms', 'baria', 'mississippi', 'wicker'],
                 'MTSen': ['mtsen', '#mtsen', 'mt', 'tester', 'montana', 'rosendale'],
                 'NDSen': ['ndsen', '#ndsen', 'nd', 'heitkamp', 'north dakota', 'cramer'],
                 'NESen': ['nesen', '#nesen', 'ne', 'raybould', 'nebraska', 'fischer'],
                 'NJSen': ['njsen', '#njsen', 'nj', 'menendez', 'new jersey', 'hugin'],
                 'NVSen': ['nvsen', '#nvsen', 'nv', 'rosen', 'nevada', 'heller'],
                 'OHSen': ['ohsen', '#ohsen', 'oh', 'brown', 'ohio', 'renacci'],
                 'PASen': ['pasen', '#pasen', 'pa', 'casey', 'montana', 'barletta'],
                 'TNSen': ['tnsen', '#tnsen', 'tn', 'bredesen', 'tennessee', 'blackburn'],
                 'TXSen': ['txsen', '#txsen', 'tx', 'o’rourke', 'texas', 'cruz'],
                 'WISen': ['wisen', '#wisen', 'wi', 'baldwin', 'wisconsin', 'vukmir'],
                 'WVSen': ['wvsen', '#wvsen', 'wv', 'manchin', 'west virginia', 'morrisey'],
                'ar02': ['ar02',
                          'ar-02',
                          '#ar02',
                          '#ar-02',
                          '#ar2',
                          'ar 02',
                          'clarketucker',
                          'wendyrogersaz'],
                 'az01': ['az01',
                          'az-01',
                          '#az01',
                          '#az-01',
                          '#az1',
                          'az 01',
                          'tomohalleran',
                          'leapeterson'],
                 'az02': ['az02',
                          'az-02',
                          '#az02',
                          '#az-02',
                          '#az2',
                          'az 02',
                          'ann_kirkpatrick',
                          'davidschweikert'],
                 'az06': ['az06',
                          'az-06',
                          '#az06',
                          '#az-06',
                          '#az6',
                          'az 06',
                          'anitamalik',
                          'steveferraramd'],
                 'az09': ['az09',
                          'az-09',
                          '#az09',
                          '#az-09',
                          '#az9',
                          'az 09',
                          'mayorstanton',
                          'electfrench'],
                 'ca04': ['ca04',
                          'ca-04',
                          '#ca04',
                          '#ca-04',
                          '#ca4',
                          'ca 04',
                          'morse4america',
                          'tommcclintock'],
                 'ca07': ['ca07',
                          'ca-07',
                          '#ca07',
                          '#ca-07',
                          '#ca7',
                          'ca 07',
                          'beraforcongress',
                          'andrewfgrant'],
                 'ca10': ['ca10',
                          'ca-10',
                          '#ca10',
                          '#ca-10',
                          'ca 10',
                          'joshua_harder',
                          'jeffdenham'],
                 'ca21': ['ca21',
                          'ca-21',
                          '#ca21',
                          '#ca-21',
                          'ca 21',
                          'tjcoxcongress',
                          'dgvaladao'],
                 'ca25': ['ca25',
                          'ca-25',
                          '#ca25',
                          '#ca-25',
                          'ca 25',
                          'katiehill4ca',
                          'teamknight25'],
                 'ca39': ['ca39',
                          'ca-39',
                          '#ca39',
                          '#ca-39',
                          'ca 39',
                          'gilcisnerosca',
                          'youngkimcd39'],
                 'ca45': ['ca45',
                          'ca-45',
                          '#ca45',
                          '#ca-45',
                          'ca 45',
                          'katieporteroc',
                          'mimiwaltersca'],
                 'ca48': ['ca48',
                          'ca-48',
                          '#ca48',
                          '#ca-48',
                          'ca 48',
                          'harleyrouda',
                          'danarohrabacher'],
                 'ca49': ['ca49',
                          'ca-49',
                          '#ca49',
                          '#ca-49',
                          'ca 49',
                          'mikelevinca \u200f',
                          'diane_harkey'],
                 'ca50': ['ca50',
                          'ca-50',
                          '#ca50',
                          '#ca-50',
                          'ca 50',
                          'acampanajjar',
                          'rep_hunter'],
                 'co03': ['co03',
                          'co-03',
                          '#co03',
                          '#co-03',
                          '#co3',
                          'co 03',
                          'repdmb',
                          'scottrtipton'],
                 'co06': ['co06',
                          'co-06',
                          '#co06',
                          '#co-06',
                          '#co6',
                          'co 06',
                          'jasoncrowco6',
                          'coffmanforco'],
                 'ct05': ['ct05',
                          'ct-05',
                          '#ct05',
                          '#ct-05',
                          '#ct5',
                          'ct 05',
                          'jahanahayes',
                          'santos4congress'],
                 'fl06': ['fl06',
                          'fl-06',
                          '#fl06',
                          '#fl-06',
                          '#fl6',
                          'fl 06',
                          'nancysoderberg',
                          'michaelgwaltz'],
                 'fl07': ['fl07',
                          'fl-07',
                          '#fl07',
                          '#fl-07',
                          '#fl7',
                          'fl 07',
                          'smurphycongress',
                          'mike_miller_fl'],
                 'fl15': ['fl15',
                          'fl-15',
                          '#fl15',
                          '#fl-15',
                          'fl 15',
                          'kristenforfl',
                          'rossspano'],
                 'fl16': ['fl16',
                          'fl-16',
                          '#fl16',
                          '#fl-16',
                          'fl 16',
                          'vern2014',
                          'shapiro4fl16'],
                 'fl18': ['fl18',
                          'fl-18',
                          '#fl18',
                          '#fl-18',
                          'fl 18',
                          'laurenbaer',
                          'brianmastfl'],
                 'fl25': ['fl25',
                          'fl-25',
                          '#fl25',
                          '#fl-25',
                          'fl 25',
                          'mbfforcongress',
                          'mariodb'],
                 'fl26': ['fl26',
                          'fl-26',
                          '#fl26',
                          '#fl-26',
                          'fl 26',
                          'debbieforfl',
                          'carloslcurbelo'],
                 'fl27': ['fl27',
                          'fl-27',
                          '#fl27',
                          '#fl-27',
                          'fl 27',
                          'donnashalala',
                          'maelvirasalazar'],
                 'ga06': ['ga06',
                          'ga-06',
                          '#ga06',
                          '#ga-06',
                          '#ga6',
                          'ga 06',
                          'lucywins2018',
                          'karenhandel'],
                 'ga07': ['ga07',
                          'ga-07',
                          '#ga07',
                          '#ga-07',
                          '#ga7',
                          'ga 07',
                          'carolyn4ga7',
                          'reprobwoodall'],
                 'ia01': ['ia01',
                          'ia-01',
                          '#ia01',
                          '#ia-01',
                          '#ia1',
                          'ia 01',
                          'abby4iowa',
                          'rodblum'],
                 'ia03': ['ia03',
                          'ia-03',
                          '#ia03',
                          '#ia-03',
                          '#ia3',
                          'ia 03',
                          'axne4congress',
                          'youngforiowa'],
                 'il06': ['il06',
                          'il-06',
                          '#il06',
                          '#il-06',
                          '#il6',
                          'il 06',
                          'seancasten',
                          'teamroskam'],
                 'il12': ['il12',
                          'il-12',
                          '#il12',
                          '#il-12',
                          'il 12',
                          'kelly4southrnil',
                          'bostforcongress'],
                 'il13': ['il13',
                          'il-13',
                          '#il13',
                          '#il-13',
                          'il 13',
                          'betsyforil',
                          'electrodney'],
                 'il14': ['il14',
                          'il-14',
                          '#il14',
                          '#il-14',
                          'il 14',
                          'lunderwood630',
                          'randyhultgren'],
                 'in02': ['in02',
                          'in-02',
                          '#in02',
                          '#in-02',
                          '#in2',
                          'in 02',
                          'melforcongress',
                          'jackiewalorski'],
                 'ks02': ['ks02',
                          'ks-02',
                          '#ks02',
                          '#ks-02',
                          'ks 02',
                          'pauldavisks',
                          'steve4kansas'],
                 'ks03': ['ks03',
                          'ks-03',
                          '#ks03',
                          '#ks-03',
                          'ks 03',
                          'sharicedavids',
                          'kevinyoder'],
                 'ky06': ['ky06',
                          'ky-06',
                          '#ky06',
                          '#ky-06',
                          '#ky6',
                          'ky 06',
                          'amymcgrathky',
                          'barrforcongress'],
                 'me02': ['me02',
                          'me-02',
                          '#me02',
                          '#me-02',
                          '#me2',
                          'me 02',
                          'golden4congress',
                          'brucepoliquin'],
                 'mi01': ['mi01',
                          'mi-01',
                          '#mi01',
                          '#mi-01',
                          '#mi1',
                          'mi 01',
                          'morganformi',
                          'jackbergman_mi1'],
                 'mi03': ['mi03',
                          'mi-03',
                          '#mi03',
                          '#mi-03',
                          '#mi3',
                          'mi 03',
                          'cathy albro',
                          'justinamash'],
                 'mi06': ['mi06',
                          'mi-06',
                          '#mi06',
                          '#mi-06',
                          'mi 06',
                          'mattlongjohn',
                          'uptonforallofus'],
                 'mi07': ['mi07',
                          'mi-07',
                          '#mi07',
                          '#mi-07',
                          '#mi7',
                          'mi 07',
                          'gdriskell',
                          'teamwalberg'],
                 'mi08': ['mi08',
                          'mi-08',
                          '#mi08',
                          '#mi-08',
                          'mi 08',
                          'elissaslotkin',
                          'electmikebishop'],
                 'mi11': ['mi11',
                          'mi-11',
                          '#mi11',
                          '#mi-11',
                          'mi 11',
                          'haleylive',
                          'lenaepstein'],
                 'mn01': ['mn01',
                          'mn-01',
                          '#mn01',
                          '#mn-01',
                          '#mn1',
                          'mn 01',
                          'danielfeehan',
                          'jimhagedornmn'],
                 'mn02': ['mn02',
                          'mn-02',
                          '#mn02',
                          '#mn-02',
                          '#mn2',
                          'mn 02',
                          'angiecraigmn',
                          'jason2cd'],
                 'mn03': ['mn03',
                          'mn-03',
                          '#mn03',
                          '#mn-03',
                          '#mn3',
                          'mn 03',
                          'deanbphillips',
                          'erik_paulsen'],
                 'mn07': ['mn07',
                          'mn-07',
                          '#mn07',
                          '#mn-07',
                          '#mn7',
                          'mn 07',
                          'collinpeterson',
                          'dhughescongress'],
                 'mn08': ['mn08',
                          'mn-08',
                          '#mn08',
                          '#mn-08',
                          '#mn8',
                          'mn 08',
                          'joeradinovich',
                          'petestauber'],
                 'mo02': ['mo02',
                          'mo-02',
                          '#mo02',
                          '#mo-02',
                          '#mo2',
                          'mo 02',
                          'cortvo',
                          'annlwagner'],
                 'mt00': ['mt00', 'mt-00', '#mt00', '#mt-00', 'mt 00'],
                 'mtAL': ['mtal',
                          'mt-al',
                          '#mtal',
                          '#mt-al',
                          'mt al',
                          'williamsformt',
                          'gregformontana'],
                 'nc02': ['nc02',
                          'nc-02',
                          '#nc02',
                          '#nc-02',
                          '#nc2',
                          'nc 02',
                          'lindafornc',
                          'georgeholding'],
                 'nc08': ['nc08',
                          'nc-08',
                          '#nc08',
                          '#nc-08',
                          '#nc8',
                          'nc 08',
                          'frank4nc',
                          'richhudson'],
                 'nc09': ['nc09',
                          'nc-09',
                          '#nc09',
                          '#nc-09',
                          '#nc9',
                          'mc 09',
                          'mccreadyfornc',
                          'markharrisnc9'],
                 'nc13': ['nc13',
                          'nc-13',
                          '#nc13',
                          '#nc-13',
                          'nc 13',
                          'kathymanningnc',
                          'buddforcongress'],
                 'ne02': ['ne02',
                          'ne-02',
                          '#ne02',
                          '#ne-02',
                          '#ne2',
                          'ne 02',
                          'clint4congress',
                          'markamodeinv2'],
                 'nh01': ['nh01',
                          'nh-01',
                          '#nh01',
                          '#nh-01',
                          '#nh1',
                          'nh 01',
                          'chrispappasnh',
                          'eddieedwardsnh'],
                 'nh02': ['nh02',
                          'nh-02',
                          '#nh02',
                          '#nh-02',
                          '#nh2',
                          'nh 02',
                          'annmclanekuster',
                          'annmclanekuster'],
                 'nj02': ['nj02',
                          'nj-02',
                          '#nj02',
                          '#nj-02',
                          '#nj2',
                          'nj 02',
                          'vandrewfornj',
                          'grossman4nj'],
                 'nj03': ['nj03',
                          'nj-03',
                          '#nj03',
                          '#nj-03',
                          '#nj3',
                          'nj 03',
                          'andykimnj',
                          'tmac4congress'],
                 'nj05': ['nj05',
                          'nj-05',
                          '#nj05',
                          '#nj-05',
                          '#nj5',
                          'nj 05',
                          'joshgottheimer',
                          'realjohnmccann'],
                 'nj07': ['nj07',
                          'nj-07',
                          '#nj07',
                          '#nj-07',
                          '#nj7',
                          'nj 07',
                          'malinowski',
                          'leonardlancenj7'],
                 'nj11': ['nj11',
                          'nj-11',
                          '#nj11',
                          '#nj-11',
                          'nj 11',
                          'mikiesherrill',
                          'jaywebbernj'],
                 'nm02': ['nm02',
                          'nm-02',
                          '#nm02',
                          '#nm-02',
                          '#nm2',
                          'nm 02',
                          'xochforcongress',
                          'yvette4congress'],
                 'nv03': ['nv03',
                          'nv-03',
                          '#nv03',
                          '#nv-03',
                          '#nv3',
                          'nv 03',
                          'susieleenv',
                          'dannytarkanian'],
                 'nv04': ['nv04',
                          'nv-04',
                          '#nv04',
                          '#nv-04',
                          '#nv4',
                          'nv 04',
                          'stevenhorsford',
                          'cresenthardy'],
                 'ny01': ['ny01',
                          'ny-01',
                          '#ny01',
                          '#ny-01',
                          '#ny1',
                          'ny 01',
                          'perrygershon',
                          'leezeldin'],
                 'ny11': ['ny11',
                          'ny-11',
                          '#ny11',
                          '#ny-11',
                          'ny 11',
                          'maxrose4ny',
                          'dandonovan_ny'],
                 'ny19': ['ny19',
                          'ny-19',
                          '#ny19',
                          '#ny-19',
                          'ny 19',
                          'delgadoforny19',
                          'johnfasony'],
                 'ny21': ['ny21',
                          'ny-21',
                          '#ny21',
                          '#ny-21',
                          'ny 21',
                          'tedracobb',
                          'claudiatenney'],
                 'ny22': ['ny22',
                          'ny-22',
                          '#ny22',
                          '#ny-22',
                          'ny 22',
                          'abrindisiny',
                          'elisestefanik'],
                 'ny24': ['ny24',
                          'ny-24',
                          '#ny24',
                          '#ny-24',
                          'ny 24',
                          'dana_balter',
                          'repjohnkatko'],
                 'ny25': ['ny25',
                          'ny-25',
                          '#ny25',
                          '#ny-25',
                          'ny 25',
                          'votemorelle',
                          'drjimmaxwell'],
                 'ny27': ['ny27',
                          'ny-27',
                          '#ny27',
                          '#ny-27',
                          'ny 27',
                          'nate_mcmurray',
                          'collinsny27'],
                 'oh01': ['oh01',
                          'oh-01',
                          '#oh01',
                          '#oh-01',
                          '#oh1',
                          'oh 01',
                          'aftabpureval',
                          'stevechabot'],
                 'oh10': ['oh10',
                          'oh-10',
                          '#oh10',
                          '#oh-10',
                          'oh 10',
                          'gasperforoh10',
                          'miketurneroh'],
                 'oh12': ['oh12',
                          'oh-12',
                          '#oh12',
                          '#oh-12',
                          'oh 12',
                          'dannyoconnor1',
                          'troy_balderson'],
                 'oh14': ['oh14',
                          'oh-14',
                          '#oh14',
                          '#oh-14',
                          'oh 14',
                          'betsyraderoh',
                          'davejoyceoh14'],
                 'oh15': ['oh15',
                          'oh-15',
                          '#oh15',
                          '#oh-15',
                          'oh 15',
                          'rick_neal',
                          'stevestivers'],
                 'pa01': ['pa01',
                          'pa-01',
                          '#pa01',
                          '#pa-01',
                          '#pa1',
                          'pa 01',
                          'scottwallacepa',
                          'brianfitzusa'],
                 'pa05': ['pa05',
                          'pa-05',
                          '#pa05',
                          '#pa-05',
                          '#pa5',
                          'pa 05',
                          'marygayscanlon',
                          'pearlkimpa'],
                 'pa06': ['pa06',
                          'pa-06',
                          '#pa06',
                          '#pa-06',
                          '#pa6',
                          'pa 06',
                          'houlahanforpa',
                          'mccauley4pa'],
                 'pa07': ['pa07',
                          'pa-07',
                          '#pa07',
                          '#pa-07',
                          '#pa7',
                          'pa 07',
                          'wildforcongress',
                          'marty_nothstein'],
                 'pa08': ['pa08',
                          'pa-08',
                          '#pa08',
                          '#pa-08',
                          '#pa8',
                          'pa 08',
                          'cartwrightpa',
                          'johnchrin'],
                 'pa10': ['pa10',
                          'pa-10',
                          '#pa10',
                          '#pa-10',
                          'pa 10',
                          'gscott4congress',
                          'repscottperry'],
                 'pa14': ['pa14',
                          'pa-14',
                          '#pa14',
                          '#pa-14',
                          'pa 14',
                          'boerio4congress',
                          'reschenthaler'],
                 'pa16': ['pa16',
                          'pa-16',
                          '#pa16',
                          '#pa-16',
                          'pa 16',
                          'ron_dinicola',
                          'mikekellyforpa'],
                 'pa17': ['pa17',
                          'pa-17',
                          '#pa17',
                          '#pa-17',
                          'pa 17',
                          'conorlambpa',
                          'keithrothfus'],
                 'sc01': ['sc01',
                          'sc-01',
                          '#sc01',
                          '#sc-01',
                          '#sc1',
                          'sc 01',
                          'joecunninghamsc',
                          'karringtonsc'],
                 'sc05': ['sc05',
                          'sc-05',
                          '#sc05',
                          '#sc-05',
                          '#sc5',
                          'sc 05',
                          'archie4congress',
                          'ralphnorman'],
                 'tx07': ['tx07',
                          'tx-07',
                          '#tx07',
                          '#tx-07',
                          '#tx7',
                          'tx 07',
                          'lizzieforcongress',
                          'johnculberson'],
                 'tx21': ['tx21',
                          'tx-21',
                          '#tx21',
                          '#tx-21',
                          'tx 21',
                          'josephkopser',
                          'chiproytx'],
                 'tx23': ['tx23',
                          'tx-23',
                          '#tx23',
                          '#tx-23',
                          'tx 23',
                          'ginaortizjones',
                          'willhurd'],
                 'tx31': ['tx31',
                          'tx-31',
                          '#tx31',
                          '#tx-31',
                          'tx 31',
                          'mjhegar',
                          'judgejohncarter'],
                 'tx32': ['tx32',
                          'tx-32',
                          '#tx32',
                          '#tx-32',
                          'tx 32',
                          'colinallredtx',
                          'sessionsfortx32'],
                 'ut04': ['ut04',
                          'ut-04',
                          '#ut04',
                          '#ut-04',
                          '#ut4',
                          'ut 04',
                          'benmcadams',
                          'miablove'],
                 'va02': ['va02',
                          'va-02',
                          '#va02',
                          '#va-02',
                          '#va2',
                          'va 02',
                          'elaineluriava',
                          'scotttaylorva'],
                 'va05': ['va05',
                          'va-05',
                          '#va05',
                          '#va-05',
                          '#va5',
                          'va 05',
                          'teamcockburn',
                          'denver4va'],
                 'va07': ['va07',
                          'va-07',
                          '#va07',
                          '#va-07',
                          '#va7',
                          'va 07',
                          'spanbergerva07',
                          'davebratva7th'],
                 'va10': ['va10',
                          'va-10',
                          '#va10',
                          '#va-10',
                          'va 10',
                          'jenniferwexton',
                          'barbaracomstock'],
                 'wa03': ['wa03',
                          'wa-03',
                          '#wa03',
                          '#wa-03',
                          '#wa3',
                          'wa 03',
                          'electlong',
                          'herrerabeutler'],
                 'wa05': ['wa05',
                          'wa-05',
                          '#wa05',
                          '#wa-05',
                          '#wa5',
                          'wa 05',
                          'lisa4congress',
                          'teamcmr'],
                 'wa08': ['wa08',
                          'wa-08',
                          '#wa08',
                          '#wa-08',
                          '#wa8',
                          'wa 08',
                          'drkimschrier',
                          'dinorossiwa'],
                 'wi01': ['wi01',
                          'wi-01',
                          '#wi01',
                          '#wi-01',
                          '#wi1',
                          'wi 01',
                          'ironstache',
                          'bryansteilforwi'],
                 'wi03': ['wi03',
                          'wi-03',
                          '#wi03',
                          '#wi-03',
                          '#wi3',
                          'wi 03',
                          'toftforcongress',
                          'kindforcongress'],
                 'wi06': ['wi06',
                          'wi-06',
                          '#wi06',
                          '#wi-06',
                          '#wi6',
                          'wi 06',
                          'dankohlwi',
                          'grothmanforwi'],
                 'wi07': ['wi07',
                          'wi-07',
                          '#wi07',
                          '#wi-07',
                          '#wi7',
                          'wi 07',
                          'vetfordemocracy',
                          'duffy4wisconsin'],
                 'wv03': ['wv03',
                          'wv-03',
                          '#wv03',
                          '#wv-03',
                          '#wv3',
                          'wv 03',
                          'ojeda4congress',
                          'carolmillerwv']}

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


#Write Twitter variables to DB
def write_database(post_id, user_id, text, created_at, created_at_dt, reply_to_user_id,
        reply_to_scrname, reply_to_status_id, retweet_count,
        favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
        original_text, original_tweet_created_at, original_tweet_likes,
        original_author_id, original_author_scrname, polarity,
        polarity_val, tag_list, url_list, user_scrname, user_name,
        user_location, user_created, user_followers, user_friends,
        user_statuses, district_name):

    #print("starting db entry for postid = {}".format(post_id))

    if district_name[3:] == 'Sen':
        district = 'sen'
        dist_type = 2
    else:
        district = district_name[3:]
        dist_type = 1

    #POST TABLE:
    #If tweet ID not already in database, add to Post table

    if db.session.query(Post).filter(Post.post_id == post_id).count() == 0:

        #print('adding post')
        #USER table

        #If User already in User table, update dynamic elements, associate with this post
        this_user = db.session.query(User).filter(User.user_id == user_id).first()
        if this_user != None:
            this_user.user_location = user_location
            this_user.user_followers = user_followers
            this_user.user_friends = user_friends
            this_user.user_statuses = user_statuses
            db.session.add(this_user)

        #Otherise, add User to user table, associate with this post
        else:
            this_user = User(user_id, user_scrname, user_name, user_location,\
            user_created, user_followers, user_friends, user_statuses)
            db.session.add(this_user)

        #POST table

        new_post = Post(post_id, user_id, text, created_at, created_at_dt,
            reply_to_user_id, reply_to_scrname, reply_to_status_id, retweet_count,
            favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
            original_text, original_tweet_created_at, original_tweet_likes,
            original_author_id, original_author_scrname, polarity, polarity_val)

        db.session.add(new_post)

        #If original tweet is in database, update its retweeted count. If not, do nothing
        if original_tweet_id != None:
            orig_tweet = db.session.query(Post).\
            filter(Post.post_id == original_tweet_id).first()
            if orig_tweet != None:
                orig_tweet.retweet_count = original_tweet_retweets
                db.session.add(orig_tweet)

        #HASHTAG TABLE

        # If tweet is being added, iterate through tag/url list, and create a
        # Hashtag/Url table row for each tag
        for item in tag_list:
            #If hashtag is not already in Hashtag table, create new row
            hash_search = db.session.query(Hashtag).\
            filter(Hashtag.hashtag == item).first()
            if hash_search == None:
                new_hashtag = Hashtag(item)
                db.session.add(new_hashtag)
            else:
                new_hashtag = hash_search
            #Add association to posthash_assoc_table
            new_post.hashtags.append(new_hashtag)
            #db.session.add(posthash_assoc.hashtag)

            #add one row to Post_extended per hashtag
            # NOTE: this means number of rows per post_id = cartesian product
            # of hashtags times districts (if picked up in search for every dist)

            new_row = Post_extended(post_id, user_id, created_at, created_at_dt,
                retweet_count, is_retweet, original_tweet_id,
                original_text, original_tweet_created_at,
                original_author_id, original_author_scrname, polarity, polarity_val,
                item, district_name, dist_type, user_scrname)

            db.session.add(new_row)
            #print("added newrow for hash {}".format(item))


        #DISTRICT TABLE
            #capture District_id from 1st query term:
        state = district_name[0:3].lower()
            #Handle Senate districts differently than congressional
        # if query[4:7] == 'Sen':
        #     district = 'sen'
        #     district_name = query[2:7]
        #     dist_type = 2
        # else:
        #     district = query[4:6]
        #     district_name = query[2:6]
        #     dist_type = 1

        #Check if district is in DB, add if not
        district_search = db.session.query(District).\
        filter(District.district_name == district_name).first()

        if district_search == None:
            new_district = District(state, district, district_name, dist_type)
            db.session.add(new_district)
        else:
            new_district = district_search

        #Add association to postdist_assoc_table
        new_post.districts.append(new_district)



        #URL TABLE

        #if URLS exist, add to db
        if len(url_list) > 0:
            for item in url_list:
                url_search = db.session.query(Url).filter(Url.url == item).first()
                if url_search == None:
                    new_url = Url(item)
                    db.session.add(new_url)
                else:
                    new_url = url_search


                #Add association to postDistAssoc_table
            new_post.urls.append(new_url)




        #associate user with post
        this_user.user_posts.append(new_post)

    #If tweet ID in db (from another dist query), add new association to Post table
    else:
        #print('ID there, trying plan B')
        district_check = db.session.query(District.district_name).\
        join(Post.districts).\
        filter(Post.post_id==post_id).all()

        check = 0
        for result in district_check:               #iterate through associated dists
            if result[0] == district_name:
                check = 1
                #print("already there")                          #if find match, check =  1, do nothing
        if check == 0:
            #print("adding newdist")                               # if no match, add to postdist_assoc
            sql_command = '''INSERT INTO postdist_assoc (post_id, district_name)
                            VALUES (post_id, district_name);'''
            conn = db.engine.connect()
            conn.execute(sql_command)
            conn.close()


def add_tweet(tweet_id, district_name=None):

    print("getting missing tweet now, buster")
    tweet = cred.api.get_status(tweet_id, include_entities=True,
                                tweet_mode="extended")
    print("got the tweet, man")

    #Create variables from JSON data
    #User table variables
    user_id = tweet.user.id_str
    user_scrname = tweet.user.screen_name
    user_name = tweet.user.name
    user_location = tweet.user.location
    user_created = tweet.user.created_at
    user_followers = tweet.user.followers_count
    user_friends = tweet.user.friends_count
    user_statuses = tweet.user.statuses_count


    #Post table variables: always in place
    post_id = tweet.id_str
    text = tweet.full_text
    created_at = tweet.created_at                #NOTE: UTC time
    created_at_dt = tweet.created_at

    #Post table variables: Nullable
    reply_to_user_id = tweet.in_reply_to_user_id_str
    reply_to_scrname = tweet.in_reply_to_screen_name
    reply_to_status_id = tweet.in_reply_to_status_id_str
    retweet_count = tweet.retweet_count


    favorite_count = tweet.favorite_count

    #Retweet status variables: from "retweeted status: Tweet object
    #TAGS/URLS included here, because may only be included in retweeted status entities

    tag_list = []
    url_list = []

    print("next on to retweeted status")

    try:
        if tweet.retweeted_status:
            is_retweet = True
            original_tweet_id = tweet.retweeted_status.id_str
            original_tweet_retweets = tweet.retweeted_status.retweet_count
            original_text = tweet.retweeted_status.full_text

            original_tweet_created_at = tweet.retweeted_status.created_at
            original_tweet_likes = tweet.retweeted_status.favorite_count
            original_author_id = tweet.retweeted_status.user.id_str
            original_author_scrname = tweet.retweeted_status.user.screen_name

        #Get full list of hashtags in retweeted entities
            for dict in tweet.retweeted_status.entities['hashtags']:
                tag_list.append(dict['text'].lower())
        #Get full list of urls in retweeted entities
            for dict in tweet.retweeted_status.entities['urls']:
                url_list.append(dict['expanded_url'])
    except AttributeError as ae:
        # print("Error raised: {0}".format(ae))
        is_retweet = False
        original_tweet_id = None
        original_tweet_retweets = None
        original_text = None
        original_tweet_created_at = None
        original_tweet_likes = None
        original_author_id = None
        original_author_scrname = None

    #Get simple list of hashtags in top-level (non-RT) tweet
        for hashtag in tweet.entities["hashtags"]:
            tag_list.append(hashtag["text"].lower())
    #Get simple list of urls in top-level (non-RT) tweet
        for link in tweet.entities["urls"]:
            url_list.append(link['expanded_url'])




    print("trying this distlist thing")

    if district_name == None:
        for key, word_list in distdict_short.items():
            for keyword in word_list:
                if keyword in text:
                    district_name = key
                    break
            if district_name != None:
                break
    if district_name == None:
        return False

    print("the district name is {}".format(district_name))




    # #Use local relevance filter *if not Senate*
    # #NOTE: if this creates garbages in Senate, figure out better filter
    #
    #
    # if query[4:7] != 'Sen':
    #     district_name = query[2:6]
    #
    #
    #     # Check Tweet text for district name to filter out irrelvancies;
    #     # skip rest of for loop if district name (or aliases) not found
    #
    #     check = False
    #
    #     for district_alias in distdict_short[district_name]:
    #         if original_text:
    #             if district_alias in original_text.lower():
    #                 check = True
    #         else:
    #             if district_alias in text.lower():
    #                 check = True
    #     if check == False:
    #         # print("Tweet rejected, no district reference")
    #         continue


    #TextBlob analysis of tweet sentiment
    analysis = TextBlob(tweet.full_text)
    polarity = analysis.sentiment.polarity
    # print(polarity)

    if polarity > 0:
        polarity_val = 'positive'
    elif polarity < 0:
        polarity_val = 'negative'
    else:
        polarity_val = 'neutral'

    print("thought i'd maybe try putting it in the database, hon")

    try:
        write_database(post_id, user_id, text, created_at,
                created_at_dt, reply_to_user_id,
                reply_to_scrname, reply_to_status_id, retweet_count,
                favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
                original_text, original_tweet_created_at, original_tweet_likes,
                original_author_id, original_author_scrname, polarity,
                polarity_val, tag_list, url_list, user_scrname, user_name,
                user_location, user_created, user_followers, user_friends,
                user_statuses, district_name)

        print("baby, it's in there")


    except exc.SQLAlchemyError as e:
        print("There's a dadgummed database write error for post ID {0}: {1}".\
        format(post_id, e))
        print("It's currently {}".format(datetime.datetime.now()))

        with open('logs/twitterscrape_passed.txt', 'a') as pw:
            pw.write('{}\n'.format(post_id))

        db.session.rollback()

        pass
    return True

def cache_top_hashtags():

    str_time_range = stringtime(14)

    top_hash_list = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.hashtags).\
    filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).\
    order_by(func.count(Hashtag.hashtag).desc()).all()


    time_list = [1, 2, 7, 14]
    url_header = {"secret-header": "True"}

    print(top_hash_list[0:10])
    for result in top_hash_list[0:40]:
        for figure in time_list:
            url_visit = 'https://pollchatter.org/hashtag/{0}?time_delta={1}'.\
                    format(result[0], figure)
            req = urllib.request.Request(url_visit, headers = url_header)
            print(url_visit)
            print(req.header_items())
            page = urllib.request.urlopen(req)
            print("got url for time_delta={}".format(figure))
            print(page.info().as_string())

def cache_overviews():


    group_list = ['allcong', 'allsen', 'allraces']
    time_list = [1, 2, 7, 14]
    url_header = {"secret-header": "True"}

    for group in group_list:
        for figure in time_list:

            url_visit = 'https://pollchatter.org/overview/{0}?time_delta={1}'.\
                format(group, figure)
            req = urllib.request.Request(url_visit, headers = url_header)
            print(req.header_items())
            page = urllib.request.urlopen(req)
            print("got url for {0}, time_delta={1}".format(group, figure))
            print(page.info().as_string())

def cache_botspy():

    time_list = [1, 2, 7, 14]
    url_header = {"secret-header": "True"}

    for figure in time_list:

        url_visit = 'https://pollchatter.org/botspy/allbots?time_delta={}'.\
            format(figure)
        req = urllib.request.Request(url_visit, headers = url_header)
        print(req.header_items())
        page = urllib.request.urlopen(req)
        print("got url for botspy time_delta={}".format(figure))
        print(page.info().as_string())




def cache_dists():

    time_list = [1, 2, 7, 14]
    url_header = {"secret-header": "True"}

    for figure in time_list:
        # get senate districts
        with open('app/comp_races_parsed_sen.csv', 'r') as f:
            reader = csv.reader(f)

            for row in reader:
                #Create search query with quotation marks, to limit to exact matches
                query = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                    '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"' + ' OR ' + \
                    '"'+row[4]+'"' + ' OR ' + '"'+row[5]+'"'

                url_visit = 'https://pollchatter.org/district/{0}?time_delta={1}'.\
                        format(query[2:7], figure)
                req = urllib.request.Request(url_visit, headers = url_header)
                print(req.header_items())
                page = urllib.request.urlopen(req)
                print("got url for time_delta={}".format(figure))
                print(page.info().as_string())

        # Get cong districts
        with open('app/comp_races_parsed.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                #Create search query with quotation marks, to limit to exact matches
                if row[4] != "":
                    query = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                    '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"' + ' OR ' + '"'+row[4]+'"'
                else:
                    query = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                    '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"'

                url_visit = 'https://pollchatter.org/district/{0}?time_delta={1}'.\
                        format(query[2:6], figure)
                req = urllib.request.Request(url_visit, headers = url_header)
                print(req.header_items())
                page = urllib.request.urlopen(req)
                print("got url for time_delta={}".format(figure))
                print(page.info().as_string())
