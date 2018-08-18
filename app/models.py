from app import db


postdist_assoc = db.Table('postdist_assoc',
        db.Column('post_id', db.String, db.ForeignKey('Post.post_id')),
        db.Column('district_name', db.String, db.ForeignKey('District.district_name')),
        db.Index('postdist_postdist_idx', 'post_id', 'district_name'),
        db.Index('postdist_distpost_idx', 'district_name', 'post_id')
        )


posthash_assoc = db.Table('posthash_assoc',
            db.Column('post_id', db.String, db.ForeignKey('Post.post_id')),
            db.Column('hashtag', db.String, db.ForeignKey('Hashtag.hashtag')),
            db.Index('posthash_posthash_idx', 'post_id', 'hashtag'),
            db.Index('posthash_hashpost_idx', 'hashtag', 'post_id')
            )

posturl_assoc = db.Table('posturl_assoc',
            db.Column('post_id', db.String, db.ForeignKey('Post.post_id')),
            db.Column('url_id', db.String, db.ForeignKey('Url.url_id')),
            db.Index('posturl_posturl_idx', 'post_id', 'url_id'),
            db.Index('posturl_urlpost_idx', 'url_id', 'post_id')
            )




class User(db.Model):
    __tablename__='User'
    user_id = db.Column(db.String, primary_key=True)
    user_scrname = db.Column(db.String, index=True, nullable=False)
    user_name = db.Column(db.String)
    user_location = db.Column(db.String)
    user_created = db.Column(db.String)
    user_followers = db.Column(db.Integer)
    user_friends = db.Column(db.Integer)
    user_statuses = db.Column(db.Integer)
    user_botprob = db.Column(db.Float)
    user_botprob_cap = db.Column(db.Float)
    user_cap_perc = db.Column(db.Float, index=True)

    user_posts = db.relationship("Post", back_populates="user")

#    user_user_scrname_index = db.Index('user_user_scrname_idx', 'user_scrname')
#    user_user_cap_perc_index = db.Index('user_user_cap_perc_idx', 'user_scrname')


    def __repr__(self):
        return "Object: Twitter User with id {0!r} and screen name {1!r}".\
        format(self.user_id, self.user_scrname)



class Post(db.Model):
    __tablename__='Post'
    post_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('User.user_id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False, index=True)
    created_at_dt = db.Column(db.DateTime, index=True)
    reply_to_user_id = db.Column(db.String)
    reply_to_scrname = db.Column(db.String)
    reply_to_status_id = db.Column(db.String)
    retweet_count = db.Column(db.Integer)
    favorite_count = db.Column(db.Integer)

    is_retweet = db.Column(db.Integer)
    original_tweet_id = db.Column(db.String)
    original_tweet_retweets = db.Column(db.Integer)
    original_text = db.Column(db.String)
    original_tweet_created_at = db.Column(db.String)
    original_tweet_likes = db.Column(db.Integer)
    original_author_id = db.Column(db.String)
    original_author_scrname = db.Column(db.String, index=True)

    polarity = db.Column(db.Integer)
    polarity_val = db.Column(db.String)

    tweet_html = db.Column(db.String)

    user = db.relationship("User", back_populates="user_posts")

    districts = db.relationship(
        "District",
        secondary = postdist_assoc,
        back_populates = "district_posts"
        )
    hashtags = db.relationship(
        "Hashtag",
        secondary = posthash_assoc,
        back_populates = "hashtag_posts"
        )
    urls = db.relationship(
        "Url",
        secondary = posturl_assoc,
        back_populates = "url_posts"
        )

#    post_created_at_index = db.Index('post_created_at_idx', 'created_at')
#    post_original_author_scrname_index = db.Index('post_original_author_scrname_idx',
#        'original_author_scrname')


    def __init__(self, post_id, user_id, text, created_at, created_at_dt, reply_to_user_id,
     reply_to_scrname, reply_to_status_id, retweet_count,
     favorite_count, is_retweet, original_text, original_author_id,
     original_author_scrname, polarity, polarity_val):
        self.post_id = post_id
        self.user_id = user_id
        self.text = text
        self.created_at = created_at
        self.created_at_dt = created_at_dt
        self.reply_to_user_id = reply_to_user_id
        self.reply_to_scrname = reply_to_scrname
        self.reply_to_status_id = reply_to_status_id
        self.retweet_count = retweet_count

        self.favorite_count = favorite_count
        self.is_retweet = is_retweet
        self.original_text = original_text
        self.original_author_id = original_author_id
        self.original_author_scrname = original_author_scrname
        self.polarity = polarity
        self.polarity_val = polarity_val



    def __repr__(self):
        return "Object: Tweet by {0!r}, with ID {1!r}".format(self.user_id, self.post_id)



class Hashtag(db.Model):
    __tablename__='Hashtag'
    hash_id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String, index=True)

    hashtag_posts = db.relationship(
            "Post",
            secondary = posthash_assoc,
            back_populates = "hashtags"
        )
