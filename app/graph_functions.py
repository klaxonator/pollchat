
from app import app, db
from datetime import datetime, date, timedelta
from app.helpers import dists as district_list
from app.helpers import distlist
from app.models import User, Post, District, Hashtag, Url
from sqlalchemy import Column, Integer, String, Float, func




#Set beginnin of searches at midnight, so have full-day comparisons
str_today = date.today().strftime("%Y-%m-%d %H:%M:%S")



def get_beg_date(time_delta):
    beg_date = date.today() - timedelta(days=time_delta)
    str_beg_date = beg_date.strftime("%Y-%m-%d %H:%M:%S")
    shrt_beg_date = beg_date.strftime('%b %d')
    results = [str_beg_date, shrt_beg_date]
    return results

#Get top line for hash or user chart
def top_line_all(var_type, index=1):

    top_line = []
    top_line.append('Date')

    #Get beginning of time range (to expand if insufficient posts)
    beg_range = date.today() - timedelta(days=index)
    str_beg_range = beg_range.strftime("%Y-%m-%d %H:%M:%S")

    print("next try is: starting from {}".format(str_beg_range))

    if var_type == "users":

        top_list = db.session.query(User.user_scrname, func.count(User.user_scrname)).\
        join(Post.user).\
        filter(Post.created_at >= str_beg_range).\
        group_by(User.user_scrname).order_by(func.count(User.user_scrname).desc()).all()

    elif var_type == "hashtags":

        top_list = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
        join(Post.hashtags).\
        filter(Post.created_at >= str_beg_range).\
        group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    else:

        return "Needs a variable type!"

    counter = 0
    for item in top_list:
        if item[0] in distlist:
            pass
        else:
            top_line.append(item[0])
            counter += 1
            if counter == 5:
                break

    print(top_line)

    if len(top_line) == 6:
        return top_line
    else:
        top_line = top_line_all(var_type, index+1)

    return top_line




def top_line_generic(this_district, var_type, index=1):

    top_line = []
    top_line.append('Date')

    #Get beginning of time range (to expand if insufficient posts)
    beg_range = date.today() - timedelta(days=index)
    str_beg_range = beg_range.strftime("%Y-%m-%d %H:%M:%S")

    print("next try is: starting from {}".format(str_beg_range))

    if var_type == "users":

        top_list = db.session.query(User.user_scrname, func.count(User.user_scrname)).\
        join(Post.user).join(Post.districts).\
        filter(District.district_name==this_district).filter(Post.created_at >= str_beg_range).\
        group_by(User.user_scrname).order_by(func.count(User.user_scrname).desc()).all()

    elif var_type == "hashtags":

        top_list = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
        join(Post.districts).join(Post.hashtags).\
        filter(District.district_name==this_district).filter(Post.created_at >= str_beg_range).\
        group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    else:

        return "Needs a variable type!"

    counter = 0
    for item in top_list[0:7]:
        if item[0] == this_district:
            pass
        else:
            top_line.append(item[0])
            counter += 1
            if counter == 5:
                break

    print(top_line)

    if len(top_line) == 6:
        return top_line
    else:
        top_line = top_line_generic(this_district, var_type, index+1)

    return top_line



def get_all_hashrows():
    #Container for all rows
    rows = []

    #Get top line (first row)
    this_top_line = top_line_all(var_type='hashtags')

    #start with current time as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(shrt_end_date)


        #For each date, iterate through seperate hashtag query for date range
        for this_hashtag in this_top_line[1:]:


            date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
            join(Post.hashtags).\
            filter(Hashtag.hashtag==this_hashtag).\
            filter(Post.created_at > beg_date[0]).filter(Post.created_at <= end_date).first()

            new_row.append(date_hash_num[0])
            print('Finished with hashtag: {}'.format(this_hashtag))

        #Add new row to rows, reset new_row, move end-time back a day
        rows.append(new_row)
        new_row = []
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]
        print('Finished with day -{}'.format(x))



    rows.append(this_top_line)
    rows.reverse()

    return rows


def get_hash_rows(this_district):
    #Container for all rows
    rows = []

    #Get top line (first row)
    this_top_line = top_line_generic(this_district, var_type='hashtags')

    #start with current time as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(shrt_end_date)


        #For each date, iterate through seperate hashtag query for date range
        for this_hashtag in this_top_line[1:]:


            date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
            join(Post.districts).join(Post.hashtags).\
            filter(District.district_name==this_district).filter(Hashtag.hashtag==this_hashtag).\
            filter(Post.created_at > beg_date[0]).filter(Post.created_at <= end_date).first()

            new_row.append(date_hash_num[0])
            # print('Finished with hashtag: {}'.format(this_hashtag))

        #Add new row to rows, reset new_row, move end-time back a day
        rows.append(new_row)
        new_row = []
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]
        print('Finished with day -{}'.format(x))



    rows.append(this_top_line)
    rows.reverse()

    return rows
#




def get_hash_dict_key(this_district):

    #Get 6-item top line for table,
    this_top_line = top_line_generic(this_district, var_type='hashtags')

    #Create date object for first row
    end_date = date.today()
    str_end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
    str_end_date_sm = end_date.strftime('%Y-%m-%d')

    beg_date = end_date - timedelta(days=1)
    str_beg_date = beg_date.strftime('%Y-%m-%d %H:%M:%S')
    str_beg_date_sm = beg_date.strftime('%Y-%m-%d')

    #CREATE basic top-level (of 2 levels) dictionary container -- to hold dates
    date_dict = {}
    date_dict[str_end_date_sm] = ""

    #Create second-level container for (<hashtag>: <number of appearances>)
    hash_dict = {}

    for this_hashtag in this_top_line[1:]:

        date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
        join(Post.districts).join(Post.hashtags).\
        filter(District.district_name==this_district).filter(Hashtag.hashtag==this_hashtag).\
        filter(Post.created_at > str_beg_date).filter(Post.created_at <= str_end_date).first()

        hash_dict[this_hashtag] = date_hash_num[0]

    date_dict[str_end_date_sm] = hash_dict

    return date_dict


