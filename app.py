from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/par-mums")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)