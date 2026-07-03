from flask import redirect, render_template, request, session
from functools import wraps
import pypandoc
import fitz
import os
import time
import PyPDF2
import openai

openai.api_key = ''


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_image(file_path, output_dir):
    dpi = 300
    zoom = dpi / 72
    magnify = fitz.Matrix(zoom, zoom)
    doc = fitz.open(file_path)
    page = doc[0]  # Access the first page
    pix = page.get_pixmap(matrix=magnify)
    unique_id = int(time.time())  # Generate a unique identifier based on the current time
    output_path = os.path.join(output_dir, f"page-0-{unique_id}.png")
    pix.save(output_path)
    return output_path


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

# implement word count checker before you do this
def generate_questions(pdf_text):

    messages = [
        {"role": "system", "content": "You are an expert quiz generator for AP courses."},
        {"role": "user", "content": f"Generate ONLY 10 multiple choice quiz questions (3 easy, 4 medium, 3 hard) along with an answer key at the end based on the CONCEPTS detailed in the following text:\n\n{pdf_text}\n\nQuestions:"}
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1200,
        temperature=0.75,
    )

    questions = response.choices[0].message.content
    return questions


# not being currently used
def convert_to_pdf(doc_path, pdf_path):
    pypandoc.convert_file(doc_path, 'pdf', outputfile=pdf_path)


