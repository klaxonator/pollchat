

from app import app, db
from datetime import datetime, date, timedelta
from app.helpers import dists as district_list
from app.helpers import distlist, str_today, today
from app.models import User, Post, District, Hashtag, Url, District_graphs
from sqlalchemy import Column, Integer, String, Float, func
import pickle
import csv




def get_beg_date(time_delta):

    # get midnight of current day
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight

    # beg_date = midnight minus time_delta days
    beg_date = today - timedelta(days=time_delta)

    str_beg_date = beg_date.strftime("%Y-%m-%d %H:%M:%S")
    shrt_beg_date = beg_date.strftime('%b %d')

    results = [str_beg_date, shrt_beg_date]
    return results

# Get top line for get_all_hashrows (overview page)


def top_line_all(distgroup, var_type, index=3):
    print(distgroup)
    print(var_type)
    print(index)

    if distgroup == "allcong":
        dist_fig = 1
    elif distgroup == "allsen":
        dist_fig = 2
    elif distgroup == "allraces":
        dist_fig = 3

    print(dist_fig)

    top_line = []
    top_line.append('Date')
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight

    #Get beginning of time range (to expand if insufficient posts)
    beg_range = today - timedelta(days=index)
    str_beg_range = beg_range.strftime("%Y-%m-%d %H:%M:%S")

    print("next try is: starting from {}".format(str_beg_range))

    if distgroup == "allcong" or distgroup == "allsen":

        if var_type == "users":

            top_list = db.session.query(User.user_scrname, func.count(User.user_scrname)).\
            join(Post.user).join(Post.districts).\
            filter(Post.created_at >= str_beg_range).filter(District.dist_type==dist_fig).\
            group_by(User.user_scrname).order_by(func.count(User.user_scrname).desc()).all()

        elif var_type == "hashtags":
            print("trying hashsearch")

            top_list = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
            join(Post.hashtags).join(Post.districts).\
            filter(Post.created_at >= str_beg_range).filter(District.dist_type==dist_fig).\
            group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

            print(len(top_list))
        else:

            raise ValueError('Needs a variable type!')

    else:                           #For allraces (all congressional races)

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

            raise ValueError('Needs a variable type!')

        print(len(top_list))
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
        top_line = top_line_all(distgroup, var_type, index+1)

    # Top line = [Date, hash_1, hash_2, hash_3, hash_4, hash_5]
    return top_line



# Get top line for charts. Index=3 means starting with 3-day running average
# Used for get_hash_rows (single-district page)
def top_line_generic(this_district, var_type, index=3):

    top_line = []
    top_line.append('Date')
    today = datetime.combine(date.today(), datetime.min.time())  #datetime object for midnight

    #Get (previous midnight) beginning of time range (to expand if insufficient posts)
    beg_range = today - timedelta(days=index)
    str_beg_range = beg_range.strftime("%Y-%m-%d %H:%M:%S")

    print("next try is: starting from {}".format(str_beg_range))

    # Get search object for most frequent posters in this district
    if var_type == "users":

        top_list = db.session.query(User.user_scrname, func.count(User.user_scrname)).\
        join(Post.user).join(Post.districts).\
        filter(District.district_name==this_district).filter(Post.created_at >= str_beg_range).\
        group_by(User.user_scrname).order_by(func.count(User.user_scrname).desc()).all()

    # Get search object for most frequent hashtags used in this district
    elif var_type == "hashtags":

        top_list = db.session.query(Hashtag.hashtag, func.count(Hashtag.hashtag)).\
        join(Post.districts).join(Post.hashtags).\
        filter(District.district_name==this_district).filter(Post.created_at >= str_beg_range).\
        group_by(Hashtag.hashtag).order_by(func.count(Hashtag.hashtag).desc()).all()

    else:

        return "Needs a variable type!"

    counter = 0
    for item in top_list:
        if item[0] in distlist:                 #skip all district names
            pass
        else:
            top_line.append(item[0])            #add hashtag to list
            counter += 1
            if counter == 5:                    #break at "date" plus 5 items
                break

    print(top_line)

    if len(top_line) == 6:
        return top_line
    else:

        top_line = top_line_generic(this_district, var_type, index+1)

    return top_line


#This is used only for Overview chart

