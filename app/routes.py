from flask import render_template, flash, redirect, url_for, request
from flask_wtf import csrf
from app import app, db
from app.forms import HashtagSearchForm, PhraseSearchForm, DistrictForm, \
AllCongSearchForm, ChangeTimeForm, BotSearchForm, SenForm
from app.models import User, Post, District, Hashtag, Url, District_graphs, Post_extended
from sqlalchemy import func, Date, cast
from sqlalchemy.dialects.sqlite import DATETIME
from datetime import datetime, timedelta, date
from app.helpers import stringtime, get_tweet, test_insert, test_hashgraph_data, \
test_usergraph_data, distlist, get_tweet_datetime, get_tweet_list, \
get_tweet_list_nodist, Logger, skip_list
import app.graph_functions as gf
import sys
import pickle

sys.stdout = Logger("logs/pollchat_stdout.txt")


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    url = request.path

    return render_template('index.html', title ='Home', d_form=DistrictForm(), \
    h_form=HashtagSearchForm(), p_form=PhraseSearchForm(), all_form=AllCongSearchForm(),\
    botform=BotSearchForm(), sen_form=SenForm(), url=url)

@app.route('/select_district', methods = ['GET', 'POST'])
def select_district():
    d_form = DistrictForm()
    sen_form = SenForm()
#    if request.method == 'POST':
    if d_form.is_submitted():
        dynamic = d_form.select_district.data
        time_delta = d_form.district_time_delta.data
        flash('Your request({0}) has been submitted, with delta(days)={1}'.format(dynamic, \
        time_delta))
        return redirect(url_for('district', dynamic=dynamic, time_delta=time_delta))

    if sen_form.is_submitted():
        dynamic = sen_form.select_district.data
        time_delta = sen_form.district_time_delta.data
        flash('Your request({0}) has been submitted, with delta(days)={1}'.format(dynamic, \
        time_delta))
        return redirect(url_for('district', dynamic=dynamic, time_delta=time_delta))

    return render_template('index.html', title='Home', d_form=d_form, \
    p_form=PhraseSearchForm(), h_form=HashtagSearchForm(), all_form=AllCongSearchForm(),\
    botform=BotSearchForm(), sen_form=SenForm())

