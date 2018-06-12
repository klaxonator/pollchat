from app import app
from app import db
from app.models import User, Post, Hashtag, Url, District

#from app.database import db_session, init_db

#init_db()
#
#
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

@app.shell_context_processor
def make_shell_context():
    return {'db' : db, 'User' : User, 'Post' : Post, 'Hashtag' : Hashtag, 'Url' : Url, 'District' : District}