def get_hash_dict_modular(this_district, end_date, this_top_line, beg_date):

    #Create second-level container for (<hashtag>: <number of appearances>)
    hash_dict = {}

    #fill hash_dict container with items from this_top_line
    for this_hashtag in this_top_line[1:]:

        date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
        join(Post.districts).join(Post.hashtags).\
        filter(District.district_name==this_district).filter(Hashtag.hashtag==this_hashtag).\
        filter(Post.created_at > beg_date).filter(Post.created_at <= end_date).first()

        hash_dict[this_hashtag] = date_hash_num[0]

    return hash_dict

def create_hash_dict(this_district):
    #Import or create main dict container
    date_dict = {} #NOTE: to be changed to import if statement

    #Get 6-item top line for table,
    this_top_line = top_line_generic(this_district, var_type='hashtags')

    #start with midnight current day as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')


    for x in range(1,11):
        beg_date = get_beg_date(x)

        #Get date_dict <value> (a dict) for key=end_date
        hash_dict_day = get_hash_dict_modular(this_district, end_date, this_top_line, beg_date[0])
        print(hash_dict_day)

        #Add key:value pair (<shrt_end_date>: <hash_dict_day> to date_dict
        date_dict[shrt_end_date] = hash_dict_day

        #reset dates for next loop
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]

        print('Finished with day -{}'.format(x))

    return date_dict

def get_user_dict_modular(this_district, end_date, this_top_line, beg_date):

    #Create second-level container for (<hashtag>: <number of appearances>)
    user_dict = {}

    #fill hash_dict container with items from this_top_line
    for this_user in this_top_line[1:]:

        date_user_num = db.session.query(func.count(User.user_scrname)).\
        join(Post.user).join(Post.districts).\
        filter(District.district_name==this_district).filter(User.user_scrname==this_user).\
        filter(Post.created_at > beg_date).filter(Post.created_at <= end_date).first()

        user_dict[this_user] = date_user_num[0]

    return user_dict

def create_user_dict(this_district):
    #Import or create main dict container
    date_dict = {} #NOTE: to be changed to import if statement

    #Get 6-item top line for table,
    this_top_line = top_line_generic(this_district, var_type='users')

    #start with midnight current day as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')


    for x in range(1,11):
        beg_date = get_beg_date(x)

        #Get date_dict <value> (a dict) for key=end_date
        user_dict_day = get_user_dict_modular(this_district, end_date, this_top_line, beg_date[0])
        print(user_dict_day)

        #Add key:value pair (<shrt_end_date>: <hash_dict_day> to date_dict
        date_dict[shrt_end_date] = user_dict_day

        #reset dates for next loop
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]

        print('Finished with day -{}'.format(x))

    return date_dict

def save_dicts(this_district):

    # for item in district_list:

    hash_dict = create_hash_dict(this_district)

    print('I made a hash dictionary')

    user_dict = create_user_dict(this_district)

    print('I made a user dictionary')

    today = date.today().strftime('%Y-%m-%d')

    new_dict = {today:
                    {
                    "hashdict": hash_dict,
                    "userdict": user_dict
                    }
                }
    return new_dict

def botweather_chart():
    this_top_line = ["Date", "No. of posts"]

    rows = []

    #start with current time as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(shrt_end_date)

        #Search for # of botposts between begdate and enddate
        date_botpost_count = db.session.query(func.count(Post.post_id)).\
        join(Post.user).\
        filter(User.user_cap_perc >= 60.0).\
        filter(Post.created_at > beg_date[0]).filter(Post.created_at <= end_date).\
        first()

        #Add to day's row
        new_row.append(date_botpost_count[0])


        #Add new row to rows, reset new_row, move end-time back a day
        rows.append(new_row)
        new_row = []
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]
        print('Finished with day -{}'.format(x))



    rows.append(this_top_line)
    rows.reverse()

    return rows

def scrname_chart(screen_name):
    this_top_line = ["Date", "No. of original posts", "No. of retweets"]

    rows = []

    #start with current time as endtime
    end_date = str_today
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Loop through week-long periods, starting from today
    for x in range(7, 71, 7):
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(shrt_end_date)

        #Search for # of original posts between begdate and enddate




        date_origpost_count = db.session.query(func.count(Post.post_id)).\
        join(Post.user).\
        filter(User.user_scrname == screen_name).filter(Post.is_retweet == 0).\
        filter(Post.created_at > beg_date[0]).filter(Post.created_at <= end_date).\
        first()

        #Add to day's row
        new_row.append(date_origpost_count[0])

        date_repost_count = db.session.query(func.count(Post.post_id)).\
        join(Post.user).\
        filter(User.user_scrname == screen_name).filter(Post.is_retweet == 1).\
        filter(Post.created_at > beg_date[0]).filter(Post.created_at <= end_date).\
        first()

        new_row.append(date_repost_count[0])

        #Add new row to rows, reset new_row, move end-time back a day
        rows.append(new_row)
        new_row = []
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]
        print('Finished with day -{}'.format(x))



    # rows.append(this_top_line) #NOTE:Not necessary for current double-y config
    rows.reverse()

    return rows
