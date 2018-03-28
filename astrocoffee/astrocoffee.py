# -*- coding: utf-8 -*-
"""
AstroCoffee
~~~~~~~~~~~
Web application for organizing astro-ph coffee discussion.

Inspired by Astro Coffee 2 by Abhimat Gautam and previous versions of
astroph.py by Ryan T. Hamilton, Ian J. Crossfield, and Nathaniel Ross.

:author: Anowar J. Shajib and Abhimat Gautam.
:copyright: © 2018 by Anowar J. Shajib.
:license: MIT.
"""

import os
import sqlite3
from datetime import datetime, timedelta
import click
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, escape
from flask_bcrypt import Bcrypt

from .web import get_paper


app = Flask(__name__, instance_relative_config=True)
bcrypt = Bcrypt(app)

app.config.from_object('config')
app.config.from_pyfile('config.py')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../instance/astrocoffee.db')
))


def connect_db():
    """Connect to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database"""
    db = get_db()

    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize the database.

    :Example:

    .. code-block: bash

        $ flask initdb

    """
    init_db()
    click.echo('Initialized the AstroCoffee database.')


@app.cli.command('mkuser')
@click.option('--user', prompt='Username', help='Login username.')
@click.option('--password', prompt='Password', help='Login password.',
              hide_input=True)
@click.option('--repassword', prompt='Re-enter password',
              help='Confirm login password.', hide_input=True)
@click.option('--salt', prompt='Secret key', help='Phrase for salting.')
def mkuser_command(user, password, repassword, salt):
    """
    Create the user with username and password.

    :Example:

    .. code-block:: bash

        $ flask mkuser

    :param user: Username.
    :type user: str
    :param password: Password.
    :type password: str
    :param repassword: Re-entered password.
    :type repassword: str
    :param salt: Phrase for salting.
    :type salt: str
    :return: None
    :rtype: None
    """
    if password != repassword:
        click.echo('Passwords do not match!')
    else:
        with open(os.path.join(app.root_path,
                               '../instance/config.py'), 'w') as f:
            salted_password = salt + password
            hashed_password = bcrypt.generate_password_hash(salted_password)
            f.write(('# -*- coding: utf-8 -*-\n'
                     'SECRET_KEY = "{}"\n'
                     'USERNAME = "{}"\n'
                     'PASSWORD = {}').format(salt, user, hashed_password))


@app.cli.command('check')
@click.option('--p', prompt='Username', help='Login username.')
def check(p):
    salted_password = app.config['SECRET_KEY'] + p.encode('utf-8')
    click.echo(salted_password)
    click.echo(bcrypt.check_password_hash(app.config['PASSWORD'],
                                          salted_password))


def get_db():
    """Open a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, format_=None):
    """Convert datetime to given format."""
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    if format_ is None:
        format_ = '%b %d %Y'
    return date.strftime(format_)


@app.route('/')
def show_papers():
    """Render the homepage."""
    now = datetime.now()
    week_earlier = now - timedelta(days=7)

    now = now.strftime("%Y-%m-%d %H:%M")
    week_earlier = week_earlier.strftime("%Y-%m-%d %H:%M")

    db = get_db()
    cursor = db.execute(('select id, url, author, title, abstract, '
                         'date_extended, sources, volunteer, discussed '
                         'from paper where date_extended between '
                         '"{}" and "{}"'.format(week_earlier, now)))
    papers = cursor.fetchall()

    new_papers = []
    discussed_papers = []
    for paper in papers:
        if paper['discussed'] == 0:
            new_papers.append(paper)
        else:
            discussed_papers.append(paper)

    return render_template('papers.html', new_papers=new_papers,
                           discussed_papers=discussed_papers)


@app.route('/submit', methods=['POST'])
def submit_paper():
    """Save the paper info in the database after a URL submission."""
    paper = get_paper(escape(request.form['article']))

    if paper is not None:
        db = get_db()
        db.execute(('insert into paper (url, author, author_number, title,'
                    'date_submitted, date_extended, abstract, subject,'
                    'sources) values (?, ?, ?, ?, ?, ?, ?, ?, ?)'),
                   [paper.url,
                    paper.author,
                    paper.author_number,
                    paper.title,
                    paper.date_submitted,
                    paper.date_extended,
                    paper.abstract,
                    paper.subject,
                    paper.sources])
        db.commit()
        flash('Your submission was successfully added. Thanks for '
              'advancing knowledge!', 'success')
    else:
        flash('Error processing the URL or arXiv-ID! Please make sure '
              'it\'s valid.', 'error')

    return redirect(url_for('show_papers'))


@app.route('/archive/')
def show_archive():
    """Render the archive page."""
    return render_template('archive.html')


@app.route('/usefullinks/')
def show_useful_links():
    """Render the useful links page."""
    return render_template('usefullinks.html')


@app.route('/login-form/')
def show_login_form():
    """Render the login page."""
    return render_template('form.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in the user."""
    if request.method == 'POST':
        salted_password = app.config['SECRET_KEY'] + request.form['password']

        if request.form['username'] == app.config['USERNAME'] and \
                bcrypt.check_password_hash(app.config['PASSWORD'],
                                           salted_password):
            session['logged_in'] = True
            flash('You are logged in.', 'success')
            return redirect(url_for('show_papers'))

    flash('Invalid login credential(s).', 'error')
    return render_template('form.html')


@app.route('/logout')
def logout():
    """Log a user out."""
    session.pop('logged_in', None)
    flash('You are logged out.', 'success')
    return redirect(url_for('show_papers'))


@app.route('/mark_discussed')
def mark_discussed():
    """Mark a paper as discussed."""
    paper_id = request.args.get('paper_id', None)

    if paper_id is not None and session['logged_in']:
        db = get_db()
        db.execute('update paper set discussed = 1 where id = ?', [paper_id])
        db.commit()
        flash('The paper has been marked as discussed.', 'success')

    return redirect(url_for('show_papers'))


@app.route('/unmark_discussed')
def unmark_discussed():
    """Mark a paper as discussed."""
    paper_id = request.args.get('paper_id', None)

    if paper_id is not None and session['logged_in']:
        db = get_db()
        db.execute('update paper set discussed = 0 where id = ?', [paper_id])
        db.commit()
        flash('The paper has been marked as undiscussed.', 'success')

    return redirect(url_for('show_papers'))