#    hashtag_hashtag_index = db.Index('hashtag_hashtag_idx','hashtag')

    def __init__(self, hashtag):
        self.hashtag = hashtag
        #self.post_id = post_id

    def __repr__(self):
        return "Hashtag object with hashtag: {0!r}".format(self.hashtag)



class Url(db.Model):
    __tablename__='Url'
    url_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    #post_id = db.Column(db.String, db.ForeignKey('Post.post_id'))
    url_posts = db.relationship(
            "Post",
            secondary = posturl_assoc,
            back_populates = "urls"
        )

    def __init__(self, url):
        self.url = url
        #self.post_id = post_id

    def __repr__(self):
        return "Url object with url: {0!r}".format(self.url)

class District(db.Model):
    __tablename__="District"
    district_id = db.Column(db.Integer, primary_key=True)
    #post_id = db.Column(db.String, db.ForeignKey('Post.post_id'))
    state = db.Column(db.String)
    district = db.Column(db.String)
    district_name = db.Column(db.String, index=True)
    incumbent = db.Column(db.String)
    trump_2016 = db.Column(db.Float)
    clinton_2016 = db.Column(db.Float)
    incumbent_party = db.Column(db.String)
    state_fullname = db.Column(db.String)
    dem_candidate = db.Column(db.String)
    rep_candidate = db.Column(db.String)
    dist_type = db.Column(db.Integer)

    district_posts = db.relationship(
        "Post",
        secondary = postdist_assoc,
        back_populates = "districts"
    )

#    district_district_name_index = db.Index('district_district_name_idx', 'district_name')

    #TO ADD IN LATER VERSION: Also possible array of candidates, so don't limit to 2-party
    # district_type = db.Column(db.Integer)
    # dem_candidate = db.Column(db.String)
    # rep_candidate = db.Column(db.String)

    def __init__(self, state, district, district_name, dist_type):
        #self.post_id = post_id
        self.state = state
        self.district = district
        self.district_name = district_name
        self.dist_type = dist_type

    def __repr__(self):
        return "District object with district {0}".format(self.district_name)



### HERE BEGINS SUMMARY/ROLLUP TABLES SERVING AS CACHE FOR OVERVIEW ##

class Dist_Activity_1(db.Model):
    __tablename__ =  'dist_activity_1'
    rank = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(12), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)


class Dist_Activity_2(db.Model):
    __tablename__ =  'dist_activity_2'
    rank = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(12), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)

class Dist_Activity_7(db.Model):
    __tablename__ =  'dist_activity_7'
    rank = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(12), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)

class Dist_Activity_28(db.Model):
    __tablename__ =  'dist_activity_28'
    rank = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(12), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)


#HASHTAG Activity summary tables, split up by time period

class Hash_Activity_1(db.Model):
    __tablename__ =  'hash_activity_1'
    rank = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, nullable=False)
    hashtag = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)


class Hash_Activity_2(db.Model):
    __tablename__ =  'hash_activity_2'
    rank = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, nullable=False)
    hashtag = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)

class Hash_Activity_7(db.Model):
    __tablename__ =  'hash_activity_7'
    rank = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, nullable=False)
    hashtag = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)

class Hash_Activity_28(db.Model):
    __tablename__ =  'hash_activity_28'
    rank = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, nullable=False)
    hashtag = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)


# Summary tables for Top_tweeters function (overview.html)

