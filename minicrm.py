from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Client, Note
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "crm-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicia sesión para continuar."

STATUS_LABELS = {
    "lead":     {"label": "Lead",     "color": "warning"},
    "active":   {"label": "Activo",   "color": "success"},
    "inactive": {"label": "Inactivo", "color": "secondary"},
}

@app.context_processor
def inject_globals():
    return {"STATUS_LABELS": STATUS_LABELS}

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("El usuario o email ya existe.", "danger")
        elif len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "warning")
        else:
            user = User(username=username, email=email,
                        password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    clients  = Client.query.filter_by(user_id=current_user.id).all()
    total    = len(clients)
    leads    = sum(1 for c in clients if c.status == "lead")
    active   = sum(1 for c in clients if c.status == "active")
    inactive = sum(1 for c in clients if c.status == "inactive")
    recent   = sorted(clients, key=lambda c: c.created_at, reverse=True)[:5]
    return render_template("dashboard.html",
        total=total, leads=leads, active=active, inactive=inactive, recent=recent)


# ── Clients ───────────────────────────────────────────────────────────────────

@app.route("/clients")
@login_required
def clients():
    q      = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    query  = Client.query.filter_by(user_id=current_user.id)
    if q:
        query = query.filter(
            (Client.name.ilike(f"%{q}%")) |
            (Client.company.ilike(f"%{q}%")) |
            (Client.email.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter_by(status=status)
    client_list = query.order_by(Client.created_at.desc()).all()
    return render_template("clients.html", clients=client_list, q=q, status=status)


@app.route("/clients/add", methods=["GET", "POST"])
@login_required
def add_client():
    if request.method == "POST":
        client = Client(
            user_id=current_user.id,
            name=request.form["name"].strip(),
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            company=request.form.get("company", "").strip(),
            status=request.form.get("status", "lead"),
        )
        db.session.add(client)
        db.session.commit()
        flash("Cliente agregado.", "success")
        return redirect(url_for("client_detail", client_id=client.id))
    return render_template("add_client.html")


@app.route("/clients/<int:client_id>")
@login_required
def client_detail(client_id):
    client = db.get_or_404(Client, client_id)
    if client.user_id != current_user.id:
        return redirect(url_for("clients"))
    notes = sorted(client.notes, key=lambda n: n.created_at, reverse=True)
    return render_template("client_detail.html", client=client, notes=notes)


@app.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    client = db.get_or_404(Client, client_id)
    if client.user_id != current_user.id:
        return redirect(url_for("clients"))
    if request.method == "POST":
        client.name    = request.form["name"].strip()
        client.email   = request.form.get("email", "").strip()
        client.phone   = request.form.get("phone", "").strip()
        client.company = request.form.get("company", "").strip()
        client.status  = request.form.get("status", "lead")
        db.session.commit()
        flash("Cliente actualizado.", "success")
        return redirect(url_for("client_detail", client_id=client.id))
    return render_template("edit_client.html", client=client)


@app.route("/clients/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    client = db.get_or_404(Client, client_id)
    if client.user_id != current_user.id:
        return redirect(url_for("clients"))
    db.session.delete(client)
    db.session.commit()
    flash("Cliente eliminado.", "success")
    return redirect(url_for("clients"))


# ── Notes ─────────────────────────────────────────────────────────────────────

@app.route("/clients/<int:client_id>/notes/add", methods=["POST"])
@login_required
def add_note(client_id):
    client = db.get_or_404(Client, client_id)
    if client.user_id != current_user.id:
        return redirect(url_for("clients"))
    content = request.form.get("content", "").strip()
    if content:
        note = Note(client_id=client_id, content=content)
        db.session.add(note)
        db.session.commit()
        flash("Nota agregada.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id):
    note   = db.get_or_404(Note, note_id)
    client = db.get_or_404(Client, note.client_id)
    if client.user_id != current_user.id:
        return redirect(url_for("clients"))
    client_id = note.client_id
    db.session.delete(note)
    db.session.commit()
    flash("Nota eliminada.", "success")
    return redirect(url_for("client_detail", client_id=client_id))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
