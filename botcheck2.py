import os
from app import app, db
from app.models import *

from app.tweepy_cred import *
import botometer
import time
from decimal import Decimal, ROUND_HALF_UP
from app.helpers import stringtime




from sqlalchemy import Column, Integer, String, Float, func


str_time_range = stringtime(14)

#GET ALL USER OBJECTS, in order of posting volume last 14 days
users = db.session.query(User.user_scrname, func.count(User.user_scrname)).\
join(Post.user).\
filter(Post.created_at >= str_time_range).\
group_by(User.user_scrname).\
order_by(func.count(User.user_scrname).desc()).all()

bom = botometer.Botometer(wait_on_rate_limit=True, mashape_key=mashape_key, **twitter_app_auth)

x = 0



# Iterate through first 2000 top posters
for item in users[0:3]:

    this_user = db.session.query(User).\
    filter(User.user_scrname==item[0]).first()

    # format botometer search

    to_search = "@{}".format(this_user.user_scrname)
    print("searching user: {}".format(to_search))

    try:
        # Do botometer search
        result = bom.check_account(to_search)
        end_result_display = result['display_scores']['english']
        end_result_cap = result['cap']['english']

        print("user {0}'s bot-or-not-score (0=no, 5=yes) is {1}".format(to_search, end_result_cap))



        this_user.user_botprob = end_result_display
        this_user.user_botprob_cap = end_result_cap

        print(end_result_display)
        print(end_result_cap)

        #Convert CAP into string, then a decimal rounded to 0.0001
        clean_cap = Decimal(str(this_user.user_botprob_cap)).quantize(Decimal('0.0001'),\
        rounding = ROUND_HALF_UP)

        print(clean_cap)

        #Convert CAP into percentage (and store as 00.01 float)
        str_clean_cap = str(clean_cap)
        user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])

        print(user_cap)

        this_user.user_cap_perc = user_cap

        db.session.add(this_user)

        print("updating user{}".format(this_user.user_scrname))
        x += 1
        if x % 25 == 0:
            db.session.commit()
    except tweepy.error.TweepError as err:
        print("Error raised: {0}".format(err))
        time.sleep(4 * 60)
    except botometer.NoTimelineError as err:
        print("Error raised: {0}".format(err))
    except:
        db.session.rollback()
        continue
    # else:
    #     #Convert CAP into string, then a decimal rounded to 0.0001
    #     clean_cap = Decimal(str(this_user.user_botprob_cap)).quantize(Decimal('0.0001'),\
    #     rounding = ROUND_HALF_UP)
    #
    #     #Convert CAP into percentage (and store as 00.01 float)
    #     str_clean_cap = str(clean_cap)
    #     user_cap = float(str_clean_cap[2:4] + "." + str_clean_cap[4:])
    #
    #     this_user.user_cap_perc = user_cap
    #
    #     db.session.add(this_user)
db.session.commit()
db.session.close()
