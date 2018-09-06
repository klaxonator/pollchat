import os
import csv
import sys
import tweepy
import time
from app.helpers import skip_list, get_tweet, distdict_short
from app import app, db
import fill_overview_tables_timed as fill
import app.graph_functions as gf
import urllib.request

#import preprocessor as p
from textblob import TextBlob
import datetime

#Import all Twitter credentials
import app.tweepy_cred_mf as cred


##Set up database functions
from app.models import User, Post, Hashtag, District, Url, posthash_assoc,\
 posturl_assoc, postdist_assoc, Post_extended
from sqlalchemy import exc, func

#Instantiate SQLalchemy database connection


#Write Twitter variables to DB
def write_database(post_id, user_id, text, created_at, created_at_dt, reply_to_user_id,
        reply_to_scrname, reply_to_status_id, retweet_count,
        favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
        original_text, original_tweet_created_at, original_tweet_likes,
        original_author_id, original_author_scrname, polarity,
        polarity_val, tag_list, url_list, user_scrname, user_name,
        user_location, user_created, user_followers, user_friends,
        user_statuses, query):

    #print("starting db entry for postid = {}".format(post_id))

    if query[4:7] == 'Sen':
        district = 'sen'
        district_name = query[2:7]
        dist_type = 2
    else:
        district = query[4:6]
        district_name = query[2:6]
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
        state = query[2:4].lower()
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

def twitter_search(query):

    # Get district name from query
    if query[4:7] == 'Sen':
        this_district_name = query[2:7]
    else:
        this_district_name = query[2:6]

    max_db_tweet = db.session.query(func.max(Post.post_id)).\
            join(Post.districts).\
            filter(District.district_name==this_district_name).first()

    #Iterate over tweets returned by Tweepy Cursor, with query contained in 'q'

    sinceId = max_db_tweet[0]
    #sinceId = None
    maxTweets = 10000000
    tweetsPerQry = 100
    max_id = -1


    tweetCount = 0      # Number of tweets obtained from Twitter
    indexCount = 0      # Number of tweets added to DB

    # Create manual paging system for tweets. Each new call is 100-tweet page
    # Here will generally always use no sinceID (meaning return all possible tweets)

    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = cred.api.search(q=query, count=tweetsPerQry,
                                                lang='en',
                                                result_type='mixed',
                                                include_entities=True,
                                                tweet_mode="extended")
                    #print("New_tweets length is: {}".format(len(new_tweets)))
                else:
                    new_tweets = cred.api.search(q=query, count=tweetsPerQry,
                                            since_id=sinceId,
                                            lang='en',
                                            include_entities=True,
                                            tweet_mode="extended")
                    #print("New_tweets length is: {}".format(len(new_tweets)))

            else:
                if (not sinceId):
                    new_tweets = cred.api.search(q=query, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            lang='en',
                                            include_entities=True,
                                            tweet_mode="extended")
                    #print("New_tweets length is: {}".format(len(new_tweets)))
                else:
                    new_tweets = cred.api.search(q=query, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId,
                                            lang='en',
                                            include_entities=True,
                                            tweet_mode="extended")
                    #print("New_tweets length is: {}".format(len(new_tweets)))

            if not new_tweets:
                #print("No more tweets found")
                break

            print("This batch has {} tweets".format(len(new_tweets)))
            for tweet in new_tweets:




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

                #Skip write step if tag in known skip list
                for tag in skip_list:
                    if tag in tag_list or original_author_scrname == tag:
                        continue

                #Use local relevance filter *if not Senate*
                #NOTE: if this creates garbages in Senate, figure out better filter!!

                if query[4:7] != 'Sen':
                    district_name = query[2:6]


                    # Check Tweet text for district name to filter out irrelvancies;
                    # skip rest of for loop if district name (or aliases) not found

                    check = False

                    for district_alias in distdict_short[district_name]:
                        if original_text:
                            if district_alias in original_text.lower():
                                check = True
                        else:
                            if district_alias in text.lower():
                                check = True
                    if check == False:
                        # print("Tweet rejected, no district reference")
                        continue


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



                # Try writing to Mysql database
                try:
                    write_database(post_id, user_id, text, created_at,
                            created_at_dt, reply_to_user_id,
                            reply_to_scrname, reply_to_status_id, retweet_count,
                            favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
                            original_text, original_tweet_created_at, original_tweet_likes,
                            original_author_id, original_author_scrname, polarity,
                            polarity_val, tag_list, url_list, user_scrname, user_name,
                            user_location, user_created, user_followers, user_friends,
                            user_statuses, query)

                    indexCount += 1


                except exc.SQLAlchemyError as e:
                    print("There's a dadgummed database write error for post ID {0}: {1}".\
                    format(post_id, e))
                    print("It's currently {}".format(datetime.datetime.now()))

                    with open('logs/twitterscrape_passed.txt', 'a') as pw:
                        pw.write('{}\n'.format(post_id))

                    time.sleep(1 * 60)
                    db.session.rollback()

                    pass




                if indexCount % 50 == 0:
                    db.session.commit()
                    print("{} tweets searched".format(indexCount))
                    print(tweet.id, tweet.created_at)


            #Reset total tweets fetched
            tweetCount += len(new_tweets)
            #print("Downloaded {} tweets".format(tweetCount))

            #Reset max_id from last tweet returned for new manually paged page of tweets
            max_id = new_tweets[-1].id


        except tweepy.error.TweepError as err:
            print("Error raised: {0}".format(err))
            time.sleep(5 * 60)


