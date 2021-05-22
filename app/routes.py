from flask import render_template, redirect, request, url_for, flash

from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Books, User_books, Classes, Subjects, Authors, Book_authors, Class_books, Schools


@app.route('/')
def index():
    if current_user.is_authenticated:
        name = current_user.name
        if current_user.is_admin == 1:
            name = "Admin"
    else:
        name = ""
    return render_template('index.html', name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user is None or not user.check_password(request.form['password']):
            flash("Неправильное имя пользователя и/или пароль")
        else:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    classes = [[i.id_class, str(i.num), i.letter] for i in Classes.query.all()]
    schools = [[i.id_school, i.name] for i in Schools.query.all()]
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('Такой пользователь уже существует')
        else:
            is_admin = 0
            if "is_admin" in request.form and request.form['is_admin'] == "on":
                is_admin = -1
            all_classes = [[i.id_class, "".join([str(i.num), i.letter])] for i in Classes.query.all()]
            id_class = 0
            for i in all_classes:
                if i[1] == request.form['id_class']:
                    id_class = i[0]
            id_school = 0
            for i in schools:
                if i[1] == request.form['id_school']:
                    id_school = i[0]
            user = User(email=request.form['email'], is_admin=is_admin,
                        name=request.form['my_name'], id_class=id_class, id_school=id_school)
            user.set_password(request.form['password'])
            db.session.add(user)
            db.session.commit()
            login_user(User.query.filter_by(email=request.form['email']).first(), remember=True)
            return redirect(url_for('index'))
    return render_template('registration.html', classes=classes, schools=schools)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/view_books')
def view_books():
    books = []
    if current_user.is_authenticated:
        name = current_user.name
        if current_user.is_admin == 1:
            name = "Admin"
        id_class = current_user.id_class
    else:
        id_class = 1
        name = ""
    if request.args.get('selected_class'):
        id_class = request.args.get('selected_class')

    my_class_books = Class_books.query.filter_by(id_class=id_class)
    all_classes = [[i.id_class, "".join([str(i.num), i.letter])] for i in Classes.query.all()]
    book_class = Classes.query.filter_by(id_class=id_class).first()
    book_class = str(book_class.num) + book_class.letter
    for current in my_class_books.all():
        book = Books.query.filter_by(id_book=current.id_book).first()
        authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                            [i.id_author for i in Book_authors.query.filter_by(id_book=current.id_book).all()]])
        subject = Subjects.query.filter_by(id_subject=book.id_subject).first().name
        books.append([book_class, authors, subject])
    if not books:
        books = [[book_class, "None", "None"]]
    return render_template('view_books.html', books=books, all_classes=all_classes, name=name)
