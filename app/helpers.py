from app import app, db
from datetime import datetime, timedelta
import json
import requests
from app.models import User, Post, District, Hashtag, Url

def stringtime(time_delta):
    if time_delta == None:
        time_delta = "7"
    time_range = datetime.now() - timedelta(days=int(time_delta))
    str_time_range = time_range.strftime('%Y-%m-%d %H:%M:%S')
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

def get_tweet_list(db_search_object):

    # produce list of [post_id, original screen name, retweet count, original_tweet_id,
    # orig_tweet_html]
    #

    most_retweeted_tweets = db_search_object
    original_tweets = []                 #list of tweets used to avoid repeats
    most_retweeted_tweet_list = []
    count = 0

    for item in most_retweeted_tweets:
        #if the tweet id has been seen, skip
        # print(original_tweets)
        if item[3] in original_tweets or item[0] in original_tweets:
            pass
        else:
            tweet = []
            original_tweets.append(item[0])
            tweet.append(item[0])       #post_id: list [item0]
            if item[1]:                     #if retweet
                tweet.append(item[1])   #original_author_scrname : list item[1]

            else:                           # or if original tweet
                tweet.append(item[4])   #original poster

            tweet.append(item[2])       #retweet count; list item[2]
                #if loop: if tweet_html exists, don't go looking for it
            if item[5]:
                tweet.append(item[5])         #tweet_text: list item[3]
                if item[3]:
                    original_tweets.append(item[3])
                #if no tweet_html, then go to Twitter for the Tweet
            else:
                #if RT (if original_tweet_id exists)
                if item[3]:
                    original_tweets.append(item[3])
                    try:
                        tweet_text = get_tweet(item[3]) #get text of tweet
                        tweet.append(tweet_text)   #tweet_text: list item[3]
                    except:
                        tweet.append("Can't retrieve Tweet")
                #if not RT (no original_tweet_id), use post ID
                else:
                    try:
                        tweet_text = get_tweet(item[0]) #get text of tweet
                        tweet.append(tweet_text)   #tweet_text: list item[3]
                    except:
                        tweet.append("Can't retrieve Tweet")

            #Get botscore for original poster using tweet[1]: either
            #original_author (if RT) or post author (if not RT)
            botscore = db.session.query(User.user_cap_perc).\
            filter(User.user_scrname==tweet[1]).first()

            if botscore:
                tweet.append(botscore[0])           #list item[4]
            else:
                tweet.append("Not yet in database")
            if item[3]:
                tweet.append("ORIGINAL_ID:{}".format(item[3]))
            else:
                tweet.append("ORIGINAL TWEET")
            # print(tweet)
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
    "TheWarrior"
    ]
