from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

'''
students = db.Table('students',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)'''



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    '''
    studying = db.relationship(
        'User', secondary=students,
        primaryjoin=(students.c.user_id == id),
        secondaryjoin=(followers.c.course_id == id),
        backref=db.backref('students', lazy='dynamic'), lazy='dynamic')'''

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    #students = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Course %r>' % self.id

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Lesson %r>' % self.id
    def format(self):
        res = ""
        cnt = 0
        for i in range(len(self.text)):
            res += self.text[i]
            cnt += 1
            if self.text[i] == '\n':
                cnt = 0
            if cnt == 135:
                cnt = 0
                res += '\n'
        return res

class Sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        return '<Sub %r>' % self.id



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

'''
def init_db():
    db.create_all()#(extend_existing=True)

    # Create a test Article

    a = Article(title="example", intro="look", text="here it is")
    db.session.add(a)
    db.session.commit()


if __name__ == '__main__':
    init_db()
'''