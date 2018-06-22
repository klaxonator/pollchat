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

    def __init__(self, post_id, user_id, text, created_at, reply_to_user_id,
     reply_to_scrname, reply_to_status_id, retweet_count,
     favorite_count, is_retweet, original_tweet_id, original_tweet_retweets,
     original_text, original_tweet_created_at, original_tweet_likes,
     original_author_id, original_author_scrname, polarity, polarity_val):

        self.post_id = post_id
        self.user_id = user_id
        self.text = text
        self.created_at = created_at
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
    hashtag = Column(String)
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
    district_name = Column(String)
    incumbent = Column(String)
    trump_2016 = Column(Float)
    clinton_2016 = Column(Float)
    incumbent_party = Column(String)

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

    def __init__(self, state, district, district_name):
        #self.post_id = post_id
        self.state = state
        self.district = district
        self.district_name = district_name

    def __repr__(self):
        return "District object with district {0}".format(self.district_name)


###INDEXES




class DateData(Base):
    __tablename__="DateData"
    date_str = Column(String, primary_key=True)
    az01_hashdict = Column(String)
    az01_userdict = Column(String)
    az02_hashdict = Column(String)
    az02_userdict = Column(String)
    az06_hashdict = Column(String)
    az06_userdict = Column(String)
    az09_hashdict = Column(String)
    az09_userdict = Column(String)
    ar02_hashdict = Column(String)
    ar02_userdict = Column(String)
    ca04_hashdict = Column(String)
    ca04_userdict = Column(String)
    ca07_hashdict = Column(String)
    ca07_userdict = Column(String)
    ca10_hashdict = Column(String)
    ca10_userdict = Column(String)
    ca21_hashdict = Column(String)
    ca21_userdict = Column(String)
    ca25_hashdict = Column(String)
    ca25_userdict = Column(String)
    ca39_hashdict = Column(String)
    ca39_userdict = Column(String)
    ca45_hashdict = Column(String)
    ca45_userdict = Column(String)
    ca48_hashdict = Column(String)
    ca48_userdict = Column(String)
    ca49_hashdict = Column(String)
    ca49_userdict = Column(String)
    ca50_hashdict = Column(String)
    ca50_userdict = Column(String)
    co06_hashdict = Column(String)
    co06_userdict = Column(String)
    ct05_hashdict = Column(String)
    ct05_userdict = Column(String)
    fl07_hashdict = Column(String)
    fl07_userdict = Column(String)
    fl15_hashdict = Column(String)
    fl15_userdict = Column(String)
    fl16_hashdict = Column(String)
    fl16_userdict = Column(String)
    fl18_hashdict = Column(String)
    fl18_userdict = Column(String)
    fl25_hashdict = Column(String)
    fl25_userdict = Column(String)
    fl26_hashdict = Column(String)
    fl26_userdict = Column(String)
    fl27_hashdict = Column(String)
    fl27_userdict = Column(String)
    ga06_hashdict = Column(String)
    ga06_userdict = Column(String)
    ga07_hashdict = Column(String)
    ga07_userdict = Column(String)
    ia01_hashdict = Column(String)
    ia01_userdict = Column(String)
    ia03_hashdict = Column(String)
    ia03_userdict = Column(String)
    il06_hashdict = Column(String)
    il06_userdict = Column(String)
    il12_hashdict = Column(String)
    il12_userdict = Column(String)
    il13_hashdict = Column(String)
    il13_userdict = Column(String)
    il14_hashdict = Column(String)
    il14_userdict = Column(String)
    in02_hashdict = Column(String)
    in02_userdict = Column(String)
    ks02_hashdict = Column(String)
    ks02_userdict = Column(String)
    ks03_hashdict = Column(String)
    ks03_userdict = Column(String)
    ky06_hashdict = Column(String)
    ky06_userdict = Column(String)
    me02_hashdict = Column(String)
    me02_userdict = Column(String)
    mi01_hashdict = Column(String)
    mi01_userdict = Column(String)
    mi06_hashdict = Column(String)
    mi06_userdict = Column(String)
    mi07_hashdict = Column(String)
    mi07_userdict = Column(String)
    mi08_hashdict = Column(String)
    mi08_userdict = Column(String)
    mi11_hashdict = Column(String)
    mi11_userdict = Column(String)
    mn01_hashdict = Column(String)
    mn01_userdict = Column(String)
    mn02_hashdict = Column(String)
    mn02_userdict = Column(String)
    mn03_hashdict = Column(String)
    mn03_userdict = Column(String)
    mn07_hashdict = Column(String)
    mn07_userdict = Column(String)
    mn08_hashdict = Column(String)
    mn08_userdict = Column(String)
    mo02_hashdict = Column(String)
    mo02_userdict = Column(String)
    mt00_hashdict = Column(String)
    mt00_userdict = Column(String)
    nc02_hashdict = Column(String)
    nc02_userdict = Column(String)
    nc08_hashdict = Column(String)
    nc08_userdict = Column(String)
    nc09_hashdict = Column(String)
    nc09_userdict = Column(String)
    nc13_hashdict = Column(String)
    nc13_userdict = Column(String)
    ne02_hashdict = Column(String)
    ne02_userdict = Column(String)
    nh01_hashdict = Column(String)
    nh01_userdict = Column(String)
    nh02_hashdict = Column(String)
    nh02_userdict = Column(String)
    nj02_hashdict = Column(String)
    nj02_userdict = Column(String)
    nj03_hashdict = Column(String)
    nj03_userdict = Column(String)
    nj05_hashdict = Column(String)
    nj05_userdict = Column(String)
    nj07_hashdict = Column(String)
    nj07_userdict = Column(String)
    nj11_hashdict = Column(String)
    nj11_userdict = Column(String)
    nm02_hashdict = Column(String)
    nm02_userdict = Column(String)
    nv03_hashdict = Column(String)
    nv03_userdict = Column(String)
    nv04_hashdict = Column(String)
    nv04_userdict = Column(String)
    ny01_hashdict = Column(String)
    ny01_userdict = Column(String)
    ny11_hashdict = Column(String)
    ny11_userdict = Column(String)
    ny19_hashdict = Column(String)
    ny19_userdict = Column(String)
    ny22_hashdict = Column(String)
    ny22_userdict = Column(String)
    ny24_hashdict = Column(String)
    ny24_userdict = Column(String)
    oh01_hashdict = Column(String)
    oh01_userdict = Column(String)
    oh10_hashdict = Column(String)
    oh10_userdict = Column(String)
    oh12_hashdict = Column(String)
    oh12_userdict = Column(String)
    oh14_hashdict = Column(String)
    oh14_userdict = Column(String)
    oh15_hashdict = Column(String)
    oh15_userdict = Column(String)
    pa01_hashdict = Column(String)
    pa01_userdict = Column(String)
    pa05_hashdict = Column(String)
    pa05_userdict = Column(String)
    pa06_hashdict = Column(String)
    pa06_userdict = Column(String)
    pa07_hashdict = Column(String)
    pa07_userdict = Column(String)
    pa08_hashdict = Column(String)
    pa08_userdict = Column(String)
    pa10_hashdict = Column(String)
    pa10_userdict = Column(String)
    pa14_hashdict = Column(String)
    pa14_userdict = Column(String)
    pa16_hashdict = Column(String)
    pa16_userdict = Column(String)
    pa17_hashdict = Column(String)
    pa17_userdict = Column(String)
    sc01_hashdict = Column(String)
    sc01_userdict = Column(String)
    sc05_hashdict = Column(String)
    sc05_userdict = Column(String)
    tx07_hashdict = Column(String)
    tx07_userdict = Column(String)
    tx21_hashdict = Column(String)
    tx21_userdict = Column(String)
    tx23_hashdict = Column(String)
    tx23_userdict = Column(String)
    tx32_hashdict = Column(String)
    tx32_userdict = Column(String)
    ut04_hashdict = Column(String)
    ut04_userdict = Column(String)
    va02_hashdict = Column(String)
    va02_userdict = Column(String)
    va05_hashdict = Column(String)
    va05_userdict = Column(String)
    va07_hashdict = Column(String)
    va07_userdict = Column(String)
    va10_hashdict = Column(String)
    va10_userdict = Column(String)
    wa03_hashdict = Column(String)
    wa03_userdict = Column(String)
    wa05_hashdict = Column(String)
    wa05_userdict = Column(String)
    wa08_hashdict = Column(String)
    wa08_userdict = Column(String)
    wi01_hashdict = Column(String)
    wi01_userdict = Column(String)
    wi03_hashdict = Column(String)
    wi03_userdict = Column(String)
    wi06_hashdict = Column(String)
    wi06_userdict = Column(String)
    wi07_hashdict = Column(String)
    wi07_userdict = Column(String)
    wv03_hashdict = Column(String)
    wv03_userdict = Column(String)
    overview_hashdict = Column(String)
    overview_userdict = Column(String)

    def __init__(self, date_str):
        self.date_str = date_str

    def __repr__(self):
        return "Datedata object with date {0}, and data dictionaries for districts and overview".format(self.date_str)
