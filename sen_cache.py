from app import app, db
from app.models import *
from app.helpers import stringtime
import csv
from sqlalchemy import func


def sen_cache(time_delta):

    str_time_range = stringtime(time_delta)

    with open('app/comp_races_parsed_sen.csv', 'r') as f:
        reader = csv.reader(f)


        for row in reader:
            #row_split = row.split(',')
            dynamic = row[0][1:6]
            print("District is {}".format(dynamic))

            dist_hashes = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
            join(Post.districts).join(Post.hashtags).\
            filter(District.district_name==dynamic).\
            filter(Post.created_at >= str_time_range).\
            group_by(Hashtag.hashtag).\
            order_by(func.count(Hashtag.hashtag).desc()).all()

            print(len(dist_hashes))

            top_tweeters = db.session.query(User.user_scrname, \
            func.count(User.user_scrname), User.user_cap_perc, User.user_id).\
            join(Post.user).join(Post.districts).\
            filter(District.district_name==dynamic).\
            filter(Post.created_at >= str_time_range).\
            group_by(User.user_id).\
            order_by(func.count(User.user_id).desc()).all()

            print(len(top_tweeters))

            most_retweeted = db.session.query(Post.original_author_scrname, \
            func.count(Post.original_author_scrname)).\
            join(Post.districts).\
            filter(District.district_name==dynamic).\
            filter(Post.created_at >= str_time_range).\
            filter(Post.original_author_scrname != "").\
            group_by(Post.original_author_scrname).\
            order_by(func.count(Post.original_author_scrname).desc()).all()

            print(len(most_retweeted))

if __name__ == "__main__":
    sen_cache(14)
