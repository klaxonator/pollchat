import os
import csv
import sys
import tweepy
import time
from app.helpers import skip_list, get_tweet, distdict_short
from app import app, db
import fill_overview_tables_timed as fill

#import preprocessor as p
from textblob import TextBlob
import datetime

#Import all Twitter credentials
import app.tweepy_cred as cred


##Set up database functions
from azmodels import User, Post, Hashtag, District, Url, posthash_assoc,\
 posturl_assoc, postdist_assoc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Instantiate SQLalchemy database connection


#Write Twitter variables to DB
def write_database(post_id, user_id, text, created_at, reply_to_user_id,
        reply_to_scrname, reply_to_status_id, retweet_count,
        favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
        original_text, original_tweet_created_at, original_tweet_likes,
        original_author_id, original_author_scrname, polarity,
        polarity_val, tag_list, url_list, user_scrname, user_name,
        user_location, user_created, user_followers, user_friends,
        user_statuses, query):



#POST TABLE: If tweet ID not already in database, add to Post table

    if db.session.query(Post).filter(Post.post_id == post_id).count() == 0:


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


        new_post = Post(post_id, user_id, text, created_at, reply_to_user_id,
            reply_to_scrname, reply_to_status_id, retweet_count,
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


#DISTRICT TABLE
            #capture District_id from 1st query term:
        state = query[2:4]
        district = query[4:6]
        district_name = query[2:6]

        #Check if district is in DB, add if not
        district_search = db.session.query(District).\
        filter(District.district_name == district_name).first()
        if district_search == None:
            new_district = District(state, district, district_name)
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




def twitter_search(query):



    #Iterate over tweets returned by Tweepy Cursor, with query contained in 'q'

    count = 0

    try:
        for tweet in tweepy.Cursor(
                cred.api.search,
                q=query,
                lang='en',
                count=100,
                include_entities=True,
                tweet_mode="extended").items():




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
                print("Error raised: {0}".format(ae))
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




            # Check Tweet text for district name to filter out irrelvancies;
            # skip rest of for loop if district name (or aliases) not found
            district_name = query[2:6]
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



            #NOTE: Taeks to long, take out until online. cut from:"
            # in pollchat_twitter:
            #     write_database,
            #     new_post
            #     write_database
            #
            # in az_models
            #     def_init

            # try:
            #     tweet_html = get_tweet(post_id)
            # except:
            #     pass

            # print(tweet.user.screen_name, "\n", tweet.id_str, "\n", tweet.full_text, "\n")
            # print(original_tweet_id)
            # print(original_tweet_retweets)
            # print(tweet_html)
            # print(polarity_val)




            write_database(post_id, user_id, text, created_at, reply_to_user_id,
                    reply_to_scrname, reply_to_status_id, retweet_count,
                    favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
                    original_text, original_tweet_created_at, original_tweet_likes,
                    original_author_id, original_author_scrname, polarity,
                    polarity_val, tag_list, url_list, user_scrname, user_name,
                    user_location, user_created, user_followers, user_friends,
                    user_statuses, query)

            count += 1

            if count % 200 == 0:
                db.session.commit()
                print("{} items added to database so far".format(count))

    except tweepy.error.TweepError as err:
        print("Error raised: {0}".format(err))
        time.sleep(5 * 60)






def run_twitterscrape():

    with open('logs/twitterscrape_log.txt', 'a') as fw:
        fw.write('started twitterscrape at {}\n'.format(datetime.datetime.now()))


    #Open csv file of competitive districts, iterate through it, searching for each row/district
    with open('app/comp_races_parsed.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #Create search query with quotation marks, to limit to exact matches
            if row[4] != "":
                q = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"' + ' OR ' + '"'+row[4]+'"'
            else:
                q = '"'+row[0]+'"' + ' OR ' + '"'+row[1]+'"' + ' OR ' + \
                '"'+row[2]+'"' + ' OR ' + '"'+row[3]+'"'
            print("Starting district: {}".format(q))
            twitter_search(q)
            print("Finished with district: {}".format(q))
            db.session.commit()

    db.session.close()
    print(datetime.datetime.now())
    time = datetime.datetime.now()

    with open('logs/twitterscrape_log.txt', 'a') as f:
        f.write('added items to database, finished at {}\n\n'.format(time))

    #Run function filling overview-cache tables
    fill.run_all()


    with open('logs/twitterscrape_log.txt', 'a') as f:
        f.write('filled all cache tables, finished at {}\n\n'.format(time))
