
import datetime
import os



from dotenv import load_dotenv

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, func
from azmodels import User, Post, Hashtag, District, Url, Base
from sqlalchemy.orm import sessionmaker

from app.helpers import check_district_relevance_st

def clean_bad_posts():

    basedir = os.path.abspath(os.path.dirname(__file__))

    load_dotenv(os.path.join(basedir, '.env'))


    engine = create_engine(os.environ.get('DATABASE_URL'))

    Base = declarative_base()
    Base.metadata.create_all(engine)


    Session = sessionmaker(bind=engine)
    session = Session()

    print("database started")
    #Get top retweeted list
    print("starting search")

    #NOTE: ADDING DISTRICT CHECK FOR SEN: TEST TO MAKE SURE WORKS

    most_retweeted_tweets = session.query(Post.post_id,
    Post.text, Post.original_text, District.district_name, Post.retweet_count).\
    join(Post.districts).\
    filter(Post.created_at >= '2018-05-15').\
    order_by(Post.retweet_count.desc()).all()

    #Search district associations with post
    print(len(most_retweeted_tweets))
    count = 0

    for db_tweet in most_retweeted_tweets:

        #If Tweet is Senat district, do nothing
        #if db_tweet[3][2:5] == 'Sen':
            #print("handling senate tweet")


        #If not Senate district, check relevance, delete if not relevant
        try:
            check = check_district_relevance_st(db_tweet)

            if check == False:


                to_delete = session.query(Post).\
                filter(Post.post_id==db_tweet[0]).first()

                session.delete(to_delete)

                if db_tweet[2]:
                    print("Deleting tweet_id {}".format(db_tweet[0]))
                    print(db_tweet[2])
                    with open('logs/clean_bad_posts_log.txt', 'a') as f:
                        f.write('Deleted tweet_id {}\n\n'.format(db_tweet[0]))
                        f.write('Text: {}\n\n'.format(db_tweet[2]))
                else:
                    print("Deleting tweet_id {}".format(db_tweet[0]))
                    print(db_tweet[1])
                    with open('logs/clean_bad_posts_log.txt', 'a') as f:
                        f.write('Deleted tweet_id {}\n\n'.format(db_tweet[1]))


                count += 1
                if count % 100 == 0:
                    db.session.commit()
                    print("deleted {} posts".format(count))
        except:
            session.rollback()
            continue

    session.commit()
    print('Finished at {0}, deleted {1} bad posts'.\
    format(datetime.datetime.now(), count))

if __name__ == "__main__":
    clean_bad_posts()
