from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, func, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

postdist_assoc = Table('postdist_assoc', Base.metadata,
        Column('post_id', String, ForeignKey('Post.post_id')),
        Column('district_name', String, ForeignKey('District.district_name')),
        Index('postdist_postdist_idx', 'post_id', 'district_name'),
        Index('postdist_distpost_idx', 'district_name', 'post_id')
        )


posthash_assoc = Table('posthash_assoc', Base.metadata,
            Column('post_id', String, ForeignKey('Post.post_id')),
            Column('hashtag', String, ForeignKey('Hashtag.hashtag')),
            Index('posthash_posthash_idx', 'post_id', 'hashtag'),
            Index('posthash_posthash_idx', 'hashtag', 'post_id')
            )

posturl_assoc = Table('posturl_assoc', Base.metadata,
            Column('post_id', String, ForeignKey('Post.post_id')),
            Column('url_id', String, ForeignKey('Url.url_id')),
            Index('posturl_posturl_idx', 'post_id', 'url_id'),
            Index('posthash_posturl_idx', 'url_id', 'post_id')
            )




class User(Base):
    __tablename__='User'
    user_id = Column(String, primary_key=True)
    user_scrname = Column(String, nullable=False)
    user_name = Column(String)
    user_location = Column(String)
    user_created = Column(String)
    user_followers = Column(Integer)
    user_friends = Column(Integer)
    user_statuses = Column(Integer)
    user_botprob = Column(Float)
    user_botprob_cap = Column(Float)
    user_cap_perc = Column(Float)

    user_posts = relationship("Post", back_populates="user")
    user_user_scrname_index = Index('user_user_scrname_idx', 'user_scrname')

    def __init__(self, user_id, user_scrname, user_name, user_location, user_created, user_followers, user_friends, user_statuses):
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_name = user_name
        self.user_location = user_location
        self.user_created = user_created
        self.user_followers = user_followers
        self.user_friends = user_friends
        self.user_statuses = user_statuses


    def __repr__(self):
        return "Object: Twitter User with id {0!r} and screen name {1!r}".format(self.user_id, self.user_scrname)

class Post(Base):
    __tablename__='Post'
    post_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('User.user_id'), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    created_at_dt = Column(String)
    reply_to_user_id = Column(String)
    reply_to_scrname = Column(String)
    reply_to_status_id = Column(String)
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)

    is_retweet = Column(Integer)
    original_tweet_id = Column(String)
    original_tweet_retweets = Column(Integer)
    original_text = Column(String)
    original_tweet_created_at = Column(String)
    original_tweet_likes = Column(Integer)
    original_author_id = Column(String)
    original_author_scrname = Column(String)

    tweet_html = Column(String)

    polarity = Column(Integer)
    polarity_val = Column(String)

    user = relationship("User", back_populates="user_posts")
    districts = relationship(
        "District",
        secondary = postdist_assoc,
        back_populates = "district_posts"
        )
    hashtags = relationship(
        "Hashtag",
        secondary = posthash_assoc,
        back_populates = "hashtag_posts"
        )
    urls = relationship(
        "Url",
        secondary = posturl_assoc,
        back_populates = "url_posts"
        )

    post_created_at_index = Index('post_created_at_idx', 'created_at')

    def __init__(self, post_id, user_id, text, created_at, created_at_dt, reply_to_user_id,
     reply_to_scrname, reply_to_status_id, retweet_count,
     favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
     original_text, original_tweet_created_at, original_tweet_likes,
     original_author_id, original_author_scrname, polarity, polarity_val):

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
        self.original_tweet_id = original_tweet_id
        self.original_tweet_retweets = original_tweet_retweets
        self.original_text = original_text
        self.original_tweet_created_at = original_tweet_created_at
        self.original_tweet_likes = original_tweet_likes
        self.original_author_id = original_author_id
        self.original_author_scrname = original_author_scrname

        self.polarity = polarity
        self.polarity_val = polarity_val
        # self.tweet_html = tweet_html


    def __repr__(self):
        return "Object: Tweet by {0!r}, with ID {1!r}".format(self.user_id, self.post_id)

