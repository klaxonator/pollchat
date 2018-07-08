import os
from app.helpers import stringtime, get_tweet_list_ids, populate_tweet_list
from app import app, db
from app.models import *
from sqlalchemy import func, Date
import pprint





# STRATEGY:
# mysql> DROP TABLE IF EXISTS my_summary_new, my_summary_old;
# mysql> CREATE TABLE my_summary_new LIKE my_summary;
# -- populate my_summary_new as desired
# mysql> RENAME TABLE my_summary TO my_summary_old, my_summary_new TO my_summary;




def fill_dist_activity(time_delta, table, table_new, table_old):

    #CREATE CONNECTION FOR DIRECT DB ACCESS

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF DISTRICTS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    most_active = db.session.query(District.district_name,\
    func.count(District.district_name)).\
    join(Post.districts).\
    filter(Post.created_at >= str_time_range).\
    group_by(District.district_name).\
    order_by(func.count(District.district_name).desc()).all()



    counter = 1
    for item in most_active:

        conn.execute("INSERT INTO {0} VALUES ({1}, '{2}', {3});".\
                                format(table_new, counter, item[0], item[1]))

        counter += 1




    conn.execute('RENAME TABLE {0} TO {1}, {2} TO {3}'.\
    format(table, table_old, table_new, table))

    conn.close()






def fill_hash_activity(time_delta, table, table_new, table_old):
    #CREATE CONNECTION FOR DIRECT DB ACCESS

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    all_hashes = db.session.query(Hashtag.hash_id, Hashtag.hashtag,\
    func.count(Hashtag.hash_id)).\
    join(Post.hashtags).\
    filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hash_id).order_by(func.count(Hashtag.hash_id).desc()).all()


    #INSERT TOP 100 ITEMS INTO SHADOW TABLE (TABLE_NEW)
    counter = 1
    for item in all_hashes[0:100]:

        conn.execute("INSERT INTO {0} VALUES ({1}, {2}, '{3}', {4});".\
                format(table_new, counter, item[0], item[1], item[2]))

        counter += 1



    #RENAME EXISTING (MAIN) TABLE TO OLD, RENAME SHADOW TO MAIN

    conn.execute('RENAME TABLE {0} TO {1}, {2} TO {3}'.\
    format(table, table_old, table_new, table))

    conn.close()




def fill_top_tweeters(time_delta, table, table_new, table_old):

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    top_tweeters = db.session.query(User.user_id, User.user_scrname,\
    User.user_cap_perc, func.count(User.user_scrname)).\
    join(Post.user).\
    filter(Post.created_at >= str_time_range).\
    group_by(User.user_id).order_by(func.count(User.user_id).desc()).all()


    #INSERT TOP 100 ITEMS INTO SHADOW TABLE (TABLE_NEW)
    counter = 1
    for item in top_tweeters[0:100]:

        if item[2]:

            conn.execute("INSERT INTO {0} VALUES ({1}, '{2}', '{3}', {4}, {5});".\
                                    format(table_new, counter, item[0], item[1],\
                                    item[2], item[3]))

            counter += 1

        else:
            conn.execute("INSERT INTO {0} VALUES ({1}, '{2}', '{3}', {4}, {5});".\
                                    format(table_new, counter, item[0], item[1],\
                                    '-1.0', item[3]))

            counter += 1

    #RENAME EXISTING (MAIN) TABLE TO OLD, RENAME SHADOW TO MAIN

    conn.execute('RENAME TABLE {0} TO {1}, {2} TO {3}'.\
    format(table, table_old, table_new, table))

    conn.close()

def fill_retweeted_users(time_delta, table, table_new, table_old):

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    retweeted_users = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    filter(Post.original_author_scrname != "").filter(Post.created_at >= str_time_range).\
    group_by(Post.original_author_scrname).order_by(func.count(Post.original_author_scrname).\
    desc()).all()


    counter = 1
    for item in retweeted_users[0:100]:

        conn.execute("INSERT INTO {0} VALUES ({1}, '{2}', {3});".\
                                format(table_new, counter, item[0], item[1]))

        counter += 1



    conn.execute('RENAME TABLE {0} TO {1}, {2} TO {3}'.\
    format(table, table_old, table_new, table))

    conn.close()

