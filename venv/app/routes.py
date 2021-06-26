from flask import Flask, url_for, render_template, flash, redirect
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Course, Lesson, Sub
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# @app.route('/about')
# def about():
#     return render_template("about.html")

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    my_courses_list = []
    for sub in Sub.query.filter_by(user_id=current_user.id):
        my_courses_list.append(Course.query.get(sub.course_id))
    return render_template('user.html', user=user, my_courses=my_courses_list)

@app.route('/courses')
def courses():
    courses = Course.query.order_by(Course.id.desc()).all()
    return render_template("courses.html", courses=courses)

@app.route('/my_courses')
@login_required
def my_courses():
    my_courses_list = Course.query.filter_by(author_id=current_user.id)
    return render_template("my_courses.html", courses=my_courses_list)

@app.route('/courses/<int:id>')
@login_required
def course_detail(id):
    user = current_user.id
    course = Course.query.get(id)
    author_id = course.author_id
    author = User.query.get(author_id)
    lessons = Lesson.query.filter_by(course_id=id)
    taken=0
    for sub in Sub.query.filter_by(user_id=user):
        if sub.course_id == id:
            taken=1
    return render_template("course_detail.html", course=course, lessons=lessons, user=user, author=author, taken=taken)




@app.route('/create-course', methods=['POST', 'GET'])
def create_course():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        author_id = current_user.id
        course = Course(title=title, intro=intro, author_id=author_id)

        try:
            db.session.add(course)
            db.session.commit()
            return redirect('/courses')
        except:
            return "An error occured while creating the course"
    else:
        return render_template("create_course.html")




@app.route('/courses/<int:id>/update', methods=['POST', 'GET'])
def course_update(id):
    course = Course.query.get(id)
    if request.method == "POST":
        course.title = request.form['title']
        course.intro = request.form['intro']
        try:
            db.session.commit()
            return redirect('/courses')
        except:
            return "An error occured while changing"
    else:
        return render_template("course_update.html", course=course)


@app.route('/courses/<int:id>/delete')
def course_delete(id):
    course = Course.query.get_or_404(id)

    try:
        lessons = Lesson.query.filter_by(course_id=id)
        for el in lessons:
            db.session.delete(el)
        db.session.delete(course)
        db.session.commit()
        return redirect('/courses')
    except:
         return "Problem with deleting a course"


@app.route('/courses/<int:id>/create-lesson', methods=['POST', 'GET'])
def create_lesson(id):
    if request.method == "POST":
        title = request.form['title']
        course_id = id
        text = request.form['intro']
        author_id = current_user.id
        #text = format_text(text)

        lesson = Lesson(title=title, text=text, course_id=course_id, author_id=author_id)

        try:
            db.session.add(lesson)
            db.session.commit()
            return redirect('/courses/' + str(id))
        except:
            return "An error occured while adding the lesson"
    else:
        return render_template("create_lesson.html")

@app.route('/courses/<int:course_id>/les/<int:les_id>')
def lesson(course_id, les_id):
    user = current_user.id
    lesson = Lesson.query.get(les_id)
    author_id = lesson.author_id
    return render_template("lesson.html", lesson=lesson, user=user, author=author_id)


@app.route('/courses/<int:course_id>/les/<int:les_id>/update', methods=['POST', 'GET'])
def lesson_update(course_id, les_id):
    lesson = Lesson.query.get(les_id)
    if request.method == "POST":
        lesson.title = request.form['title']
        lesson.text = request.form['text']
        #lesson.text = format_text(lesson.text)
        try:
            db.session.commit()
            return redirect('/courses/' + str(course_id) + '/les/' + str(les_id))
        except:
            return "An error occured while changing"
    else:
        return render_template("lesson_update.html", lesson=lesson)

@app.route('/courses/<int:course_id>/les/<int:les_id>/delete')
def lesson_delete(course_id, les_id):
    lesson = Lesson.query.get_or_404(les_id)

    try:
        db.session.delete(lesson)
        db.session.commit()
        return redirect('/courses/' + str(course_id))
    except:
        return "Problem with deleting a lesson"

@app.route('/courses/<int:id>/study', methods=['POST', 'GET'])
def study(id):
    user_id = current_user.id
    course = Course.query.get(id)
    author_id = course.author_id

    sub = Sub(course_id=id, user_id=user_id)


    try:
        db.session.add(sub)
        db.session.commit()
    except:
        return "An error occured while adding course"
    lessons = Lesson.query.filter_by(course_id=id)
    return render_template("course_detail.html", course=course, lessons=lessons, user=user, author=author_id)


@app.route('/studying')
@login_required
def studying():
    my_courses_list = []
    for sub in Sub.query.filter_by(user_id=current_user.id):
        my_courses_list.append(Course.query.get(sub.course_id))
    return render_template("studying.html", courses=my_courses_list)