@app.route('/district/<dynamic>', methods=['GET', 'POST'])
def district(dynamic):
    print('starting district {}'.format(dynamic))

    time_delta = request.args.get('time_delta')
    url = request.path

    str_time_range = stringtime(time_delta)

    #Set str_today within page call, so is correct (today)
    # NOTE: Possibly faster to do this w/i hash_pickled db lookup
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight
    str_today = today.strftime("%Y-%m-%d %H:%M:%S")         # string version of midnight

    # Most frequently used hashtags column
    dist_hashes = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.districts).join(Post.hashtags).\
    filter(District.district_name==dynamic).\
    filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).\
    order_by(func.count(Hashtag.hashtag).desc()).all()

    print('got dist_hashes')

    # Most active tweeters column
    top_tweeters = db.session.query(User.user_scrname, func.count(User.user_scrname),\
    User.user_cap_perc, User.user_id).\
    join(Post.user).join(Post.districts).\
    filter(District.district_name==dynamic).\
    filter(Post.created_at >= str_time_range).\
    group_by(User.user_id).\
    order_by(func.count(User.user_id).desc()).all()

    print('got top_tweeters')

    # Most frequently retweeted users column )
    most_retweeted = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.districts).\
    filter(District.district_name==dynamic).\
    filter(Post.created_at >= str_time_range).\
    filter(Post.original_author_scrname != "").\
    group_by(Post.original_author_scrname).\
    order_by(func.count(Post.original_author_scrname).desc()).all()

    #Get botscore for top five most-retweeted users, create list of [name, retweet
    #numbers, botscore] to send to template
    most_retweeted_list = []

    for item in most_retweeted[0:5]:
        tweeter = []
        tweeter.append(item[0])
        tweeter.append(item[1])

        # Get botscore for original authors
        botscore = db.session.query(User.user_cap_perc).\
        filter(User.user_scrname==item[0]).first()

        if botscore:
            tweeter.append(botscore[0])
        else:
            tweeter.append("Not yet in database")
        most_retweeted_list.append(tweeter)

    print('got most_retweeted')

    # Most retweeted tweets column

    # Gets list of tweets in time period, ordered by most-retweeted (NOTE: many
    # or most of these retweets may be previous to this period)
    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text, Post.original_text).\
    join(Post.districts).join(Post.user).\
    filter(District.district_name==dynamic).filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    # Use helper function to Get botscore for top five most-retweeted tweets,
    # create list of [post_id, name,retweet numbers, botscore]

    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets, dynamic)

    #most_retweeted_tweet_list_dated = get_tweet_list_dated(db_search_object, time_delta)


    print('got most_retweeted_list')

    #Get basic district object for district info
    dist_obj = db.session.query(District.state_fullname, District.district, \
    District.incumbent, District.incumbent_party, District.clinton_2016, \
    District.trump_2016, District.dem_candidate, District.rep_candidate).\
    filter(District.district_name==dynamic).first()

    print('got dist_obj')

    #Using 3-day index for top-row hashtags to spotlight
    #hash_table_rows = gf.get_hash_rows(dynamic)
    hash_pickled = db.session.query(District_graphs.chart_rows).\
    filter(District_graphs.reference_date==str_today).\
    filter(District_graphs.district_name==dynamic).first()

    if hash_pickled != None:
        hash_table_rows = pickle.loads(hash_pickled[0])
    else:
        hash_table_rows = gf.get_hash_rows(dynamic)

    print(hash_table_rows)

    print('got chart_rows')

    return render_template('district.html', dynamic=dynamic, time_delta=time_delta, \
    url=url, dist_hashes=dist_hashes, top_tweeters=top_tweeters, \
    most_retweeted=most_retweeted, most_retweeted_tweets=most_retweeted_tweets, \
    t_form=ChangeTimeForm(), get_tweet=get_tweet, dist_obj=dist_obj, \
    test_insert=test_insert, distlist=distlist, hash_table_rows=hash_table_rows,\
    most_retweeted_list=most_retweeted_list, most_retweeted_tweet_list=\
    most_retweeted_tweet_list)

@app.route('/tweet/<post_id>/tweet_popup', methods = ['GET', 'POST'])
def tweet_popup(post_id):

    return render_template('tweet_popup.html', post_id=post_id, \
    get_tweet=get_tweet, test_insert=test_insert)

@app.route('/hashtag_search', methods = ['GET', 'POST'])
def hashtag_search():
    h_form = HashtagSearchForm(meta={'csrf': False})
    if h_form.validate_on_submit():
        dynamic = h_form.hashtag_search.data
        time_delta = h_form.hashtag_time_delta.data
        flash('Your hashtag({0}) has been submitted, with delta(days)={1}'.format(dynamic, \
        time_delta))

        dynamic = dynamic.lstrip('#').lower()

        if db.session.query(Hashtag).filter(Hashtag.hashtag == dynamic).first():
            return redirect(url_for('hashtag', dynamic=dynamic, time_delta=time_delta))
        else:
            return redirect(url_for('doesnt_exist', dynamic=dynamic))

    return render_template('index.html', title ='Home', h_form=h_form, \
    p_form=PhraseSearchForm(), d_form=DistrictForm(), all_form=AllCongSearchForm(),\
    botform=BotSearchForm(), sen_form=SenForm())