def get_hashrows_overview(distgroup):
    #Container for all rows

    rows = []

    #Get top line (first row)
    this_top_line = top_line_all(distgroup=distgroup, var_type='hashtags')

    #start with midnight of current day as endtime
    end_date = str_today()
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []

    if distgroup == "allcong":
        dist_fig = 1
    elif distgroup == "allsen":
        dist_fig = 2
    elif distgroup == "allraces":
        dist_fig = 3

    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):

        # Using X as time_delta, get beg date of -1, -2, etc ... days
        # Function returns (midnight, display date)
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(beg_date[1])


        #For each date, iterate through seperate hashtag query for date range
        for this_hashtag in this_top_line[1:]:


            if distgroup == "allcong" or distgroup == "allsen":
                date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
                join(Post.hashtags).join(Post.districts).\
                filter(Hashtag.hashtag==this_hashtag).\
                filter(District.dist_type==dist_fig).\
                filter(Post.created_at > beg_date[0]).\
                filter(Post.created_at <= end_date).first()

            else:
                date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
                join(Post.hashtags).\
                filter(Hashtag.hashtag==this_hashtag).\
                filter(Post.created_at > beg_date[0]).\
                filter(Post.created_at <= end_date).first()

            new_row.append(date_hash_num[0])
            print('Finished with hashtag: {}'.format(this_hashtag))

        #Add new row to rows, reset new_row, move end-time back a day
        rows.append(new_row)
        new_row = []
        end_date = beg_date[0]
        shrt_end_date = beg_date[1]
        print('Finished with day -{}'.format(x))



    rows.append(this_top_line)

    #Reverse so that earliest row is first, latest last
    rows.reverse()

    rows_pickled = pickle.dumps(rows)

    # get district row as object if exists
    check = db.session.query(District_graphs).\
    filter(District_graphs.reference_date==str_today()).\
    filter(District_graphs.district_name==distgroup).first()

    #IF district row for today already exists, update
    if check != None:
        check.chart_rows = rows_pickled
        try:
            db.session.add(check)
            db.session.commit()
        except:
            db.session.rollback()

    else:

        hash_add = District_graphs(str_today(), distgroup, rows_pickled)

        try:
            db.session.add(hash_add)
            db.session.commit()
        except:
            db.session.rollback()


def get_hash_rows(this_district):
    #Container for all rows
    rows = []

    #Get top line (first row)
    this_top_line = top_line_generic(this_district, var_type='hashtags')

    #start with midnight of current day as endtime
    end_date = str_today()
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):
        beg_date = get_beg_date(x)


        #add short date version as first item of row
        new_row.append(beg_date[1])


        #For each date, iterate through seperate hashtag query for date range
        for this_hashtag in this_top_line[1:]:


            date_hash_num = db.session.query(func.count(Hashtag.hashtag)).\
            join(Post.districts).join(Post.hashtags).\
            filter(District.district_name==this_district).filter(Hashtag.hashtag==this_hashtag).\
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


    rows_pickled = pickle.dumps(rows)

    # get district row as object if exists
    check = db.session.query(District_graphs).\
    filter(District_graphs.reference_date==str_today()).\
    filter(District_graphs.district_name==this_district).first()

    #IF district row for today already exists, update
    if check != None:
        check.chart_rows = rows_pickled
        try:
            db.session.add(check)
            db.session.commit()
        except:
            db.session.rollback()

    else:

        hash_add = District_graphs(str_today(), this_district, rows_pickled)

        try:
            db.session.add(hash_add)
            db.session.commit()
        except:
            db.session.rollback()



    return rows


def fill_graphs():
    overview_districts = ['allcong', 'allsen', 'allraces']


    for item in overview_districts:
        get_hashrows_overview(item)


    with open('app/comp_races_parsed.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0][1:5] == 'ks04':
                break
            print(row[0][1:5])
            get_hash_rows(row[0][1:5])



    with open('app/comp_races_parsed_sen.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            get_hash_rows(row[0][1:6])

    with open('logs/twitterscrape_log.txt', 'a') as fw:
        fw.write('Updated graph data at {}\n'.format(datetime.now()))

# Chart for botspy.html page
def botweather_chart():
    this_top_line = ["Date", "No. of posts"]

    rows = []

    #start with midnight of current date as endtime


    end_date = str_today()
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    #Top level loop through dates
    for x in range(1, 11):
        beg_date = get_beg_date(x)


        #add date as first item of row - use start date(midnight) fpr full day
        new_row.append(beg_date[1])

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
    print(rows)
    return rows


# Chart for screen_name.html page
def scrname_chart(screen_name):
    this_top_line = ["Date", "No. of original posts", "No. of retweets"]

    rows = []

    #start with midnight of current day as endtime
    end_date = str_today()
    shrt_end_date = date.today().strftime('%b %d')

    #Create container for individual rows
    new_row = []


    #Populate other rows with hashtag quantities by date

    # Loop through day-long periods, starting from today
    for x in range(1, 11):
        beg_date = get_beg_date(x)
        last_chart_date = str_today()

        #add short date version as first item of row
        new_row.append(shrt_end_date)

    # #Loop through week-long periods, starting from today
    # for x in range(7, 71, 7):
    #     beg_date = get_beg_date(x)
    #     last_chart_date = shrt_end_date
    #
    #     #add short date version as first item of row
    #     new_row.append(shrt_end_date)
    #
    #     #Search for # of original posts between begdate and enddate




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



if __name__ == '__main__':
    fill_graphs()
