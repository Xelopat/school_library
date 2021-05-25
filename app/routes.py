import base64

from io import BytesIO

from PIL import Image
from flask import render_template, redirect, request, url_for, flash, jsonify
import pyzbar.pyzbar as zbar
from selenium import webdriver


from app import app, db
from flask_login import current_user, login_user, logout_user
from app.models import User, All_books, Classes, Subjects, Authors, Book_authors, Class_books, Schools, \
    Info_about_books


@app.route('/')
def index():
    is_admin = 0
    if current_user.is_authenticated:
        name = current_user.name
        is_admin = current_user.is_admin
    else:
        name = ""
    return render_template('index.html', name=name, is_admin=is_admin)


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
        id_class = current_user.id_class
        if id_class == 0:
            id_class = 1
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
        book = Info_about_books.query.filter_by(id_book=current.id_book).first()
        authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                            [i.id_author for i in Book_authors.query.filter_by(id_book=current.id_book).all()]])
        subject = Subjects.query.filter_by(id_subject=book.id_subject).first().name
        books.append([book_class, authors, subject])
    if not books:
        books = [[book_class, "книг", "нет"]]
    return render_template('view_books.html', books=books, all_classes=all_classes, name=name)


@app.route('/view_books_edit')
def view_books_edit():
    is_admin = 0
    name = ""
    if current_user.is_authenticated:
        is_admin = current_user.is_admin
        name = current_user.name
        if is_admin != 1:
            return redirect(url_for('index'))
    if is_admin != 1:
        return redirect(url_for('index'))
    books = []
    all_books = []
    id_class = 1
    if request.args.get('selected_class'):
        id_class = request.args.get('selected_class')

    my_class_books = Class_books.query.filter_by(id_class=id_class)
    all_classes = [[i.id_class, "".join([str(i.num), i.letter])] for i in Classes.query.all()]
    book_class = Classes.query.filter_by(id_class=id_class).first()
    book_class = str(book_class.num) + book_class.letter
    for current in my_class_books.all():
        book = Info_about_books.query.filter_by(id_book=current.id_book).first()
        authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                            [i.id_author for i in Book_authors.query.filter_by(id_book=current.id_book).all()]])
        subject = Subjects.query.filter_by(id_subject=book.id_subject).first().name
        books.append([book_class, authors, subject])

    for current in Info_about_books.query.all():
        book = Info_about_books.query.filter_by(id_book=current.id_book).first()
        authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                            [i.id_author for i in Book_authors.query.filter_by(id_book=current.id_book).all()]])
        subject = Subjects.query.filter_by(id_subject=book.id_subject).first().name
        all_books.append(subject + authors + book_class)
    return render_template('view_books.html', books=books, all_classes=all_classes, name=name, all_books=all_books)


@app.route('/scan_book')
def scan_book():
    is_admin = 0
    if current_user.is_authenticated:
        is_admin = current_user.is_admin
        name = current_user.name
    else:
        name = ""
    return render_template('scan_book.html', is_admin=is_admin, name=name)


@app.route('/scan_isbn', methods=['POST', 'GET'])
def scan_isbn():
    is_admin = 0
    name = ""
    if current_user.is_authenticated:
        is_admin = current_user.is_admin
        name = current_user.name
        if is_admin != 1:
            return redirect(url_for('index'))
    if is_admin != 1:
        return redirect(url_for('index'))
    if request.method == "POST":
        authors = request.form['authors'].replace(" ", "").split(",")
        current_class = request.form['current_class']
        subject = request.form['subject']
        if not Info_about_books.query.filter_by(isbn=request.form['isbn']).first():
            if 12 > int(current_class) > 0:
                is_subject = Subjects.query.filter_by(name=subject).first()
                if not is_subject:
                    db.session.add(Subjects(name=subject))
                for author in authors:
                    is_author = Authors.query.filter_by(name=author).first()
                    if not is_author:
                        db.session.add(Authors(name=author))
            else:
                return render_template('scan_isbn.html', is_admin=is_admin, name=name,
                                       error="Введён некорректный класс")
            db.session.commit()
            append_book = Info_about_books(id_subject=Subjects.query.filter_by(name=subject).first().id_subject,
                                           num_class=current_class, isbn=request.form['isbn'])
            db.session.add(append_book)
            db.session.flush()
            for author in authors:
                db.session.add(Book_authors(id_author=Authors.query.filter_by(name=author).first().id_author,
                                            id_book=append_book.id_book))
        else:
            return render_template('scan_isbn.html', is_admin=is_admin, name=name, error="Книга уже есть в базе")
        db.session.commit()
    return render_template('scan_isbn.html', is_admin=is_admin, name=name, error="")