class Hashtag(Base):
    __tablename__='Hashtag'
    hash_id = Column(Integer, primary_key=True)
    hashtag = Column(String, index=True)
    #post_id = Column(String, ForeignKey('Post.post_id'))
    hashtag_posts = relationship(
            "Post",
            secondary = posthash_assoc,
            back_populates = "hashtags"
        )
    hashtag_hashtag_index = Index('hashtag_hashtag_idx', 'hashtag')

    def __init__(self, hashtag):
        self.hashtag = hashtag
        #self.post_id = post_id

    def __repr__(self):
        return "Hashtag object with hashtag: {0!r}".format(self.hashtag)

class Url(Base):
    __tablename__='Url'
    url_id = Column(Integer, primary_key=True)
    url = Column(String)
    #post_id = Column(String, ForeignKey('Post.post_id'))
    url_posts = relationship(
            "Post",
            secondary = posturl_assoc,
            back_populates = "urls"
        )

    def __init__(self, url):
        self.url = url
        #self.post_id = post_id

    def __repr__(self):
        return "Url object with url: {0!r}".format(self.url)

class District(Base):
    __tablename__="District"
    district_id = Column(Integer, primary_key=True)
    #post_id = Column(String, ForeignKey('Post.post_id'))
    state = Column(String)
    district = Column(String)
    district_name = Column(String, index=True)
    incumbent = Column(String)
    trump_2016 = Column(Float)
    clinton_2016 = Column(Float)
    incumbent_party = Column(String)
    state_fullname = Column(String)
    dem_candidate = Column(String)
    rep_candidate = Column(String)
    dist_type = Column(Integer)

    district_posts = relationship(
        "Post",
        secondary = postdist_assoc,
        back_populates = "districts"
    )

    district_district_name_index = Index('district_district_name_idx', 'district_name')

    #TO ADD IN LATER VERSION: Also possible array of candidates, so don't limit to 2-party
    # district_type = Column(Integer)
    # dem_candidate = Column(String)
    # rep_candidate = Column(String)

    def __init__(self, state, district, district_name, dist_type):
        #self.post_id = post_id
        self.state = state
        self.district = district
        self.district_name = district_name
        self.dist_type = dist_type

    def __repr__(self):
        return "District object with district {0}".format(self.district_name)


## SUMMARY/ROLLUP (CACHE) TABLES for OVERVIEW PAGE



class Dist_Activity_1(Base):
    __tablename__ =  'dist_activity_1'
    rank = Column(Integer, primary_key=True)
    district_name = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)


class Dist_Activity_2(Base):
    __tablename__ =  'dist_activity_2'
    rank = Column(Integer, primary_key=True)
    district_name = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)

class Dist_Activity_7(Base):
    __tablename__ =  'dist_activity_7'
    rank = Column(Integer, primary_key=True)
    district_name = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)

class Dist_Activity_28(Base):
    __tablename__ =  'dist_activity_28'
    rank = Column(Integer, primary_key=True)
    district_name = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, district_name, count):
        self.rank = rank
        self.district_name = district_name
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for district: {}".\
        format(self.district_name)


#HASHTAG Activity summary tables, split up by time period

class Hash_Activity_1(Base):
    __tablename__ =  'hash_activity_1'
    rank = Column(Integer, primary_key=True)
    hash_id = Column(Integer, nullable=False)
    hashtag = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)


class Hash_Activity_2(Base):
    __tablename__ =  'hash_activity_2'
    rank = Column(Integer, primary_key=True)
    hash_id = Column(Integer, nullable=False)
    hashtag = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)

class Hash_Activity_7(Base):
    __tablename__ =  'hash_activity_7'
    rank = Column(Integer, primary_key=True)
    hash_id = Column(Integer, nullable=False)
    hashtag = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)

