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



#NOTE: adding dist_group = allcong, allsen, allraces

def fill_dist_activity(dist_group, time_delta, table, table_new, table_old):


    if dist_group == "allcong":
        dist_fig = 1
    if dist_group == "allsen":
        dist_fig = 2

    #CREATE CONNECTION FOR DIRECT DB ACCESS
    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1};".format(table_new, table_old))
    conn.execute('CREATE TABLE IF NOT EXISTS {0} LIKE dist_activity_1;'.format(table))
    conn.execute('CREATE TABLE {0} LIKE {1};'.format(table_new, table))
    conn.execute("DELETE FROM {0};".format(table_new))

    #GET ORDERED LIST OF DISTRICTS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    #If partial group congress or senate
    if dist_group == "allcong" or dist_group == "allsen":
        most_active = db.session.query(District.district_name,\
        func.count(District.district_name)).\
        join(Post.districts).\
        filter(Post.created_at >= str_time_range).filter(District.dist_type==dist_fig).\
        group_by(District.district_name).\
        order_by(func.count(District.district_name).desc()).all()

    #If all races
    else:

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






def fill_hash_activity(dist_group, time_delta, table, table_new, table_old):

    if dist_group == "allcong":
        dist_fig = 1
    if dist_group == "allsen":
        dist_fig = 2

    #CREATE CONNECTION FOR DIRECT DB ACCESS

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE IF NOT EXISTS {0} LIKE hash_activity_1;'.format(table))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    if dist_group == "allcong" or dist_group == "allsen":
        all_hashes = db.session.query(Hashtag.hash_id, Hashtag.hashtag,\
        func.count(Hashtag.hash_id)).\
        join(Post.hashtags).join(Post.districts).\
        filter(Post.created_at >= str_time_range).filter(District.dist_type==dist_fig).\
        group_by(Hashtag.hash_id).order_by(func.count(Hashtag.hash_id).desc()).all()

    else:
        all_hashes = db.session.query(Hashtag.hash_id, Hashtag.hashtag,\
        func.count(Hashtag.hash_id)).\
        join(Post.hashtags).join(Post.districts).\
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




def fill_top_tweeters(dist_group, time_delta, table, table_new, table_old):

    if dist_group == "allcong":
        dist_fig = 1
    if dist_group == "allsen":
        dist_fig = 2

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE IF NOT EXISTS {0} LIKE top_tweeters_1;'.format(table))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    if dist_group == "allcong" or dist_group == "allsen":

        top_tweeters = db.session.query(User.user_id, User.user_scrname,\
        User.user_cap_perc, func.count(User.user_scrname)).\
        join(Post.user).join(Post.districts).\
        filter(Post.created_at >= str_time_range).filter(District.dist_type==dist_fig).\
        group_by(User.user_id).order_by(func.count(User.user_id).desc()).all()

    else:

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

def fill_retweeted_users(dist_group, time_delta, table, table_new, table_old):

    if dist_group == "allcong":
        dist_fig = 1
    if dist_group == "allsen":
        dist_fig = 2

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE IF NOT EXISTS {0} LIKE retweeted_users_1;'.format(table))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #GET ORDERED LIST OF HASHTAGS AND ACTIVITY COUNT

    str_time_range = stringtime(time_delta)

    if dist_group == "allcong" or dist_group == "allsen":
        retweeted_users = db.session.query(Post.original_author_scrname, \
        func.count(Post.original_author_scrname)).\
        join(Post.districts).\
        filter(Post.original_author_scrname != "").filter(Post.created_at >= str_time_range).\
        filter(District.dist_type==dist_fig).\
        group_by(Post.original_author_scrname).order_by(func.count(Post.original_author_scrname).\
        desc()).all()

    else:
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

