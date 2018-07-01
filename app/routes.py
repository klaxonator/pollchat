from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import HashtagSearchForm, PhraseSearchForm, DistrictForm, \
AllCongSearchForm, ChangeTimeForm, BotSearchForm
from app.models import User, Post, District, Hashtag, Url
from sqlalchemy import func, Date, cast
from sqlalchemy.dialects.sqlite import DATETIME
from datetime import datetime, timedelta
from app.helpers import stringtime, get_tweet, test_insert, test_hashgraph_data, \
test_usergraph_data, distlist, get_tweet_datetime, get_tweet_list
import app.graph_functions as gf


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    url = request.path

    return render_template('index.html', title ='Home', d_form=DistrictForm(), \
    h_form=HashtagSearchForm(), p_form=PhraseSearchForm(), all_form=AllCongSearchForm(),\
    botform=BotSearchForm(), url=url)

@app.route('/select_district', methods = ['GET', 'POST'])
def select_district():
    d_form = DistrictForm()
#    if request.method == 'POST':
    if d_form.is_submitted():
        dynamic = d_form.select_district.data
        time_delta = d_form.district_time_delta.data
        flash('Your request({0}) has been submitted, with delta(days)={1}'.format(dynamic, \
        time_delta))
        return redirect(url_for('district', dynamic=dynamic, time_delta=time_delta))
    return render_template('index.html', title='Home', d_form=d_form, \
    p_form=PhraseSearchForm(), h_form=HashtagSearchForm(), all_form=AllCongSearchForm(),\
    botform=BotSearchForm())

@app.route('/district/<dynamic>', methods=['GET', 'POST'])
def district(dynamic):
    time_delta = request.args.get('time_delta')
    url = request.path

    str_time_range = stringtime(time_delta)

    dist_hashes = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.districts).join(Post.hashtags).\
    filter(District.district_name==dynamic).filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    print('got dist_hashes')

    #top tweeters: changed to reflect sql_mode=only_full_group_by
    top_tweeters = db.session.query(User.user_scrname, func.count(User.user_scrname),\
    User.user_cap_perc, User.user_id).\
    join(Post.user).join(Post.districts).\
    filter(District.district_name==dynamic).filter(Post.created_at >= str_time_range).\
    group_by(User.user_id).order_by(func.count(User.user_id).desc()).all()

    print('got top_tweeters')

    # NOTE: NEED *ORIGINAL_AUTHOR's BOTSCORE, NOT CURRENT POSTER'S (NOTE: DONE/BELOW)
    most_retweeted = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.districts).\
    filter(District.district_name==dynamic).filter(Post.created_at >= str_time_range).\
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

        botscore = db.session.query(User.user_cap_perc).\
        filter(User.user_scrname==item[0]).first()

        if botscore:
            tweeter.append(botscore[0])
        else:
            tweeter.append("Not yet in database")
        most_retweeted_list.append(tweeter)

    print('got most_retweeted')

    #Rewrite of most-retweeted tweets
    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text).\
    join(Post.districts).join(Post.user).\
    filter(District.district_name==dynamic).filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    # Use helper function to Get botscore for top five most-retweeted tweets,
    # create list of [post_id, name,retweet numbers, botscore]

    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets)

    print('got most_retweeted_list')

    #Get basic district object for district info
    dist_obj = db.session.query(District.state_fullname, District.district, \
    District.incumbent, District.incumbent_party, District.clinton_2016, \
    District.trump_2016, District.dem_candidate, District.rep_candidate).\
    filter(District.district_name==dynamic).first()

    print('got dist_obj')

    hash_table_rows = gf.get_hash_rows(dynamic)

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
    h_form = HashtagSearchForm()
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
    botform=BotSearchForm())

