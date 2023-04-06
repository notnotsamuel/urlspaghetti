from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import string
from time import sleep

app = Flask(__name__)
app.config.from_object('config.Config')

def shorten_url(original_url):
    # Generate a unique short URL
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=4))

    # check validity of the URL
    if not original_url.startswith("http://") and not original_url.startswith("https://"):
        original_url = "http://" + original_url
    
    
    # check for sql injection
    if "'" in original_url:
        original_url = original_url.replace("'", "''")
    
    # don't make them think it's too fast :) (best ddos protection ever)
    sleep(4)

    # Save the URL pair to the database
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO urls (original, short) VALUES (?, ?)", (original_url, short_url))

    return short_url

def retrieve_data(short_url):
    # Retrieve the original URL and visits from the database
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original, visits FROM urls WHERE short = ?", (short_url,))
        datas = cursor.fetchone()

    return datas[0] if datas else None, datas[1] if datas else None

def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT NOT NULL,
            short TEXT NOT NULL UNIQUE,
            visits INTEGER DEFAULT 0
        );
        """)

def connect_db():
    return sqlite3.connect(app.config['DATABASE_URI'])

# Route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        shortened = shorten_url(url)
        return redirect(url_for("shortened", short_url=shortened))
    return render_template("index.html")

# Route for displaying the shortened URL
@app.route("/<short_url>")
def shortened(short_url):
    original_url, visits = retrieve_data(short_url)
    # update the visits
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE urls SET visits = ? WHERE short = ?", (visits + 1, short_url))
    return render_template("shortened.html", short_url=short_url, original_url=original_url, visits=visits)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000)