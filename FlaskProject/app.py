from flask import Flask, request, jsonify, send_file, Response
import uuid
import qrcode
from io import BytesIO
import time
from datetime import datetime
import json

app = Flask(__name__)

BASE_URL = "http://localhost:5000"

STUDENTS = [
    {"id": 1, "name": "Anna Nowak"},
    {"id": 2, "name": "Tadeusz Kukuczko"},
    {"id": 3, "name": "Tomasz Pierdzibąk"},
    {"id": 4, "name": "Marek Psikuta"},
    {"id": 5, "name": "Jan Niezbędny"},
    {"id": 6, "name": "Jessica Andreas"},
    {"id": 7, "name": "Paul Walker"},
]

sessions = {}

def get_student_name(student_id):
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    return student["name"] if student else f"Uczeń: {student_id}"

@app.route('/')
def home():
    return """
        <h1>System ewidencji obecnosci</h1>
        <p><a href="/teacher" style="font-size:20px;">Panel nauczyciela</a></p>
    """

@app.route('/teacher')
def teacher_panel():
    # przygotuj mapę id->name w JSON do JS
    names_map = json.dumps({s["id"]: s["name"] for s in STUDENTS}, ensure_ascii=False)
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Panel Nauczyciela</title>
        <style>
            body {{font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9;}}
            button {{padding: 15px 30px; font-size: 18px; cursor: pointer;}}
            .session {{background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}}
        </style>
    </head>
    <body>
        <h1>Panel nauczyciela – ewidencja obecności</h1>
        <button onclick="startNewSession()">Nowa sesja obecności</button>

        <div id="sessions"></div>

        <script>
            const BASE_URL = "{BASE_URL}";  // ← dodaj to na początku
            const NAMES = {names_map};
            const activeSessions = {{}};
        
            function startNewSession() {{
                fetch('/start_session', {{method: 'POST'}})
                    .then(r => r.json())
                    .then(data => {{
                        const sessionId = data.session_id;
                        activeSessions[sessionId] = true;
                        const qrUrl = `/qr/${{sessionId}}`; // ← wyciągnięty URL
                        
                        let html = `
                            <div class="session" id="session-${{sessionId}}">
                                <h2>Sesja: <b>${{sessionId}}</b></h2>
                                <p><strong>Link dla uczniów:</strong>
                                    <code>${{BASE_URL}}/student/${{sessionId}}</code>
                                </p>
                                <p><img src="${{qrUrl}}" width="280" alt="QR Code"></p>
                                <h3>Obecni uczniowie (<span id="count-${{sessionId}}">0</span>):</h3>
                                <ul id="list-${{sessionId}}"></ul>
                            </div>
                        `;
                        document.getElementById('sessions').innerHTML += html;
                        pollSession(sessionId);
                }});
            }}
        
            function pollSession(sessionId) {{
                const interval = setInterval(() => {{
                    fetch(`/session_status/${{sessionId}}`)
                        .then(r => {{
                            if (r.status === 410) {{
                                clearInterval(interval);
                                const el = document.getElementById(`session-${{sessionId}}`);
                                if (el) el.innerHTML += "<p style='color:red;'>Sesja wygasła.</p>";
                                return null;
                            }}
                            return r.json();
                        }})
                        .then(data => {{
                            if (!data) return;
                            
                            const listEl = document.getElementById(`list-${{sessionId}}`);
                            const countEl = document.getElementById(`count-${{sessionId}}`);
                            
                            if (listEl && countEl) {{
                                listEl.innerHTML = '';
                                
                                if (data.present && data.present.length > 0) {{
                                    data.present.forEach(id => {{
                                        const name = NAMES[id] || ('Uczeń ' + id);
                                        const li = document.createElement('li');
                                        li.textContent = name;
                                        listEl.appendChild(li);
                                    }});
                                }}
                                
                                countEl.textContent = data.present.length;
                            }}
                        }})
                        .catch(err => console.error('Poll error:', err));
                }}, 2000);
            }}
        </script>
    </body>
    </html>
    """

@app.route('/start_session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {
        "present": [],
        "expires": time.time() + 3600
    }

    return jsonify({
        "session_id": session_id,
        "student_url": f"{BASE_URL}/student/{session_id}",
        "present_count": 0
    })


@app.route('/qr/<session_id>')
def generate_qr(session_id):
    print(f"DEBUG: Generuję QR dla sesji: {session_id}")
    print(f"DEBUG: Sesje dostępne: {list(sessions.keys())}")

    if session_id not in sessions:
        print(f"DEBUG: Sesja {session_id} nie znaleziona!")
        return jsonify({"error": "Sesja nie istnieje"}), 404

    if time.time() > sessions[session_id]["expires"]:
        print(f"DEBUG: Sesja {session_id} wygasła!")
        return jsonify({"error": "Sesja wygasła"}), 410

    try:
        url = f"{BASE_URL}/student/{session_id}"
        print(f"DEBUG: URL dla QR: {url}")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        print(f"DEBUG: Obraz QR stworzony")

        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        print(f"DEBUG: Obraz zapisany do bufora, rozmiar: {buf.getbuffer().nbytes}")

        return send_file(buf, mimetype='image/png', as_attachment=False)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/student/<session_id>')
def student_page(session_id):
    if session_id not in sessions or time.time() > sessions[session_id]["expires"]:
        return "<h1> Sesja wygasła lub nie istnieje.<br>Poproś nauczyciela o nowy link.</h1>"

    options = "".join(f'<option value="{s["id"]}">{s["name"]}</option>' for s in STUDENTS)

    return f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial; padding:50px; max-width:600px; margin:auto;">
        <h1>Potwierdź swoją obecność</h1>
        <p><strong>Sesja:</strong> {session_id}</p>

        <form action="/api/mark/{session_id}" method="POST">
            <select name="student_id" style="width:100%; padding:12px; font-size:18px;">
                <option value="">-- Wybierz swoje imię --</option>
                {options}
            </select><br><br>
            <button type="submit" style="padding:15px 40px; font-size:20px; width:100%;">
                Jestem obecny/a
            </button>
        </form>
    </body>
    </html>
    """

