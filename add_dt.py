from app import app, db
from app.models import User, Post, District, Hashtag, Url
from datetime import datetime, date, timedelta


unfilled = db.session.query(Post).\
            filter(Post.created_at_dt == None).all()

indexCount = 0

for row in unfilled:
    row.created_at_dt = row.created_at
    db.session.add(row)

    indexCount += 1
    if indexCount % 200 == 0:
        db.session.commit()
        print("filled {} rows".format(indexCount))

db.session.commit()