@app.route('/hashtag/<dynamic>', methods=['GET', 'POST'])
def hashtag(dynamic):

    print('starting hashtag {}'.format(dynamic))

    time_delta = request.args.get('time_delta')
    url = request.path

    str_time_range = stringtime(time_delta)

    #Where is this hashtag used column
    top_districts=db.session.query(District.district_id, District.district_name, \
    func.count(District.district_id), District.state_fullname, District.district).\
    join(Post.districts).join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at_dt >= str_time_range).\
    group_by(District.district_id).order_by(func.count(District.district_id).\
    desc()).all()

    # conn = db.engine.connect()
    # top_dist_q = '''SELECT res.district_name, count(res.district_name) as ct
    #                      FROM (
    #                         SELECT post_id, district_name
    #                         FROM  Post_extended pe
    #                         WHERE pe.hashtag = '{0}'
    #                             and pe.created_at_dt >= '{1}') res
    #                      GROUP BY res.district_name
    #                      ORDER BY ct DESC;'''.format(dynamic, str_time_range)
    # print(top_dist_q)
    #
    # top_districts = conn.execute(top_dist_q).fetchall()
    #
    # top_district = db.session.query(District.state_fullname, District.district).\
    #             filter(District.district_name==top_districts[0][0]).first()

    # conn.close()

    print("got top districts")

    # "Who uses this hashtag" column
    top_users=db.session.query(User.user_scrname, func.count(User.user_scrname), \
    User.user_cap_perc, User.user_id).\
    join(Post.user).join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at_dt >= str_time_range).\
    group_by(User.user_id).\
    order_by(func.count(User.user_id).desc()).all()

    print("got top users")

    # Data for positive/negative chart
    valences = db.session.query(Post.polarity_val, func.count(Post.polarity_val)).\
    join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at_dt >= str_time_range).\
    group_by(Post.polarity_val).all()

    valences_datatable = [['Attitude', 'Number of Tweets']]
    for item in valences:
        valences_datatable.append([item[0], item[1]])

    print("got valences")

    # Most retweeted tweets column
    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text, Post.original_text).\
    join(Post.hashtags).join(Post.user).\
    filter(Hashtag.hashtag==dynamic).filter(Post.created_at_dt >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    print("got most retweeted tweets")

    #Get botscore for top five most-retweeted tweets, create list of [post_id, name,
    # retweet numbers, botscore] to send to template
    most_retweeted_tweet_list = get_tweet_list_nodist(most_retweeted_tweets)

    print("got most retweeted tweets")

    return render_template('hashtag.html', t_form=ChangeTimeForm(), url=url, \
    dynamic=dynamic, time_delta=time_delta, top_districts=top_districts, \
    top_users=top_users, valences=valences, valences_datatable=valences_datatable,
    most_retweeted_tweets=most_retweeted_tweets, get_tweet=get_tweet, \
    most_retweeted_tweet_list=most_retweeted_tweet_list)

@app.route('/all_search', methods = ['GET', 'POST'])
def all_search():
    all_form = AllCongSearchForm()
    if all_form.is_submitted():
        dynamic = all_form.scope_search.data
        time_delta = all_form.allcong_time_delta.data
        flash('Your request({0}) has been submitted, with delta(days)={1}'.format(dynamic, \
        time_delta))
        return redirect(url_for('overview', dynamic=dynamic, time_delta=time_delta))
    return render_template('index.html', title ='Home', all_form=all_form, \
    h_form=HashtagSearchForm(), p_form=PhraseSearchForm(), d_form=DistrictForm(),\
    botform=BotSearchForm(), sen_form=SenForm())

@app.route('/overview/<dynamic>', methods = ['GET', 'POST'])
def overview(dynamic):

    print('starting district group {}'.format(dynamic))
    time_delta = request.args.get('time_delta')
    url = request.path
    str_time_range = stringtime(time_delta)

    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight
    str_today = today.strftime("%Y-%m-%d %H:%M:%S")         # string version of midnight

    conn = db.engine.connect()

    # GET 10-day table data for hashtag chart from graph_functions module
    # RETURN THIS TO TEMPLATE







    # Get a desc-ordered list of all hashtags being used in all districts
    # Object returns (hashtag, count)
    all_hashes_result = conn.execute('SELECT hashtag, count FROM hash_activity_{0}_{1};'.\
    format(dynamic, time_delta)).fetchall()

    #RETURN THIS TO TEMPLATE
    all_hashes = []

    for item in all_hashes_result:
        all_hashes.append(item)

    print("got all_hashes")

    #Get a list of tophashtags without district names
    # RETURN THIS TO TEMPLATE
    hashes_no_dists = []
    counter = 0
    for item in all_hashes:
        if item[0] not in distlist:
            hashes_no_dists.append(item)
            counter += 1
        if counter == 20:
            break



    # RETURN THIS TO TEMPLATE
    all_tweets = db.session.query(func.count(Post.post_id)).\
    filter(Post.created_at >= str_time_range).first()

    print("got all tweets")


    #Get list of most active districts

    active_dists_result = conn.execute('SELECT district_name, count FROM dist_activity_{0}_{1};'.\
    format(dynamic, time_delta)).fetchall()

    # RETURN THIS TO TEMPLATE
    most_active = []

    for item in active_dists_result:
        most_active.append(item)


    print("got most_active")

    # Get a desc-ordered list of top-volume Tweeters
    top_tweeters_result = conn.execute('SELECT user_scrname, count, user_cap_perc FROM top_tweeters_{0}_{1};'.\
    format(dynamic, time_delta)).fetchall()

    # RETURN THIS TO TEMPLATE
    top_tweeters = []

    for item in top_tweeters_result:
        new_row = []
        new_row.append(item[0])
        new_row.append(item[1])
        if item[2] == -1.0:
            new_row.append("Not yet in database")
        else:
            new_row.append(item[2])
        top_tweeters.append(new_row)


    print("got top_tweeters")

    retweeted_users_result = conn.execute('SELECT original_author_scrname, count FROM retweeted_users_{0}_{1};'.\
    format(dynamic, time_delta)).fetchall()

    # RETURN THIS TO TEMPLATE
    retweeted_users = []

    for item in retweeted_users_result:
        retweeted_users.append(item)



    print("got retweeted users")

    retweeted_tweets_result = conn.execute('SELECT post_id, original_poster, retweet_count, botscore FROM retweeted_tweets_{0}_{1};'.\
    format(dynamic, time_delta)).fetchall()

    # RETURN THIS TO TEMPLATE
    most_retweeted_tweet_list = []
    tweet_count = 0
    # Each item (tuple) is post_id, poster, count, botscore. Still need HTML
    for item in retweeted_tweets_result:

        # if original_author_scrname is in skip list, skip it
        if item[1].lower() in skip_list:
            continue

        #create list with attributes
        holding_list = []
        for attribute in item:
            holding_list.append(attribute)

        # Get Tweet HTML, add to list
        try:
            tweet_text = get_tweet(item[0])
            holding_list.append(tweet_text)
        except:
            holding_list.append("Can't retrieve tweet")

        most_retweeted_tweet_list.append(holding_list)
        tweet_count += 1
        if tweet_count == 5:
            break

    print("got most retweeted tweets")


    hash_pickled = db.session.query(District_graphs.chart_rows).\
    filter(District_graphs.reference_date==str_today).\
    filter(District_graphs.district_name==dynamic).first()

    if hash_pickled != None:
        hashtable_all = pickle.loads(hash_pickled[0])
    else:
        hashtable_all = gf.get_hashrows_overview(dynamic)

    print("got hashtable")

    conn.close()

    return render_template('overview.html', t_form=ChangeTimeForm(), \
    all_form=AllCongSearchForm(), dynamic=dynamic, time_delta=time_delta, \
    url=url, all_hashes=all_hashes,  hashes_no_dists=hashes_no_dists, \
    hashtable_all=hashtable_all, all_tweets=all_tweets,\
    most_retweeted_tweet_list=most_retweeted_tweet_list,\
    top_tweeters=top_tweeters, retweeted_users=retweeted_users,
    most_active=most_active\
    )


@app.route('/screen_name/<dynamic>', methods = ['GET', 'POST'])
def screen_name(dynamic):

    print('starting screen name {}'.format(dynamic))

    time_delta = request.args.get('time_delta')
    url = request.path
    str_time_range = stringtime(time_delta)

    # What hashtags are used most frequently by this screen name
    top_hashtags = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.user).join(Post.hashtags).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    # Which districts are referenced most frequently by screen name
    top_districts = db.session.query(District.district_name, \
    func.count(District.district_name)).\
    join(Post.districts).join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(District.district_name).order_by(func.count(District.district_name).\
    desc()).all()

    user_obj = db.session.query(User).filter(User.user_scrname==dynamic).first()
    #Turn user_created into datetime obj for use with Moment
    if user_obj:
        user_created_date = get_tweet_datetime(user_obj.user_created)

    # Who has this user most frequently retweeted in this time period?

    retweeted_users_period = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    filter(Post.original_author_scrname != "").\
    group_by(Post.original_author_scrname).\
    order_by(func.count(Post.original_author_scrname).desc()).all()

    # Who has this user most frequently retweeted overall (in accessible db)?

    retweeted_users_total = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.original_author_scrname != "").\
    group_by(Post.original_author_scrname).\
    order_by(func.count(Post.original_author_scrname).desc()).all()

    # Who has retweeted this user the most?

    who_retweets = db.session.query(User.user_scrname, \
    func.count(User.user_scrname)).\
    join(Post.user).\
    filter(Post.original_author_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(User.user_scrname).\
    order_by(func.count(User.user_scrname).desc()).all()

    #Get top retweet (retweet count reflects original post_ NOTE: needs work on authors
    #idea: filtering by orig_author, only getting retweets, always with dynamic
    #screenname. Thus no User needed. Remove?)

    # All posts that are retweets, and have this user as original_author_scrname
    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, Post.tweet_html,
    Post.text, Post.original_text).\
    filter(Post.original_author_scrname==dynamic).filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    # Use helper function to Get botscore for top five most-retweeted tweets,
    # create list of [post_id, name, retweet numbers, botscore]

    most_retweeted_tweet_list = get_tweet_list_nodist(most_retweeted_tweets)


    #Get data for double-7 chart
    scrname_chart = gf.scrname_chart(dynamic)

    hticks = [scrname_chart[0][0], scrname_chart[1][0],
    scrname_chart[2][0], scrname_chart[3][0], scrname_chart[4][0],
    scrname_chart[5][0], scrname_chart[6][0], scrname_chart[7][0],
    scrname_chart[8][0], scrname_chart[9][0]]

    if user_obj:
        return render_template('screen_name.html', t_form=ChangeTimeForm(), \
        dynamic=dynamic, url=url, time_delta=time_delta, top_hashtags=top_hashtags, \
        top_districts=top_districts, user_obj=user_obj, \
        retweeted_users_period=retweeted_users_period, \
        retweeted_users_total=retweeted_users_total, who_retweets=who_retweets,\
        user_created_date=user_created_date, most_retweeted_tweets=most_retweeted_tweets,\
        scrname_chart=scrname_chart, hticks=hticks, get_tweet=get_tweet, \
        most_retweeted_tweet_list=most_retweeted_tweet_list)

    else:
        return render_template('doesnt_exist.html', dynamic=dynamic)


