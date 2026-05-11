from flask import Flask, render_template, redirect, request, url_for
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

@app.route('/log_mood', methods=['GET', 'POST'])
def log_mood():
    conn = get_db_connection()
    
    if request.method == 'POST':
        emotion_id = request.form.get('emotion_id')
        intensity = request.form.get('intensity')
        note = request.form.get('note')
        
        conn.execute('INSERT INTO mood_logs (emotion_id, intensity, note) VALUES (?, ?, ?)',
                     (emotion_id, intensity, note))
        conn.commit()
        # After saving, we stay on the same page to see the new log
        return redirect(url_for('log_mood'))
    
    # GET: Fetch everything to show on the page
    emotions = conn.execute('SELECT * FROM emotions').fetchall()
    
    # Fetch logs and join with emotions to get the name and color!
    logs = conn.execute('''
        SELECT mood_logs.*, emotions.vards 
        FROM mood_logs 
        JOIN emotions ON mood_logs.emotion_id = emotions.id
    ''').fetchall()
    
    conn.close()
    return render_template('log_mood.html', emotions=emotions, logs=logs)

@app.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM mood_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('log_mood'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
