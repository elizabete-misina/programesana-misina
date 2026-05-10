from flask import Flask, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)


def get_db_connection():
    db = Path(__file__).parent / "emociju-dienasgramata.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/par-mums")
def about():
    return render_template("about.html")


@app.route('/apraksti')
def descriptions():
    conn = get_db_connection()
    emotions = conn.execute('''
        SELECT 
            emotions.*, 
            categories.nosaukums AS kategorija, 
            visuals.krasas_kods 
        FROM emotions
        JOIN categories ON emotions.category_id = categories.id
        JOIN visuals ON emotions.id = visuals.emotion_id
    ''').fetchall()
    conn.close()
    return render_template('descriptions.html', emotions=emotions)


@app.route('/apraksti/<int:emotion_id>')
def description_detail(emotion_id):
    conn = get_db_connection()
    emotion = conn.execute('''
        SELECT e.*, c.nosaukums AS kategorija, v.krasas_kods 
        FROM emotions e
        JOIN categories c ON e.category_id = c.id
        JOIN visuals v ON e.id = v.emotion_id
        WHERE e.id = ?''', (emotion_id,)).fetchone()

    synonyms = conn.execute(
        'SELECT * FROM synonyms WHERE emotion_id = ?', (emotion_id,)).fetchall()
    conn.close()
    return render_template('description_detail.html', emotion=emotion, synonyms=synonyms)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
