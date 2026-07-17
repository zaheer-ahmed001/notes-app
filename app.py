from flask import Flask, jsonify, request
from config import Config
from models import db, User, Task
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.first():
            default_user = User(
                username="demo",
                email="demo@example.com",
                password_hash=generate_password_hash("demo123")
            )
            db.session.add(default_user)
            db.session.commit()
    return app

app = create_app()

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notes App</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', sans-serif;
                background: #0f172a;
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
                min-height: 100vh;
            }
            .container { max-width: 600px; margin: 0 auto; }
            h1 { color: #38bdf8; text-align: center; }
            .add-form {
                display: flex;
                gap: 8px;
                margin-bottom: 24px;
            }
            input, textarea {
                background: #1e293b;
                border: 1px solid #334155;
                color: #f1f5f9;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
            }
            #noteTitle { flex: 1; }
            button {
                background: #38bdf8;
                border: none;
                color: #0f172a;
                padding: 10px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            button:hover { background: #4ade80; }
            .note {
                background: #1e293b;
                border-radius: 8px;
                padding: 14px 16px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .note-title { font-weight: 600; }
            .note-desc { color: #94a3b8; font-size: 13px; margin-top: 4px; }
            .delete-btn {
                background: #f87171;
                color: #0f172a;
                padding: 6px 10px;
                font-size: 12px;
            }
            .delete-btn:hover { background: #ef4444; }
            .empty { text-align: center; color: #64748b; margin-top: 40px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Notes App</h1>
            <div class="add-form">
                <input type="text" id="noteTitle" placeholder="Write Here....">
                <button onclick="addNote()">Add</button>
            </div>
            <div id="notesList"></div>
        </div>

        <script>
            const USER_ID = 1;

            async function loadNotes() {
                const res = await fetch('/tasks');
                const notes = await res.json();
                const list = document.getElementById('notesList');
                if (notes.length === 0) {
                    list.innerHTML = '<p class="empty">No notes yet. Add one above.</p>';
                    return;
                }
                list.innerHTML = notes.map(n => `
                    <div class="note">
                        <div>
                            <div class="note-title">${n.title}</div>
                            ${n.description ? `<div class="note-desc">${n.description}</div>` : ''}
                        </div>
                        <button class="delete-btn" onclick="deleteNote(${n.id})">Delete</button>
                    </div>
                `).join('');
            }

            async function addNote() {
                const titleInput = document.getElementById('noteTitle');
                const title = titleInput.value.trim();
                if (!title) return;
                await fetch('/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, user_id: USER_ID })
                });
                titleInput.value = '';
                loadNotes();
            }

            async function deleteNote(id) {
                await fetch('/tasks/' + id, { method: 'DELETE' });
                loadNotes();
            }

            document.getElementById('noteTitle').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') addNote();
            });

            loadNotes();
        </script>
    </body>
    </html>
    """

@app.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(username=data["username"], email=data["email"],
                password_hash=generate_password_hash(data["password"]))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route("/users", methods=["GET"])
def list_users():
    return jsonify([u.to_dict() for u in User.query.all()])

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    task = Task(title=data["title"], description=data.get("description"),
                user_id=data["user_id"])
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify([t.to_dict() for t in Task.query.all()])

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"deleted": task_id}), 200

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    db.session.commit()
    return jsonify(task.to_dict()), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
