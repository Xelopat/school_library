from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


@login.user_loader
def load_user(id_user):
    return User.query.get(int(id_user))


class User(UserMixin, db.Model):
    def get_id(self):
        return self.id_user

    __tablename__ = 'users'

    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_class = db.Column(db.Integer, nullable=True)
    id_school = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    is_admin = db.Column(db.Integer, nullable=True)
    password_hash = db.Column(db.String, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Info_about_books(db.Model):
    __tablename__ = 'info_about_books'

    id_book = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_subject = db.Column(db.Integer, nullable=True)
    num_class = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.Integer, nullable=True)


class All_books(db.Model):
    __tablename__ = 'all_books'

    id_all_books = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, default=-1)
    id_book = db.Column(db.Integer, nullable=True)
    qr = db.Column(db.String, nullable=True)


class Classes(db.Model):
    __tablename__ = 'classes'

    id_class = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num = db.Column(db.Integer, nullable=True)
    letter = db.Column(db.String, nullable=True)


class Subjects(db.Model):
    __tablename__ = 'subjects'

    id_subject = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)


class Authors(db.Model):
    __tablename__ = 'authors'

    id_author = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)


class Book_authors(db.Model):
    __tablename__ = 'book_authors'

    id_book_authors = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_book = db.Column(db.Integer, nullable=True)
    id_author = db.Column(db.Integer, nullable=True)


class Class_books(db.Model):
    __tablename__ = 'class_books'

    id_class_books = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_class = db.Column(db.Integer, nullable=True)
    id_book = db.Column(db.Integer, nullable=True)


class Schools(db.Model):
    __tablename__ = 'schools'
    id_school = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