@app.route('/api/mark/<session_id>', methods=['POST'])
def api_mark(session_id):
    if session_id not in sessions or time.time() > sessions[session_id]["expires"]:
        return jsonify({"error": "Sesja wygasła"}), 410

    # bezpieczne pobranie student_id z form lub JSON
    sid = request.form.get('student_id')
    if not sid:
        body = request.get_json(silent=True) or {}
        sid = body.get('student_id')

    try:
        student_id = int(sid)
    except Exception:
        return jsonify({"error": "Nieprawidłowy uczeń"}), 400

    if not any(s["id"] == student_id for s in STUDENTS):
        return jsonify({"error": "Nieprawidłowy uczeń"}), 400

    if student_id not in sessions[session_id]["present"]:
        sessions[session_id]["present"].append(student_id)

    return jsonify({
        "success": True,
        "message": f"Obecność potwierdzona: {get_student_name(student_id)}",
        "present_count": len(sessions[session_id]["present"])
    })

@app.route('/session_status/<session_id>')
def session_status(session_id):
    if session_id not in sessions or time.time() > sessions[session_id]["expires"]:
        return jsonify({"error": "Sesja wygasła"}), 410

    return jsonify({
        "session_id": session_id,
        "present": sorted(list(sessions[session_id]["present"]))
    })

if __name__ == '__main__':
    print("=====================================================")
    print("Serwer ewidencji obecności uruchomiony na localhost")
    print("=====================================================")
    print("Nauczyciel:   http://localhost:5000/teacher")
    print("Uczeń:        http://localhost:5000/student/XXXXXX")
    print("=====================================================")
    app.run(host='127.0.0.1', port=5000, debug=False)