def fill_retweeted_tweets(dist_group, time_delta, table, table_new, table_old):

    if dist_group == "allcong":
        dist_fig = 1
    if dist_group == "allsen":
        dist_fig = 2

    conn = db.engine.connect()
    conn.execute("DROP TABLE IF EXISTS {0}, {1}".format(table_new, table_old))
    conn.execute('CREATE TABLE IF NOT EXISTS {0} LIKE retweeted_tweets_1;'.format(table))
    conn.execute('CREATE TABLE {0} LIKE {1}'.format(table_new, table))
    conn.execute("DELETE FROM {0}".format(table_new))

    #Get uncleaned list of top retweeted tweet IDS

    str_time_range = stringtime(time_delta)

    if dist_group == "allcong" or dist_group == "allsen":
        most_retweeted_tweets = db.session.query(Post.post_id, Post.original_tweet_id, \
        Post.retweet_count, District.dist_type).\
        join(Post.districts).\
        filter(Post.created_at >= str_time_range).filter(District.dist_type==dist_fig).\
        order_by(Post.retweet_count.desc()).all()

    else:
        most_retweeted_tweets = db.session.query(Post.post_id, Post.original_tweet_id, \
        Post.retweet_count, District.dist_type).\
        join(Post.districts).\
        filter(Post.created_at >= str_time_range).\
        order_by(Post.retweet_count.desc()).all()

    # Get cleaned list of tweet ids (no dupes, w/ district relevance)
    # List returns 20 tweets, with lists of following attributes:
    # [Post.post_id, relevant screen name, retweet_count, tweet_html (if exists),
    # original_tweet_id]
    tweet_list = get_tweet_list_ids(most_retweeted_tweets)
    print(tweet_list[0])

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


