from app import app, db
from app.models import *


def delete_post(this_post_id):

    to_delete = db.session.query(Post).\
    filter(Post.post_id==this_post_id).first()

    try:
        db.session.delete(to_delete)
        db.session.commit()
        print("Deleted post id #{}".format(this_post_id))
    except:
        print("couldn't delete post")
        db.session.rollback()

def delete_id_group(this_orig_id):

    to_delete = db.session.query(Post).\
    filter(Post.original_tweet_id==this_post_id).all()
    count = 0
    for item in to_delete:
        db.session.delete(item)
        count += 1

    try:
        db.session.commit()
        print("Deleted {} posts".format(count))
    except:
        print("couldn't delete posts")
        db.session.rollback()