def search_cong():

    #Open csv file of competitive districts, iterate through it, searching for each row/district
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
            print("Starting district: {}".format(query))

            try:
                twitter_search(query)
                print("Finished with district: {}".format(query))
                db.session.commit()

                #visit district page to cache URL
                url_visit = 'https://pollchatter.org/district/{}?time_delta=14'.\
                        format(query[2:6])
                urllib.request.urlopen(url_visit)


            except exc.SQLAlchemyError as e:
                print("There's a dadgummed db error: {}".format(e))


                time.sleep(1 * 60)
                db.session.rollback()
                pass

    db.session.close()

def search_sen():
    #Open csv file of competitive districts, iterate through it, searching for each row/district
    with open('app/comp_races_parsed_sen.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #Create search query with quotation marks, to limit to exact matches
            query = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"' + ' OR ' + \
                '"'+row[4]+'"' + ' OR ' + '"'+row[5]+'"'
            print(query)
            print(query[4:7])


            try:
                twitter_search(query)
                db.session.commit()

                #visit district page to cache URL
                url_visit = 'https://pollchatter.org/district/{}?time_delta=14'.\
                        format(query[2:7])
                urllib.request.urlopen(url_visit)


            except exc.SQLAlchemyError as e:
                print("There's a dadgummed db error: {}".format(e))


                time.sleep(.5 * 60)
                db.session.rollback()
                pass



    db.session.close()



def run_twitterscrape():

    with open('logs/twitterscrape_log.txt', 'a') as fw:
        fw.write('started twitterscrape at {}\n'.format(datetime.datetime.now()))

    #Do Senate searchcd
    # search_sen()
    # with open('logs/twitterscrape_log.txt', 'a') as f:
    #     f.write('added senate items to database, finished at {}\n\n'.format(datetime.datetime.now()))

    #Do Congress search
    search_cong()


    print(datetime.datetime.now())
    time = datetime.datetime.now()

    with open('logs/twitterscrape_log.txt', 'a') as f:
        f.write('added cong items to database, finished at {}\n\n'.format(datetime.datetime.now()))

    #Run function filling overview-cache tables
    fill.run_all()


    with open('logs/twitterscrape_log.txt', 'a') as f:
        f.write('filled all cache tables, finished at {}\n\n'.format(datetime.datetime.now()))

    gf.fill_graphs()

if __name__ == "__main__":
    run_twitterscrape()