def fill_retweeted_tweets(time_delta, table, table_new, table_old):

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #Get uncleaned list of top retweeted tweet IDS

    str_time_range = stringtime(time_delta)

    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_tweet_id, \
    Post.retweet_count).\
    filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    # Get cleaned list of tweet ids (no dupes, w/ district relevance)
    # List returns 20 tweets, with lists of following attributes:
    # [Post.post_id, relevant screen name, retweet_count, tweet_html (if exists),
    # original_tweet_id]
    tweet_list = get_tweet_list_ids(most_retweeted_tweets)

    # GET FULL LIST. RETURNS FOLLOWING ATTRIBUTE:
    # [Post id, screen name, retweet count, botscore]
    populated_list = populate_tweet_list(tweet_list)

    pprint.pprint(populated_list[0])
    counter = 1
    for item in populated_list:

        x = '''INSERT INTO {table} VALUES ({counter}, '{post_id}', '{botscore}', '{name}', {retweets});'''.\
           format(table=table_new, counter=counter, post_id=item[0], botscore=item[4], name=item[1], retweets=item[2])

        print(x)

        conn.execute(x)

        counter += 1


    conn.execute('RENAME TABLE {0} TO {1}, {2} TO {3}'.\
    format(table, table_old, table_new, table))

    conn.close()


if __name__ == '__main__':
    fill_dist_activity(1, 'dist_activity_1', 'dist_activity_1_new', 'dist_activity_1_old')
    fill_dist_activity(2, 'dist_activity_2', 'dist_activity_2_new', 'dist_activity_2_old')
    fill_dist_activity(7, 'dist_activity_7', 'dist_activity_7_new', 'dist_activity_7_old')
    fill_dist_activity(28, 'dist_activity_28', 'dist_activity_28_new', 'dist_activity_28_old')
    fill_hash_activity(1, 'hash_activity_1', 'hash_activity_1_new', 'hash_activity_1_old')
    fill_hash_activity(2, 'hash_activity_2', 'hash_activity_2_new', 'hash_activity_2_old')
    fill_hash_activity(7, 'hash_activity_7', 'hash_activity_7_new', 'hash_activity_7_old')
    fill_hash_activity(28, 'hash_activity_28', 'hash_activity_28_new', 'hash_activity_28_old')
    fill_retweeted_users(1, 'retweeted_users_1', 'retweeted_users_1_new', 'retweeted_users_1_old')
    fill_retweeted_users(2, 'retweeted_users_2', 'retweeted_users_2_new', 'retweeted_users_2_old')
    fill_retweeted_users(7, 'retweeted_users_7', 'retweeted_users_7_new', 'retweeted_users_7_old')
    fill_retweeted_users(28, 'retweeted_users_28', 'retweeted_users_28_new', 'retweeted_users_28_old')
    fill_top_tweeters(1, 'top_tweeters_1', 'top_tweeters_1_new', 'top_tweeters_1_old')
    fill_top_tweeters(2, 'top_tweeters_2', 'top_tweeters_2_new', 'top_tweeters_2_old')
    fill_top_tweeters(7, 'top_tweeters_7', 'top_tweeters_7_new', 'top_tweeters_7_old')
    fill_top_tweeters(28, 'top_tweeters_28', 'top_tweeters_28_new', 'top_tweeters_28_old')
    fill_retweeted_tweets(1, 'retweeted_tweets_1', 'retweeted_tweets_1_new', 'retweeted_tweets_1_old')
    fill_retweeted_tweets(2, 'retweeted_tweets_2', 'retweeted_tweets_2_new', 'retweeted_tweets_2_old')
    fill_retweeted_tweets(7, 'retweeted_tweets_7', 'retweeted_tweets_7_new', 'retweeted_tweets_7_old')
    fill_retweeted_tweets(28, 'retweeted_tweets_28', 'retweeted_tweets_28_new', 'retweeted_tweets_28_old')
