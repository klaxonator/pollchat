from app.tweepy_cred import *
import botometer
import time
from decimal import Decimal, ROUND_HALF_UP

import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine('sqlite:///compdists_test2.db')
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy import Column, Integer, String, Float, func
from azmodels import User, Post, Hashtag, District, Url, Base, DateData
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).\
join(Post.user).\
group_by(User.user_scrname).order_by(func.count(User.user_scrname).desc()).all()

bom = botometer.Botometer(wait_on_rate_limit=True, mashape_key=mashape_key, **twitter_app_auth)

x = 0

for item in users[11500:13700]:
    if not item.user_botprob_cap:
        to_search = "@{}".format(item.user_scrname)
        print("searching user: {}".format(to_search))

        try:
            result = bom.check_account(to_search)
            end_result_display = result['display_scores']['english']
            end_result_cap = result['cap']['english']

            print("user {0}'s bot-or-not-score (0=no, 5=yes) is {1}".format(to_search, end_result_cap))

            # to_change = session.query(User).filter(User.user_scrname==item[0]).first()

            item.user_botprob = end_result_display
            item.user_botprob_cap = end_result_cap

            #Convert CAP into string, then a decimal rounded to 0.0001
            clean_cap = Decimal(str(item.user_botprob_cap)).quantize(Decimal('0.0001'),\
            rounding = ROUND_HALF_UP)

            #Convert CAP into percentage (and store as 00.01 float)
            str_clean_cap = str(clean_cap)
            user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])

            item.user_cap_perc = user_cap

            session.add(item)

            print("updating user{}".format(item.user_scrname))
            x += 1
            if x % 25 == 0:
                session.commit()
        except tweepy.error.TweepError as err:
            print("Error raised: {0}".format(err))
            # time.sleep(2 * 60)
        except botometer.NoTimelineError as err:
            print("Error raised: {0}".format(err))
    else:
        #Convert CAP into string, then a decimal rounded to 0.0001
        clean_cap = Decimal(str(item.user_botprob_cap)).quantize(Decimal('0.0001'),\
        rounding = ROUND_HALF_UP)

        #Convert CAP into percentage (and store as 00.01 float)
        str_clean_cap = str(clean_cap)
        user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])

        item.user_cap_perc = user_cap

        session.add(item)
session.commit()
session.close()
