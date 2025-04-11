import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

# TODO: reformat to one central database module
import psycopg
import os

def get_db():
    '''
    Connects to PostgreSQL database using credentials from environment variables
    @return: The database connection object
    '''

    current_app.logger.debug("Trying to connect to database...")

    dbname=os.getenv("DB_AUTH_NAME")
    user=os.getenv("DB_AUTH_USER")
    password=os.getenv("DB_AUTH_PASSWORD")
    host=os.getenv("DB_AUTH_HOST")
    port=os.getenv("DB_AUTH_PORT")
    host='35.196.76.62'

    current_app.logger.debug("DB_AUTH_NAME : "+ dbname)
    current_app.logger.debug("DB_AUTH_USER : "+ user)
    # current_app.logger.debug("DB_AUTH_PASSWORD : "+ password)
    current_app.logger.debug("DB_AUTH_HOST : "+ host)
    current_app.logger.debug("DB_AUTH_PORT : "+ port)
    
    try:
        conn = psycopg.connect(
            dbname=os.getenv("DB_AUTH_NAME"),
            user=os.getenv("DB_AUTH_USER"),
            password=os.getenv("DB_AUTH_PASSWORD"),
            host=os.getenv("DB_AUTH_HOST"),
            port=os.getenv("DB_AUTH_PORT")
        )

    except:
        current_app.logger.info("Cannot connect to database")
        conn = None

    current_app.logger.debug(conn)
    return conn

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                current_app.logger.debug("inserting (user, password) : "+ str((username, password)))
                db.execute("""
                    INSERT INTO auth (username, password_hash)
                    VALUES (%s, %s);
                    """, 
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM auth WHERE username = %s', (username,)
        ).fetchone()

        current_app.logger.debug(str(user))
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            # g.user = user[1]

            current_app.logger.debug("User logged in.")
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    elif get_db():
        g.user = get_db().execute(
            'SELECT * FROM auth WHERE id = %s', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view