@app.route('/hashtag/<dynamic>', methods=['GET', 'POST'])
def hashtag(dynamic):
    time_delta = request.args.get('time_delta')
    url = request.path

    str_time_range = stringtime(time_delta)


    top_districts=db.session.query(District.district_name, \
    func.count(District.district_name)).\
    join(Post.districts).join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(District.district_name).order_by(func.count(District.district_name).\
    desc()).all()

    top_users=db.session.query(User.user_scrname, func.count(User.user_scrname), \
    User.user_cap_perc).\
    join(Post.user).join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(User.user_id, User.user_cap_perc).\
    order_by(func.count(User.user_scrname).desc()).all()

    valences = db.session.query(Post.polarity_val, func.count(Post.polarity_val)).\
    join(Post.hashtags).\
    filter(Hashtag.hashtag == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(Post.polarity_val).all()

    valences_datatable = [['Attitude', 'Number of Tweets']]
    for item in valences:
        valences_datatable.append([item[0], item[1]])

    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text).\
    join(Post.hashtags).join(Post.user).\
    filter(Hashtag.hashtag==dynamic).filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    #Get botscore for top five most-retweeted tweets, create list of [post_id, name,
    # retweet numbers, botscore] to send to template
    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets)

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
    botform=BotSearchForm())

@app.route('/overview/<dynamic>', methods = ['GET', 'POST'])
def overview(dynamic):
    time_delta = request.args.get('time_delta')
    url = request.path
    str_time_range = stringtime(time_delta)

    #Get a desc-ordered list of all hashtags being used in all districts
    all_hashes = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.hashtags).\
    filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    print("got all_hashes")

    #Get a list of tophashtags without district names
    hashes_no_dists = []
    counter = 0
    for item in all_hashes:
        if item[0] not in distlist:
            hashes_no_dists.append(item)
            counter += 1
        if counter == 20:
            break

    #GET 10-day table data for hashtag chart from graph_functions module
    hashtable_all = gf.get_all_hashrows()

    print("got hashtable")

    all_tweets = db.session.query(func.count(Post.post_id)).\
    filter(Post.created_at >= str_time_range).first()

    print("got all tweets")

    #Get list of most active districts
    most_active = db.session.query(District.district_name,\
    func.count(District.district_name)).\
    join(Post.districts).\
    filter(Post.created_at >= str_time_range).\
    group_by(District.district_name).\
    order_by(func.count(District.district_name).desc()).all()

    print("got most_active")

    #Get a desc-ordered list of top-volume Tweeters (sql_mode=fixed)
    top_tweeters = db.session.query(User.user_scrname, func.count(User.user_scrname), \
    User.user_cap_perc, User.user_id).\
    join(Post.user).\
    filter(Post.created_at >= str_time_range).\
    group_by(User.user_id).order_by(func.count(User.user_id).desc()).all()

    print("got top_tweeters")

    retweeted_users = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    filter(Post.original_author_scrname != "").filter(Post.created_at >= str_time_range).\
    group_by(Post.original_author_scrname).order_by(func.count(Post.original_author_scrname).\
    desc()).all()

    print("got retweeted users")

    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,\
    Post.text).\
    join(Post.user).\
    filter(Post.created_at >= str_time_range).\
    group_by(Post.post_id).order_by(Post.retweet_count.desc()).all()

    print("got most retweeted tweets")

    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets)

    print("got tweet list")

    return render_template('overview.html', t_form=ChangeTimeForm(), \
    all_form=AllCongSearchForm(), dynamic=dynamic, time_delta=time_delta, \
    url=url, all_hashes=all_hashes, top_tweeters=top_tweeters, \
    retweeted_users=retweeted_users, hashes_no_dists=hashes_no_dists, \
    hashtable_all=hashtable_all, most_active=most_active, all_tweets=all_tweets,\
    most_retweeted_tweets=most_retweeted_tweets, get_tweet=get_tweet, \
    most_retweeted_tweet_list=most_retweeted_tweet_list)


