import os
from app.tweepy_cred import *
import botometer
import time
from decimal import Decimal, ROUND_HALF_UP

import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine(os.environ.get('DATABASE_URL'))
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy import Column, Integer, String, Float, func
from azmodels import User, Post, Hashtag, District, Url, Base
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

#GET ALL USER OBJECTS
users = session.query(User.user_scrname, func.count(User.user_scrname)).\
join(Post.user).\
group_by(User.user_scrname).\
order_by(func.count(User.user_scrname).desc()).all()

bom = botometer.Botometer(wait_on_rate_limit=True, mashape_key=mashape_key, **twitter_app_auth)

x = 0

for item in users[4000:6000]:

    this_user = session.query(User).\
    filter(User.user_scrname==item[0]).first()

#If no botprob has been found in previous rounds
    if not this_user.user_botprob_cap:
        to_search = "@{}".format(this_user.user_scrname)
        print("searching user: {}".format(to_search))

        try:
            result = bom.check_account(to_search)
            end_result_display = result['display_scores']['english']
            end_result_cap = result['cap']['english']

            print("user {0}'s bot-or-not-score (0=no, 5=yes) is {1}".format(to_search, end_result_cap))



            this_user.user_botprob = end_result_display
            this_user.user_botprob_cap = end_result_cap

            #Convert CAP into string, then a decimal rounded to 0.0001
            clean_cap = Decimal(str(this_user.user_botprob_cap)).quantize(Decimal('0.0001'),\
            rounding = ROUND_HALF_UP)

            #Convert CAP into percentage (and store as 00.01 float)
            str_clean_cap = str(clean_cap)
            user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])

            this_user.user_cap_perc = user_cap

            session.add(this_user)

            print("updating user{}".format(this_user.user_scrname))
            x += 1
            if x % 25 == 0:
                session.commit()
        except tweepy.error.TweepError as err:
            print("Error raised: {0}".format(err))
            time.sleep(4 * 60)
        except botometer.NoTimelineError as err:
            print("Error raised: {0}".format(err))
        except:
            session.rollback()
            continue
    else:
        #Convert CAP into string, then a decimal rounded to 0.0001
        clean_cap = Decimal(str(this_user.user_botprob_cap)).quantize(Decimal('0.0001'),\
        rounding = ROUND_HALF_UP)

        #Convert CAP into percentage (and store as 00.01 float)
        str_clean_cap = str(clean_cap)
        user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])

        this_user.user_cap_perc = user_cap

        session.add(this_user)
session.commit()
session.close()