@app.route('/change_time', methods = ['GET', 'POST'])
def change_time():

    t_form = ChangeTimeForm()
    if t_form.is_submitted():
        time_delta = t_form.change_time_delta.data
        dynamic = t_form.scope_field.data
        #url = t_form.url_field.data.rstrip("/{}".format(dynamic)).lstrip("/")
        url = t_form.url_field.data.split("/")[1]
        flash('Your request({0}) has been submitted, with delta(days)={1}'.\
        format(dynamic, time_delta))
        return redirect(url_for(url, dynamic=dynamic, time_delta=time_delta))

    return render_template('overview.html', title = 'Overview', dynamic=dynamic, \
    time_delta=time_delta, t_form=t_form, url=url)

@app.route('/phrase_search', methods = ['GET', 'POST'])
def phrase_search():
    p_form = PhraseSearchForm()
    if p_form.validate_on_submit():
        flash('Your request has been submitted')
        return redirect(url_for('index'))

    return render_template('index.html', title ='Home', p_form=p_form, \
    all_form=AllCongSearchForm(), d_form=DistrictForm(), \
    h_form=HashtagSearchForm(), sen_form=SenForm())

@app.route('/bot_search', methods = ['GET', 'POST'])
def bot_search():
    botform = BotSearchForm()
    if botform.is_submitted():
        dynamic = botform.scope_search.data
        time_delta = botform.botform_time_delta.data

        return redirect(url_for('botspy', dynamic=dynamic, time_delta=time_delta))
    return render_template('index.html', title ='Home', all_form=AllCongSearchForm(), \
    h_form=HashtagSearchForm(), p_form=PhraseSearchForm(), d_form=DistrictForm(),\
    botform=botform, sen_form=SenForm())