@app.route('/screen_name/<dynamic>', methods = ['GET', 'POST'])
def screen_name(dynamic):
    time_delta = request.args.get('time_delta')
    url = request.path
    str_time_range = stringtime(time_delta)

    top_hashtags = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
    join(Post.user).join(Post.hashtags).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    top_districts = db.session.query(District.district_name, \
    func.count(District.district_name)).\
    join(Post.districts).join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(District.district_name).order_by(func.count(District.district_name).\
    desc()).all()

    user_obj = db.session.query(User).filter(User.user_scrname==dynamic).first()
    #Turn user_created into datetime obj for use with Mmoment
    if user_obj:
        user_created_date = get_tweet_datetime(user_obj.user_created)

    retweeted_users_period = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    filter(Post.original_author_scrname != "").\
    group_by(Post.original_author_scrname).\
    order_by(func.count(Post.original_author_scrname).desc()).all()

    retweeted_users_total = db.session.query(Post.original_author_scrname, \
    func.count(Post.original_author_scrname)).\
    join(Post.user).\
    filter(User.user_scrname == dynamic).filter(Post.original_author_scrname != "").\
    group_by(Post.original_author_scrname).\
    order_by(func.count(Post.original_author_scrname).desc()).all()

    who_retweets = db.session.query(User.user_scrname, \
    func.count(User.user_scrname)).\
    join(Post.user).\
    filter(Post.original_author_scrname == dynamic).filter(Post.created_at >= str_time_range).\
    group_by(User.user_scrname).\
    order_by(func.count(User.user_scrname).desc()).all()

    #Get top retweet (retweet count reflects original post_ NOTE: needs work on authors
    #idea: filtering by orig_author, only getting retweets, always with dynamic
    #screenname. Thus no User needed. Remove?)
    most_retweeted_tweets = db.session.query(Post.post_id, Post.original_author_scrname, \
    Post.retweet_count, Post.original_tweet_id, User.user_scrname, Post.tweet_html,
    Post.text).\
    join(Post.user).\
    filter(Post.original_author_scrname==dynamic).filter(Post.created_at >= str_time_range).\
    order_by(Post.retweet_count.desc()).all()

    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets)
    print(most_retweeted_tweet_list)

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
    h_form=HashtagSearchForm())

@app.route('/bot_search', methods = ['GET', 'POST'])
def bot_search():
    botform = BotSearchForm()
    if botform.is_submitted():
        dynamic = botform.scope_search.data
        time_delta = botform.botform_time_delta.data

        return redirect(url_for('botspy', dynamic=dynamic, time_delta=time_delta))
    return render_template('index.html', title ='Home', all_form=AllCongSearchForm(), \
    h_form=HashtagSearchForm(), p_form=PhraseSearchForm(), d_form=DistrictForm(),\
    botform=botform)


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
    Post.text).\
    join(Post.user).\
    filter(User.user_cap_perc >= 60.0).filter(Post.created_at >= str_time_range).\
    filter(Post.is_retweet == 0).\
    order_by(Post.retweet_count.desc()).all()

    most_retweeted_tweet_list = get_tweet_list(most_retweeted_tweets)

    # NOTE: needs subquery to enable grouping by user_scrname
    # bot_districts = db.session.query(District.district_name, User.user_scrname, \
    # func.count(User.user_scrname).\
    # join(Post.districts).join(Post.user).\
    # filter(User.user_cap_perc >= 60.0).filter(Post.created_at >= str_time_range).\
    # group_by(District.district_name).order_by(func.count(User.user_scrname)).all()

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
    tweet_pull_nums = ['463440424141459456', '994575803504513024', '994575803504513024']
    tweet_pull = []
    for num in tweet_pull_nums:
        x = get_tweet(num)
        tweet_pull.append(x)

    tweetlist = ['994575803504513024', '994575803504513024']
    return render_template('about.html', tweetlist=tweetlist,\
    get_tweet=get_tweet, tweet_pull=tweet_pull, test_insert=test_insert,\
    url=url)

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
