import os
import sqlite3

from flask import g
from app import app

from timetable_parser import timetable_all_parser


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    with app.app_context():
        db = get_db()

        with app.open_resource(os.path.join(app.root_path, 'data', 'database','initialization.sql'), mode='r') as f:
            db.cursor().executescript(f.read())
        
        with open(app.root_path + '/course tables/all_courses.txt', mode='r', encoding='utf-8') as html_all_courses:
            courses_all = timetable_all_parser(html_all_courses)
            for course_single in courses_all:
                db.execute('insert into courses (course_id, course_name, teacher_name ,course_schedule) values (?, ?, ?, ?)', 
                           [course_single[0], course_single[1], course_single[2], course_single[3]])

        db.commit()
            
        print('Initialization of database is completed.')

if __name__ == '__main__':
    init_db()