@app.route('/botspy/<dynamic>', methods = ['GET', 'POST'])
def botspy(dynamic):
    time_delta = request.args.get('time_delta')
    url = request.path
    str_time_range = stringtime(time_delta)

    most_active = db.session.query(User.user_scrname, User.user_cap_perc,\
    func.count(Post.post_id), User.user_id).\
    join(Post.user).\
    filter(User.user_cap_perc >= 60.0).filter(Post.created_at >= str_time_range).\
    group_by(User.user_id).order_by(func.count(Post.post_id).desc()).all()

    bot_hashtags = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.user).join(Post.hashtags).\
    filter(User.user_cap_perc >= 60.0).filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text, Post.original_text).\
    join(Post.user).\
    filter(User.user_cap_perc >= 60.0).filter(Post.created_at >= str_time_range).\
    filter(Post.is_retweet == 0).\
    order_by(Post.retweet_count.desc()).all()

    most_retweeted_tweet_list = get_tweet_list_nodist(most_retweeted_tweets)


    popular_bot = db.session.query(User.user_scrname, User.user_followers,\
    User.user_id).\
    filter(User.user_cap_perc >= 60.0).\
    group_by(User.user_id).order_by(User.user_followers.desc()).all()

    avg_bot_raw = db.session.query(func.avg(User.user_followers)).\
    filter(User.user_cap_perc >= 60.0).\
    first()

    avg_bot = int(avg_bot_raw[0])

    #Get botweather chart data from graph_functions modules
    botchart = gf.botweather_chart()

    return render_template('botspy.html', time_delta=time_delta,\
    most_active=most_active, bot_hashtags=bot_hashtags, \
    most_retweeted_tweets=most_retweeted_tweets, popular_bot=popular_bot,\
    avg_bot=avg_bot, botchart=botchart, get_tweet=get_tweet, \
    most_retweeted_tweet_list=most_retweeted_tweet_list)

@app.route('/about')
def about():
    url = request.path

    return render_template('about.html', url=url)

@app.route('/doesnt_exist/<dynamic>')
def doesnt_exist(dynamic):
    url = request.path
    return render_template('doesnt_exist.html', dynamic=dynamic,
    url=url)

@app.route('/test', methods = ['GET', 'POST'])
def test():
    rows = gf.get_hash_rows('ca49')
    return render_template('test.html', get_tweet=get_tweet, \
    test_hashgraph_data=test_hashgraph_data, test_usergraph_data=test_usergraph_data)

@app.route('/how_to_use')
def how_to_use():
    url = request.path

    return render_template('how_to_use.html', url=url)