@app.route('/decode', methods=['POST'])
def decode():
    img = request.form['image']
    img = img[img.find(",") + 1:].replace(" ", "+")
    dec = base64.b64decode(img)
    barcode = zbar.decode(Image.open(BytesIO(dec)))
    if len(barcode) > 0:
        message = str(barcode[0].data)[2:-1]
        type_code = barcode[0].type
        current_book = All_books.query.filter_by(qr=message).first()
        if current_book:
            id_info_book = current_book.id_book
            info_book = Info_about_books.query.filter_by(id_book=id_info_book).first()
            authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                                [i.id_author for i in
                                 Book_authors.query.filter_by(id_book=info_book.id_book).all()]])
            subject = Subjects.query.filter_by(id_subject=info_book.id_subject).first().name
            id_user = current_book.id_user
            if id_user != -1:
                user = User.query.filter_by(id_user=id_user).first()
                username = user.name
                my_class = "без класса"
                if user.is_admin == 0:
                    book_class = Classes.query.filter_by(id_class=user.id_class).first()
                    my_class = str(book_class.num) + book_class.letter
                return jsonify({"code": "yes", "id_book": id_info_book, "username": username, "subject": subject,
                                "authors": authors, "my_class": my_class, "qr": message, "type": type_code})
            else:
                return jsonify(
                    {"code": "no_user", "subject": subject, "authors": authors, "qr": message, "id_book": id_info_book,
                     "type": type_code})
        return jsonify({"code": "no_book", "id_book": 0, "qr": message, "type": type_code})
    return jsonify({"code": "no", "type": ""})


@app.route('/info_isbn', methods=['POST'])
def info_isbn():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.triumph.ru/html/serv/find-isbn.php?isbn={request.form['isbn']}")
    subjects = Subjects.query.all()
    element = []
    for x in driver.find_elements_by_tag_name("body"):
        element.append(x.text)
    driver.quit()
    text = element[0]
    if "В РГБ найдена книга:" in text:
        authors = text[text.find("/") + 2:text.find(". -")]
        subject = ""
        current_class = ""
        if "класс" in text:
            current_class = text[text.find("класс") - 3:text.find("класс")]
        for i in subjects:
            if i.name.lower() in text.lower():
                subject = i.name
                break
        i = 0
        while not authors[i].isalpha():
            i += 1
        authors = authors[i:]
        while authors[0] != authors[0].upper() or authors[0] == " ":
            authors = authors[1:]
        i = 0
        while i != len(authors):
            if authors[i] == " " and authors[i + 1].islower():
                authors = authors[0:i]
                break
            i += 1
        return jsonify(
            {"code": "yes", "authors": authors, "subject": subject, "class": current_class, "qr": request.form['isbn']})
    return jsonify({"code": "no"})


@app.route('/give_book', methods=['POST'])
def give_book():
    changed_user = current_user
    if not changed_user.is_authenticated:
        return jsonify({"code": "no"})
    current_book = All_books.query.filter_by(qr=request.form['qr']).first()
    book = Info_about_books.query.filter_by(id_book=current_book.id_book).first()
    username = changed_user.name
    user = User.query.filter_by(id_user=changed_user.id_user).first()
    subject = Subjects.query.filter_by(id_subject=book.id_subject).first().name
    my_class = "без класса"
    if changed_user.is_admin == 0:
        book_class = Classes.query.filter_by(id_class=user.id_class).first()
        my_class = str(book_class.num) + book_class.letter
    authors = " ".join([Authors.query.filter_by(id_author=j).first().name for j in
                        [i.id_author for i in
                         Book_authors.query.filter_by(id_book=book.id_book).all()]])
    current_book.id_user = changed_user.id_user
    db.session.add(current_book)
    db.session.commit()
    return jsonify({"code": "yes", "username": username, "subject": subject,
                    "authors": authors, "my_class": my_class})


@app.route('/accept_book', methods=['POST'])
def accept_book():
    if not current_user.is_authenticated or not (current_user.is_admin > 0):
        return jsonify({"code": "no"})
    current_book = All_books.query.filter_by(qr=request.form['qr']).first()
    current_book.id_user = -1
    db.session.add(current_book)
    db.session.commit()
    return jsonify({"code": "yes"})
