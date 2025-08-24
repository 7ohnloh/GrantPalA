from flask import Flask, render_template, request, jsonify, redirect, url_for
from services.checkerpal_logic import extract_grant_info
from database import get_db, init_db, close_connection
from services.eligibilityresults import eligibility_bp
from services.calendar_service import create_calendar_event
from services.answerpal_logic import handle_generate, handle_regenerate
from flask import send_from_directory
from flask_cors import CORS




app = Flask(__name__)
init_db(app)
app.register_blueprint(eligibility_bp)
CORS(app, supports_credentials=True)

# ============ ROUTES ============

@app.route('/answerpalapp/<path:filename>')
def serve_answerpal(filename):
    return send_from_directory('static/answerpal', filename)



@app.route("/generate", methods=["POST"])
def generate():
    return handle_generate()

@app.route("/regenerate", methods=["POST", "OPTIONS"])
def regenerate():
    return handle_regenerate()



@app.route('/')
def home():
    db = get_db()
    matches = db.execute('''
        SELECT 
            m.match_score,
            m.is_urgent,
            g.name AS grant_name,
            g.timeline AS grant_timeline,
            g.budget AS grant_budget,
            p.name AS project_name,
            p.timeline AS project_timeline,
            p.budget AS project_budget
        FROM matches m
        JOIN grants g ON m.grant_id = g.id
        JOIN projects p ON m.project_id = p.id
        ORDER BY m.id DESC
    ''').fetchall()
    return render_template('home.html', matches=matches)

@app.route('/add-to-calendar', methods=['POST'])
def add_to_calendar():
    try:
        data = request.json
        title = data.get("title")
        description = data.get("description", "")
        due_date = data.get("date")

        if not title or not due_date:
            return jsonify({"error": "Missing required fields"}), 400

        create_calendar_event(title, description, due_date)
        return jsonify({"success": True})

    except Exception as e:
        print("❌ Calendar error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/checkerpal')
def checkerpal():
    return render_template('checkerpal.html')

@app.route('/answerpal')
def answerpal():
    return render_template('answerpal.html')

@app.route('/eligibility')
def eligibility():
    return render_template('eligibility.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    file = request.files.get("file")
    url = request.form.get("url")
    mode = request.form.get("mode", "grant")  # "grant" or "project"

    print("📩 Received POST to /evaluate")
    print(f"🔁 Mode: {mode}")

    try:
        data = extract_grant_info(file=file, url=url, mode=mode)
        return jsonify(data)

    except Exception as e:
        print("❌ Error in evaluate route:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/save_match', methods=['POST'])
def save_match():
    db = get_db()

    grant = db.execute('SELECT * FROM grants ORDER BY id DESC LIMIT 1').fetchone()
    if not grant:
        return "No grant found in database.", 400

    project_name = request.form.get("project_name")
    project_timeline = request.form.get("project_timeline")
    project_budget = request.form.get("project_budget")
    project_tags = request.form.get("project_tags")
    match_percent = int(request.form.get("match_percent"))
    is_urgent = request.form.get("is_urgent") == "True"

    cursor = db.execute('''
        INSERT INTO projects (name, timeline, budget, directions, source_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        project_name,
        project_timeline,
        project_budget,
        project_tags,
        ""
    ))
    project_id = cursor.lastrowid

    db.execute('''
        INSERT INTO matches (grant_id, project_id, match_score, is_urgent)
        VALUES (?, ?, ?, ?)
    ''', (grant['id'], project_id, match_percent, is_urgent))

    db.commit()

    return redirect(url_for('home'))

# ============ MAIN ============

if __name__ == '__main__':
    app.run(debug=True)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)
