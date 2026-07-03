import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, jsonify, url_for, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote

from helpers import apology, login_required, allowed_file, convert_to_image, extract_text_from_pdf, generate_questions


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

MAX_FILE_SIZE = 10 * 1024 * 1024

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("must provide username/password", 400)
        if password != confirmation:
            return apology("passwords don't match", 400)
        try:
            db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, generate_password_hash(password))
            return redirect("/login")
        except ValueError:
            return apology("username already exists", 400)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Allows users to uplaod a document"""
    if request.method == "GET":
        classes = db.execute("SELECT id, class_name FROM classes;")
        return render_template("upload.html", classes=classes)
    else:
        # check whether it's a valid type
        user_id = session["user_id"]

        # creates a path for the user's uploads
        user_directory = os.path.join('static', 'uploads', str(user_id))
        title = request.form.get("title")
        selected_class_id = request.form.get("selected_class")

        # creates a directory for the user
        os.makedirs(user_directory, exist_ok=True)

        if 'myfile' not in request.files:
            return apology("No file part", 400)

        # checks for inputs
        if not title:
            return apology("Title is required", 400)
        if not selected_class_id:
            return apology("Class selection is required", 400)
        file = request.files['myfile']

        # sanitizing it so you can't traverse it maliciously
        basename = os.path.basename(file.filename)

        file_path = os.path.join(user_directory, basename)
        if basename == '':
            return apology("No selected file", 400)
        if not allowed_file(basename):
            return apology("File type not allowed", 400)
        if file and file.content_length > MAX_FILE_SIZE:
            return apology("Max file size is 10 MB", 400)
        if file:
            # saves it to the path and inserts it into the database
            file.save(file_path)
            thumbnail_path = convert_to_image(file_path, user_directory)

            db.execute("INSERT INTO notes(title, file_path, user_id, class_id, thumbnail_path) VALUES (?, ?, ?, ?, ?)", title, file_path, user_id, selected_class_id, thumbnail_path)
            return render_template("upload-success.html")


@app.route("/", methods=["GET"])
@login_required
def index():
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)  # get the current page from the url parameters
        selected_class = request.args.get("class_id", type=int)
        pdfs_per_page = 6

        # get classes for dropdown menu
        classes = db.execute("SELECT id, class_name FROM classes;")

        query = (
            "SELECT notes.title, notes.file_path, users.username, classes.class_name, notes.thumbnail_path "
            "FROM notes JOIN users ON notes.user_id = users.id JOIN classes ON notes.class_id = classes.id"
        )


        # filters by class if class_id is provided
        if selected_class:
            # inserts the class specification into the query in order to filter by class

            query += " WHERE classes.id = :class_id"

            # sorts by newest added first
            query += " ORDER BY notes.id DESC"
            all_notes = db.execute(query, class_id=selected_class)
        else:
            # sorts by newest added first
            query += " ORDER BY notes.id DESC"
            all_notes = db.execute(query)

        # calculates total pages
        note_count = len(all_notes)
        total_pages = (note_count + pdfs_per_page - 1) // pdfs_per_page

        start = (page - 1) * pdfs_per_page
        end = start + pdfs_per_page

        # slices the list of notes for the pagination
        notes = all_notes[start:end]

        return render_template("index.html", notes=notes, total_pages=total_pages, note_count=note_count, page=page, start=start, end=end, classes=classes, selected_class=selected_class)


@app.route('/pdf/<path:file_path>')
@login_required
def pdf_view(file_path):
    # fetch the title without filtering by user_id (had the issue where title wouldn't display if the pdf wasn't uploaded by the same user)
    title_result = db.execute("SELECT title FROM notes WHERE file_path = ?;", file_path)
    if title_result:
        title = title_result[0]['title']
    else:
        title = "Error: Title Not Found"  # fallback title if not found

    class_result = db.execute("SELECT classes.class_name FROM notes JOIN classes ON notes.class_id = classes.id WHERE file_path = ?;", file_path)

    if class_result:
        class_name = class_result[0]['class_name']
    else:
        class_name = "Error: Class Not Found"

    return render_template('pdf_view.html', file_path=file_path, title=title, class_name=class_name)


@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({"error": "File path is missing"}), 400
    if not file_path:
        return jsonify({"error": "File path is missing"}), 400

    # extract text from the PDF (implement PDF text extraction)
    pdf_text = extract_text_from_pdf(file_path)
    words = pdf_text.split()
    word_count = len(words)
    if word_count < 5000:
        # generate quiz using OpenAI API
        quiz_questions = generate_questions(pdf_text)

        if quiz_questions:
            print(f"Generated questions: {quiz_questions}")
        else:
            print("No questions generated.")

        return jsonify({"questions": quiz_questions})
    else:
        return jsonify({"error": "The document is too long. Please provide a document with fewer than 5000 words."}), 400


# removes spaces in pdf names
def urlencode_filter(s):
    return quote(s)

@app.route('/delete_pdf', methods=['POST'])
@login_required
def delete_pdf():
    user_id = session["user_id"]
    data = request.get_json()
    file_path = data.get("file_path")

    # check if the file exists and belongs to the user
    pdf_record = db.execute("SELECT * FROM notes WHERE file_path = ? AND user_id = ?", file_path, user_id)
    if not pdf_record:
        return jsonify({"success": False, "message": "Unauthorized or file not found"}), 403

    try:
        # delete the file from the filesystem
        if os.path.exists(file_path):
            os.remove(file_path)

        # delete the record from the database
        db.execute("DELETE FROM notes WHERE file_path = ? AND user_id = ?", file_path, user_id)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



#    from pdf_view function: file_path = db.execute("SELECT file_path FROM notes WHERE user_id = ? AND title = ?;", user_id, title)

