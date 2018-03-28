# -*- coding: utf-8 -*-
"""
    AstroCoffee
    ~~~~~~
    Web application for organizing astro-ph coffee discussion.

    :copyright: © 2018 by Anowar J. Shajib.
    :license: MIT.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, escape

from .web import get_paper


app = Flask(__name__, instance_relative_config=True)

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
    """Initialize the database from command $flask initdb."""

    init_db()
    print('Initialized the AstroCoffee database.')


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
    """Convert datetime to given format. Filter for Jinja2."""
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
    cursor = db.execute(('select url, author, title, abstract, date_extended, '
                         'sources, volunteer, discussed from paper '
                         'where date_extended between '
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
    """Save the paper info in the database after a URL submission"""
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
    """Render the useful links page"""
    return render_template('usefullinks.html')