class Hash_Activity_28(Base):
    __tablename__ =  'hash_activity_28'
    rank = Column(Integer, primary_key=True)
    hash_id = Column(Integer, nullable=False)
    hashtag = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, hash_id, hashtag, count):
        self.rank = rank
        self.hash_id = hash_id
        self.hashtag = hashtag
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for hashtag: {}".\
        format(self.hashtag)


# Summary tables for Top_tweeters function (overview.html)

class Top_Tweeters_1(Base):
    __tablename__ =  'top_tweeters_1'
    rank = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_scrname = Column(String, nullable=False)
    user_cap_perc = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)


class Top_Tweeters_2(Base):
    __tablename__ =  'top_tweeters_2'
    rank = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_scrname = Column(String, nullable=False)
    user_cap_perc = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Top_Tweeters_7(Base):
    __tablename__ =  'top_tweeters_7'
    rank = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_scrname = Column(String, nullable=False)
    user_cap_perc = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Top_Tweeters_28(Base):
    __tablename__ =  'top_tweeters_28'
    rank = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_scrname = Column(String, nullable=False)
    user_cap_perc = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, user_id, user_scrname, user_cap_perc, count):
        self.rank = rank
        self.user_id = user_id
        self.user_scrname = user_scrname
        self.user_cap_perc = user_cap_perc
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for user: {}".\
        format(self.user_scrname)

class Retweeted_Users_1(Base):
    __tablename__ =  'retweeted_users_1'
    rank = Column(Integer, primary_key=True)
    original_author_scrname = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)


class Retweeted_Users_2(Base):
    __tablename__ =  'retweeted_users_2'
    rank = Column(Integer, primary_key=True)
    original_author_scrname = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrnamee)

class Retweeted_Users_7(Base):
    __tablename__ =  'retweeted_users_7'
    rank = Column(Integer, primary_key=True)
    original_author_scrname = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)

class Retweeted_Users_28(Base):
    __tablename__ =  'retweeted_users_28'
    rank = Column(Integer, primary_key=True)
    original_author_scrname = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, original_author_scrname, count):
        self.rank = rank
        self.original_author_scrname = original_author_scrname
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for user: {}".\
        format(self.original_author_scrname)

class Retweeted_Tweets_1(Base):
    __tablename__ =  'retweeted_tweets_1'
    rank = Column(Integer, primary_key=True)
    post_id = Column(String, nullable=False)
    original_post_id = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, post_id, original_post_id, count):
        self.rank = rank
        self.post_id = post_id
        self.original_post_id = original_post_id
        self.count = count

    def __repr__(self):
        return "Object: 1 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)


class Retweeted_Tweets_2(Base):
    __tablename__ =  'retweeted_tweets_2'
    rank = Column(Integer, primary_key=True)
    post_id = Column(String, nullable=False)
    original_post_id = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, post_id, original_post_id, count):
        self.rank = rank
        self.post_id = post_id
        self.original_post_id = original_post_id
        self.count = count

    def __repr__(self):
        return "Object: 2 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)

class Retweeted_Tweets_7(Base):
    __tablename__ =  'retweeted_tweets_7'
    rank = Column(Integer, primary_key=True)
    post_id = Column(String, nullable=False)
    original_post_id = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, post_id, original_post_id, count):
        self.rank = rank
        self.post_id = post_id
        self.original_post_id = original_post_id
        self.count = count

    def __repr__(self):
        return "Object: 7 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)

class Retweeted_Tweets_28(Base):
    __tablename__ =  'retweeted_tweets_28'
    rank = Column(Integer, primary_key=True)
    post_id = Column(String, nullable=False)
    original_post_id = Column(String, nullable=False)
    count = Column(Integer, nullable=False)

    def __init__(self, rank, post_id, original_post_id, count):
        self.rank = rank
        self.post_id = post_id
        self.original_post_id = original_post_id
        self.count = count

    def __repr__(self):
        return "Object: 28 day activity summary (# of tweets) for tweet: {}".\
        format(self.post_id)
