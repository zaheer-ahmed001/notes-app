from flask import Flask, jsonify, request
from config import Config
from models import db, User, Task
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

app = create_app()

@app.route("/")
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notes API</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: #0f172a;
                color: #f1f5f9;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            h1 { color: #38bdf8; }
            ul { list-style: none; padding: 0; }
            li { margin: 8px 0; font-size: 18px; }
            a { color: #4ade80; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .status {
                margin-top: 20px;
                padding: 6px 14px;
  
                border-radius: 20px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <h1>Notes API</h1>
        <p class="status"> Server is running</p>
        <ul>
            <li><a href="/health">/health</a> — check DB connection</li>
            <li><a href="/users">/users</a> — list users</li>
            <li><a href="/tasks">/tasks</a> — list tasks</li>
        </ul>
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)