class Top_Tweeters_1(db.Model):
    __tablename__ =  'top_tweeters_1'
    rank = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25), nullable=False)
    user_scrname = db.Column(db.String(50), nullable=False)
    user_cap_perc = db.Column(db.Float)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)


class Top_Tweeters_2(db.Model):
    __tablename__ =  'top_tweeters_2'
    rank = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25), nullable=False)
    user_scrname = db.Column(db.String(50), nullable=False)
    user_cap_perc = db.Column(db.Float)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Top_Tweeters_7(db.Model):
    __tablename__ =  'top_tweeters_7'
    rank = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25), nullable=False)
    user_scrname = db.Column(db.String(50), nullable=False)
    user_cap_perc = db.Column(db.Float)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Top_Tweeters_28(db.Model):
    __tablename__ =  'top_tweeters_28'
    rank = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25), nullable=False)
    user_scrname = db.Column(db.String(50), nullable=False)
    user_cap_perc = db.Column(db.Float)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Retweeted_Users_1(db.Model):
    __tablename__ =  'retweeted_users_1'
    rank = db.Column(db.Integer, primary_key=True)
    original_author_scrname = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)


class Retweeted_Users_2(db.Model):
    __tablename__ =  'retweeted_users_2'
    rank = db.Column(db.Integer, primary_key=True)
    original_author_scrname = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrnamee)

class Retweeted_Users_7(db.Model):
    __tablename__ =  'retweeted_users_7'
    rank = db.Column(db.Integer, primary_key=True)
    original_author_scrname = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)

class Retweeted_Users_28(db.Model):
    __tablename__ =  'retweeted_users_28'
    rank = db.Column(db.Integer, primary_key=True)
    original_author_scrname = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)

class Retweeted_Tweets_1(db.Model):
    __tablename__ =  'retweeted_tweets_1'
    rank = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(25), nullable=False)
    original_poster = db.Column(db.String(50), nullable=False)
    retweet_count = db.Column(db.Integer, nullable=False)
    # post_html = db.Column(db.Text)
    botscore = db.Column(db.String(50), nullable=False)


    def __init__(self, rank, post_id, original_poster, \
    retweet_count, botscore):
        self.rank = rank
        self.post_id = post_id
        self.original_poster = original_poster
        self.retweet_count = retweet_count
        # self.post_html = post_html
        self.botscore = botscore


    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)


class Retweeted_Tweets_2(db.Model):
    __tablename__ =  'retweeted_tweets_2'
    rank = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(25), nullable=False)
    original_poster = db.Column(db.String(50), nullable=False)
    retweet_count = db.Column(db.Integer, nullable=False)
    # post_html = db.Column(db.Text)
    botscore = db.Column(db.String(50), nullable=False)

    def __init__(self, rank, post_id, original_poster, \
    retweet_count, botscore):
        self.rank = rank
        self.post_id = post_id
        self.original_poster = original_poster
        self.retweet_count = retweet_count
        # self.post_html = post_html
        self.botscore = botscore

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)

class Retweeted_Tweets_7(db.Model):
    __tablename__ =  'retweeted_tweets_7'
    rank = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(25), nullable=False)
    original_poster = db.Column(db.String(50), nullable=False)
    retweet_count = db.Column(db.Integer, nullable=False)
    # post_html = db.Column(db.Text, nullable=False)
    botscore = db.Column(db.String(50), nullable=False)

    def __init__(self, rank, post_id, original_poster, \
    retweet_count, botscore):
        self.rank = rank
        self.post_id = post_id
        self.original_poster = original_poster
        self.retweet_count = retweet_count
        # self.post_html = post_html
        self.botscore = botscore

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)

class Retweeted_Tweets_28(db.Model):
    __tablename__ =  'retweeted_tweets_28'
    rank = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(25), nullable=False)
    original_poster = db.Column(db.String(50), nullable=False)
    retweet_count = db.Column(db.Integer, nullable=False)
    # post_html = db.Column(db.Text, nullable=False)
    botscore = db.Column(db.String(50), nullable=False)

    def __init__(self, rank, post_id, original_poster, \
    retweet_count, botscore):
        self.rank = rank
        self.post_id = post_id
        self.original_poster = original_poster
        self.retweet_count = retweet_count
        # self.post_html = post_html
        self.botscore = botscore

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)