def run_all():
    fill_dist_activity('allcong', 1, 'dist_activity_allcong_1', 'dist_activity_allcong_1_new', 'dist_activity_allcong_1_old')
    fill_dist_activity('allsen', 1, 'dist_activity_allsen_1', 'dist_activity_allsen_1_new', 'dist_activity_allsen_1_old')
    fill_dist_activity('allraces', 1, 'dist_activity_allraces_1', 'dist_activity_allraces_1_new', 'dist_activity_allraces_1_old')
    fill_dist_activity('allcong', 2, 'dist_activity_allcong_2', 'dist_activity_allcong_2_new', 'dist_activity_allcong_2_old')
    fill_dist_activity('allsen', 2, 'dist_activity_allsen_2', 'dist_activity_allsen_2_new', 'dist_activity_allsen_2_old')
    fill_dist_activity('allraces', 2, 'dist_activity_allraces_2', 'dist_activity_allraces_2_new', 'dist_activity_allraces_2_old')
    fill_dist_activity('allcong', 7, 'dist_activity_allcong_7', 'dist_activity_allcong_7_new', 'dist_activity_allcong_7_old')
    fill_dist_activity('allsen', 7, 'dist_activity_allsen_7', 'dist_activity_allsen_7_new', 'dist_activity_allsen_7_old')
    fill_dist_activity('allraces', 7, 'dist_activity_allraces_7', 'dist_activity_allraces_7_new', 'dist_activity_allraces_7_old')
    fill_dist_activity('allcong', 14, 'dist_activity_allcong_7', 'dist_activity_allcong_7_new', 'dist_activity_allcong_7_old')
    fill_dist_activity('allsen', 14, 'dist_activity_allsen_7', 'dist_activity_allsen_7_new', 'dist_activity_allsen_7_old')
    fill_dist_activity('allraces', 14, 'dist_activity_allraces_7', 'dist_activity_allraces_7_new', 'dist_activity_allraces_7_old')
    fill_dist_activity('allcong', 28, 'dist_activity_allcong_28', 'dist_activity_allcong_28_new', 'dist_activity_allcong_28_old')
    fill_dist_activity('allsen', 28, 'dist_activity_allsen_28', 'dist_activity_allsen_28_new', 'dist_activity_allsen_28_old')
    fill_dist_activity('allraces', 28, 'dist_activity_allraces_28', 'dist_activity_allraces_28_new', 'dist_activity_allracesg_28_old')

    fill_hash_activity('allcong', 1, 'hash_activity_allcong_1', 'hash_activity_allcong_1_new', 'hash_activity_allcong_1_old')
    fill_hash_activity('allsen', 1, 'hash_activity_allsen_1', 'hash_activity_allsen_1_new', 'hash_activity_allsen_1_old')
    fill_hash_activity('allraces', 1, 'hash_activity_allraces_1', 'hash_activity_allraces_1_new', 'hash_activity_allraces_1_old')
    fill_hash_activity('allcong', 2, 'hash_activity_allcong_2', 'hash_activity_allcong_2_new', 'hash_activity_allcong_2_old')
    fill_hash_activity('allsen', 2, 'hash_activity_allsen_2', 'hash_activity_allsen_2_new', 'hash_activity_allsen_2_old')
    fill_hash_activity('allraces', 2, 'hash_activity_allraces_2', 'hash_activity_allraces_2_new', 'hash_activity_allraces_2_old')
    fill_hash_activity('allcong', 7, 'hash_activity_allcong_7', 'hash_activity_allcong_7_new', 'hash_activity_allcong_7_old')
    fill_hash_activity('allsen', 7, 'hash_activity_allsen_7', 'hash_activity_allsen_7_new', 'hash_activity_allsen_7_old')
    fill_hash_activity('allraces', 7, 'hash_activity_allraces_7', 'hash_activity_allraces_7_new', 'hash_activity_allraces_7_old')
    fill_hash_activity('allcong', 14, 'hash_activity_allcong_7', 'hash_activity_allcong_7_new', 'hash_activity_allcong_7_old')
    fill_hash_activity('allsen', 14, 'hash_activity_allsen_7', 'hash_activity_allsen_7_new', 'hash_activity_allsen_7_old')
    fill_hash_activity('allraces', 14, 'hash_activity_allraces_7', 'hash_activity_allraces_7_new', 'hash_activity_allraces_7_old')
    fill_hash_activity('allcong', 28, 'hash_activity_allcong_28', 'hash_activity_allcong_28_new', 'hash_activity_allcong_28_old')
    fill_hash_activity('allsen', 28, 'hash_activity_allsen_28', 'hash_activity_allsen_28_new', 'hash_activity_allsen_28_old')
    fill_hash_activity('allraces', 28, 'hash_activity_allraces_28', 'hash_activity_allraces_28_new', 'hash_activity_allraces_28_old')

    fill_top_tweeters('allcong', 1, 'top_tweeters_allcong_1', 'top_tweeters_allcong_1_new', 'top_tweeters_allcong_1_old')
    fill_top_tweeters('allsen', 1, 'top_tweeters_allsen_1', 'top_tweeters_allsen_1_new', 'top_tweeters_allsen_1_old')
    fill_top_tweeters('allraces', 1, 'top_tweeters_allraces_1', 'top_tweeters_allraces_1_new', 'top_tweeters_allraces_1_old')
    fill_top_tweeters('allcong', 2, 'top_tweeters_allcong_2', 'top_tweeters_allcong_2_new', 'top_tweeters_allcong_2_old')
    fill_top_tweeters('allsen', 2, 'top_tweeters_allsen_2', 'top_tweeters_allsen_2_new', 'top_tweeters_allsen_2_old')
    fill_top_tweeters('allraces', 2, 'top_tweeters_allraces_2', 'top_tweeters_allraces_2_new', 'top_tweeters_allraces_2_old')
    fill_top_tweeters('allcong', 7, 'top_tweeters_allcong_7', 'top_tweeters_allcong_7_new', 'top_tweeters_allcong_7_old')
    fill_top_tweeters('allsen', 7, 'top_tweeters_allsen_7', 'top_tweeters_allsen_7_new', 'top_tweeters_allsen_7_old')
    fill_top_tweeters('allraces', 7, 'top_tweeters_allraces_7', 'top_tweeters_allraces_7_new', 'top_tweeters_allraces_7_old')
    fill_top_tweeters('allcong', 14, 'top_tweeters_allcong_28', 'top_tweeters_allcong_28_new', 'top_tweeters_allcong_28_old')
    fill_top_tweeters('allsen', 14, 'top_tweeters_allsen_28', 'top_tweeters_allsen_28_new', 'top_tweeters_allsen_28_old')
    fill_top_tweeters('allraces', 14, 'top_tweeters_allraces_28', 'top_tweeters_allraces_28_new', 'top_tweeters_allraces_28_old')
    fill_top_tweeters('allcong', 28, 'top_tweeters_allcong_28', 'top_tweeters_allcong_28_new', 'top_tweeters_allcong_28_old')
    fill_top_tweeters('allsen', 28, 'top_tweeters_allsen_28', 'top_tweeters_allsen_28_new', 'top_tweeters_allsen_28_old')
    fill_top_tweeters('allraces', 28, 'top_tweeters_allraces_28', 'top_tweeters_allraces_28_new', 'top_tweeters_allraces_28_old')


    fill_retweeted_users('allcong', 1, 'retweeted_users_allcong_1', 'retweeted_users_allcong_1_new', 'retweeted_users_allcong_1_old')
    fill_retweeted_users('allsen', 1, 'retweeted_users_allsen_1', 'retweeted_users_allsen_1_new', 'retweeted_users_allsen_1_old')
    fill_retweeted_users('allraces', 1, 'retweeted_users_allraces_1', 'retweeted_users_allraces_1_new', 'retweeted_users_allraces_1_old')
    fill_retweeted_users('allcong', 2, 'retweeted_users_allcong_2', 'retweeted_users_allcong_2_new', 'retweeted_users_allcong_2_old')
    fill_retweeted_users('allsen', 2, 'retweeted_users_allsen_2', 'retweeted_users_allsen_2_new', 'retweeted_users_allsen_2_old')
    fill_retweeted_users('allraces', 2, 'retweeted_users_allraces_2', 'retweeted_users_allraces_2_new', 'retweeted_users_allraces_2_old')
    fill_retweeted_users('allcong', 7, 'retweeted_users_allcong_7', 'retweeted_users_allcong_7_new', 'retweeted_users_allcong_7_old')
    fill_retweeted_users('allsen', 7, 'retweeted_users_allsen_7', 'retweeted_users_allsen_7_new', 'retweeted_users_allsen_7_old')
    fill_retweeted_users('allraces', 7, 'retweeted_users_allraces_7', 'retweeted_users_allraces_7_new', 'retweeted_users_allraces_7_old')
    fill_retweeted_users('allcong', 14, 'retweeted_users_allcong_28', 'retweeted_users_allcong_28_new', 'retweeted_users_allcong_28_old')
    fill_retweeted_users('allsen', 14, 'retweeted_users_allsen_28', 'retweeted_users_allsen_28_new', 'retweeted_users_allsen_28_old')
    fill_retweeted_users('allraces', 14, 'retweeted_users_allraces_28', 'retweeted_users_allraces_28_new', 'retweeted_users_allraces_28_old')
    fill_retweeted_users('allcong', 28, 'retweeted_users_allcong_28', 'retweeted_users_allcong_28_new', 'retweeted_users_allcong_28_old')
    fill_retweeted_users('allsen', 28, 'retweeted_users_allsen_28', 'retweeted_users_allsen_28_new', 'retweeted_users_allsen_28_old')
    fill_retweeted_users('allraces', 28, 'retweeted_users_allraces_28', 'retweeted_users_allraces_28_new', 'retweeted_users_allraces_28_old')


    fill_retweeted_tweets('allcong', 1, 'retweeted_tweets_allcong_1', 'retweeted_tweets_allcong_1_new', 'retweeted_tweets_allcong_1_old')
    fill_retweeted_tweets('allsen', 1, 'retweeted_tweets_allsen_1', 'retweeted_tweets_allsen_1_new', 'retweeted_tweets_allsen_1_old')
    fill_retweeted_tweets('allraces', 1, 'retweeted_tweets_allraces_1', 'retweeted_tweets_allraces_1_new', 'retweeted_tweets_allraces_1_old')
    fill_retweeted_tweets('allcong', 2, 'retweeted_tweets_allcong_2', 'retweeted_tweets_allcong_2_new', 'retweeted_tweets_allcong_2_old')
    fill_retweeted_tweets('allsen', 2, 'retweeted_tweets_allsen_2', 'retweeted_tweets_allsen_2_new', 'retweeted_tweets_allsen_2_old')
    fill_retweeted_tweets('allraces', 2, 'retweeted_tweets_allraces_2', 'retweeted_tweets_allraces_2_new', 'retweeted_tweets_allraces_2_old')
    fill_retweeted_tweets('allcong', 7, 'retweeted_tweets_allcong_7', 'retweeted_tweets_allcong_7_new', 'retweeted_tweets_allcong_7_old')
    fill_retweeted_tweets('allsen', 7, 'retweeted_tweets_allsen_7', 'retweeted_tweets_allsen_7_new', 'retweeted_tweets_allsen_7_old')
    fill_retweeted_tweets('allraces', 7, 'retweeted_tweets_allraces_7', 'retweeted_tweets_allraces_7_new', 'retweeted_tweets_allraces_7_old')
    fill_retweeted_tweets('allcong', 14, 'retweeted_tweets_allcong_28', 'retweeted_tweets_allcong_28_new', 'retweeted_tweets_allcong_28_old')
    fill_retweeted_tweets('allsen', 14, 'retweeted_tweets_allsen_28', 'retweeted_tweets_allsen_28_new', 'retweeted_tweets_allsen_28_old')
    fill_retweeted_tweets('allraces', 14, 'retweeted_tweets_allraces_28', 'retweeted_tweets_allraces_28_new', 'retweeted_tweets_allraces_28_old')
    fill_retweeted_tweets('allcong', 28, 'retweeted_tweets_allcong_28', 'retweeted_tweets_allcong_28_new', 'retweeted_tweets_allcong_28_old')
    fill_retweeted_tweets('allsen', 28, 'retweeted_tweets_allsen_28', 'retweeted_tweets_allsen_28_new', 'retweeted_tweets_allsen_28_old')
    fill_retweeted_tweets('allraces', 28, 'retweeted_tweets_allraces_28', 'retweeted_tweets_allraces_28_new', 'retweeted_tweets_allraces_28_old')




if __name__ == '__main__':
    run_all()
