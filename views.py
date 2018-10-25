import time

from database import *

from upload import *

from app import app
from flask import request, session, redirect, url_for, abort, render_template, flash, send_from_directory

from waitress import serve

from log_in_4m3 import LogIn4m3

from timetable_parser import timetable_single_parser


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return redirect(url_for('show_courses'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    #用于控制session过期时间
    session.permanent = True

    if request.method == 'POST':
        db = get_db()
        password = (db.execute('select password from students where student_id = ?',
                               [request.form['username']])).fetchone()

        if (password == None) or (str(password[0]) != request.form['password']):
            course_table = LogIn4m3(
                request.form['username'],
                request.form['password']).get_course_timetable(PhantomJS_path=app.root_path + '/phantomjs.exe')

            if course_table == 404:
                flash('无法连接4m3! (＃ﾟдﾟﾒ)')
                return render_template('login.html')

            elif course_table == 401:
                flash('用户名或密码错误! ヾ(ﾟдﾟ)ﾉ')
                return render_template('login.html')

            elif course_table == 500:
                flash('与4m3的连接因未知原因意外中断！ (＃ﾟдﾟﾒ)')
                db.execute('replace into students (student_id, password) values (?, ?)',
                           [request.form['username'], request.form['password']])
                db.commit()

            else:
                courses_id = timetable_single_parser(course_table)
                if courses_id == []:
                    flash('当前学期课表为空！ (＃ﾟдﾟﾒ)')
                else:
                    flash('找到{}门课程！ (´･ᴗ･`)'.format(len(courses_id)), 'success')
                    for course_id in courses_id:
                        db.execute('replace into students_courses (student_id, course_id) values (?, ?)',
                                   [request.form['username'], course_id])
                db.execute('replace into students (student_id, password) values (?, ?)',
                           [request.form['username'], request.form['password']])
                db.commit()

        session['student_id'] = request.form['username']
        session['logged_in'] = True
        return redirect(url_for('show_courses'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/courses')
def show_courses():
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.execute(
        'select courses.course_id, courses.course_name, courses.teacher_name, courses.course_schedule \
                        from students_courses, courses where students_courses.student_id = (?) and students_courses.course_id = courses.course_id \
                        order by courses.course_id asc', [session['student_id']])
    courses = cursor.fetchall()

    return render_template('show_courses.html', courses=courses)


@app.route('/courses/all')
def all_courses():
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    return render_template('all_courses.html')


@app.route('/courses/update')
def update_courses():
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    db = get_db()
    password = (db.execute('select password from students where student_id = ?', [session['student_id']])).fetchone()

    course_table = LogIn4m3(session['student_id'],
                            password[0]).get_course_timetable(PhantomJS_path=app.root_path + '/phantomjs.exe')

    if course_table == 404:
        flash('无法连接4m3! (＃ﾟдﾟﾒ)')
        return redirect(url_for('show_courses'))

    elif course_table == 401:
        session.pop('logged_in', None)
        db.execute('delete from students where student_id = ?', [session['student_id']])
        db.commit()
        flash('用户名或密码错误! ヾ(ﾟдﾟ)ﾉ')
        return redirect(url_for('login'))

    elif course_table == 500:
        flash('与4m3的连接因未知原因意外中断！ (＃ﾟдﾟﾒ)')
        return redirect(url_for('show_courses'))

    else:
        db.execute('delete from students_courses where student_id = ?', [session['student_id']])

        courses_id = timetable_single_parser(course_table)

        if courses_id == []:
            flash('当前学期课表为空！ (＃ﾟдﾟﾒ)')
            return redirect(url_for('show_courses'))

        else:
            flash('找到{}门课程！ (´･ᴗ･`)'.format(len(courses_id)), 'success')
            for course_id in courses_id:
                db.execute('insert into students_courses (student_id, course_id) values (?, ?)',
                           [session['student_id'], course_id])

        db.commit()
        return redirect(url_for('show_courses'))


@app.route('/courses/add', methods=['GET', 'POST'])
def add_courses():
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.execute(
        'select courses.course_id, courses.course_name, courses.teacher_name, courses.course_schedule \
                        from students_courses, courses where students_courses.student_id = (?) and students_courses.course_id = courses.course_id \
                        order by courses.course_id asc', [session['student_id']])
    courses = cursor.fetchall()

    if request.method == 'POST':
        if ((db.execute('select course_id from courses where course_id = ?',
                        [request.form['course_id']])).fetchone()) == None:
            flash('课程不存在！ (＃ﾟдﾟﾒ)')
            return redirect(url_for('add_courses'))

        if ((db.execute('select student_id, course_id from students_courses where (student_id, course_id) = (?, ?)',
                        [session['student_id'], request.form['course_id']])).fetchone()) != None:
            flash('课程已存在！ ヾ(ﾟдﾟ)ﾉ')
            return redirect(url_for('add_courses'))

        db.execute('insert into students_courses (student_id, course_id) values (?, ?)',
                   [session['student_id'], request.form['course_id']])
        db.commit()
        return redirect(url_for('add_courses'))

    return render_template('add_courses.html', courses=courses)


@app.route('/courses/delete/<string:course_id>')
def delete_course(course_id):
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    db = get_db()

    if ((db.execute('select course_id from courses where course_id = ?', [course_id])).fetchone()) == None:
        flash('课程不存在！ (＃ﾟдﾟﾒ)')

    if ((db.execute('select student_id, course_id from students_courses where (student_id, course_id) = (?, ?)',
                    [session['student_id'], course_id])).fetchone()) != None:
        db.execute('delete from students_courses where (student_id, course_id) = (?, ?)',
                   [session['student_id'], course_id])
        db.commit()

    return redirect(url_for('add_courses'))


@app.route('/files/<string:course_id>', methods=['GET', 'POST'])
def show_files(course_id):
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    db = get_db()
    if ((db.execute('select student_id, course_id from students_courses where (student_id, course_id) = (?, ?)',
                    [session['student_id'], course_id])).fetchone()) == None:
        flash('请先选课！ ヾ(ﾟдﾟ)ﾉ')
        return redirect(url_for('show_courses'))

    session['course_id'] = course_id

    if not os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id'])):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id']))

    return render_template('show_files.html')


#待实现功能：文件上传时间，文件描述
@app.route('/files/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    if request.method == 'POST':
        files = request.files['file']

        if files:
            #filename = secure_filename(files.filename)
            #Here could be a secure problem
            filename = files.filename
            filename = gen_file_name(filename, session['course_id'])
            mime_type = files.content_type

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg='错误的文件类型！ ヾ(ﾟдﾟ)ﾉ')

            else:
                #save file to disk
                uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['course_id'], filename)
                files.save(uploaded_file_path)

                #create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename, session['course_id'])

                #get file size after saving
                size = os.path.getsize(uploaded_file_path)

                #return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)

            return simplejson.dumps({'files': [result.get_file()]})

    if request.method == 'GET':
        #get all file in ./data directory
        files = [
            f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id']))
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id'], f)) and
            f not in IGNORED_FILES
        ]

        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({'files': file_display})

    return redirect(url_for('show_files'))


@app.route('/files/delete/<string:filename>', methods=['DELETE'])
def delete_files(filename):
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['course_id'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)

            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)

            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


#serve static files
@app.route('/files/thumbnail/<string:filename>', methods=['GET'])
def get_thumbnail(filename):
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    return send_from_directory(os.path.join(app.config['THUMBNAIL_FOLDER']), filename=filename)


@app.route('/files/data/<string:filename>', methods=['GET'])
def get_file(filename):
    if not session.get('logged_in'):
        flash('请先登录！ (ﾟﾛﾟﾉ)ﾉ')
        return redirect(url_for('login'))

    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], session['course_id']), filename=filename)


if __name__ == '__main__':
    serve(app, listen='0.0.0.0:80')