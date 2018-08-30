from app import app, db
from app.models import User, Post, Hashtag, District, Url




distfile = open('Files/full_cong_cands.csv', 'r')


for row in distfile:
    row_split = row.split(',')
    print(row_split)
    district = row_split[0]
    print(district)

    dem_candidate = row_split[5].strip()
    rep_candidate = row_split[7].strip()
    print(dem_candidate)
    print(rep_candidate)


    dbdistrict = db.session.query(District).\
    filter(District.district_name==district).first()

    dbdistrict.dem_candidate = dem_candidate
    dbdistrict.rep_candidate = rep_candidate

    db.session.add(dbdistrict)

db.session.commit()
distfile.close()
