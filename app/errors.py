
from flask import render_template, flash, redirect, url_for, request
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    url = request.path
    return render_template('404.html', url=url), 404

@app.errorhandler(500)
def internal_error(error):
    url = request.path
    db.session.rollback()
    return render_template('500.html', url=url), 500
