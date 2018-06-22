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
    user_scrname = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String)
    user_location = db.Column(db.String)
    user_created = db.Column(db.String)
    user_followers = db.Column(db.Integer)
    user_friends = db.Column(db.Integer)
    user_statuses = db.Column(db.Integer)
    user_botprob = db.Column(db.Float)
    user_botprob_cap = db.Column(db.Float)
    user_cap_perc = db.Column(db.Float)

    user_posts = db.relationship("Post", back_populates="user")

    user_user_scrname_index = db.Index('user_user_scrname_idx', 'user_scrname')
    user_user_cap_perc_index = db.Index('user_user_cap_perc_idx', 'user_scrname')

    # def __init__(self, user_id, user_scrname, user_name, user_location, user_created, user_followers, user_friends, user_statuses):
    #     self.user_id = user_id
    #     self.user_scrname = user_scrname
    #     self.user_name = user_name
    #     self.user_location = user_location
    #     self.user_created = user_created
    #     self.user_followers = user_followers
    #     self.user_friends = user_friends
    #     self.user_statuses = user_statuses

    def __repr__(self):
        return "Object: Twitter User with id {0!r} and screen name {1!r}".format(self.user_id, self.user_scrname)



class Post(db.Model):
    __tablename__='Post'
    post_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('User.user_id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False)
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
    original_author_scrname = db.Column(db.String)

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

    post_created_at_index = db.Index('post_created_at_idx', 'created_at')
    post_original_author_scrname_index = db.Index('post_original_author_scrname_idx',
        'original_author_scrname')


    def __init__(self, post_id, user_id, text, created_at, reply_to_user_id,
     reply_to_scrname, reply_to_status_id, retweet_count,
     favorite_count, is_retweet, original_text, original_author_id,
     original_author_scrname, polarity, polarity_val):
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
    hashtag = db.Column(db.String)
    #post_id = db.Column(db.String, db.ForeignKey('Post.post_id'))
    hashtag_posts = db.relationship(
            "Post",
            secondary = posthash_assoc,
            back_populates = "hashtags"
        )
    hashtag_hashtag_index = db.Index('hashtag_hashtag_idx','hashtag')

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
    district_name = db.Column(db.String)
    incumbent = db.Column(db.String)
    trump_2016 = db.Column(db.Float)
    clinton_2016 = db.Column(db.Float)
    incumbent_party = db.Column(db.String)
    state_fullname = db.Column(db.String)
    dem_candidate = db.Column(db.String)
    rep_candidate = db.Column(db.String)

    district_posts = db.relationship(
        "Post",
        secondary = postdist_assoc,
        back_populates = "districts"
    )

    district_district_name_index = db.Index('district_district_name_idx', 'district_name')

    #TO ADD IN LATER VERSION: Also possible array of candidates, so don't limit to 2-party
    # district_type = db.Column(db.Integer)
    # dem_candidate = db.Column(db.String)
    # rep_candidate = db.Column(db.String)

    def __init__(self, state, district, district_name):
        #self.post_id = post_id
        self.state = state
        self.district = district
        self.district_name = district_name

    def __repr__(self):
        return "District object with district {0}".format(self.district_name)
