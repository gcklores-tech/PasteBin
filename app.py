
from flask import Flask, render_template, redirect, url_for, request, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, datetime
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this-in-production"  # CHANGE THIS!

login_manager = LoginManager(app)
login_manager.login_view = "login"

DB = "site.db"
OWNER_USERNAME = "Admin"
OWNER_PASSWORD = "1[YFx[h2'D1Pa6Ds7:"

# Rank hierarchy (lower index = higher priority)
RANK_HIERARCHY = ["OWNER", "MANAGER", "MOD", "COUNCIL", "HELPER", "MEMBERS"]

def db():
    return sqlite3.connect(DB)

def get_relative_time(created_str):
    """Convert ISO datetime to relative time like '2 hours ago'"""
    try:
        created = datetime.datetime.fromisoformat(created_str.replace(" ", "T"))
        now = datetime.datetime.utcnow()
        diff = now - created
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = int(diff.total_seconds() / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return created.strftime("%Y-%m-%d")
    except:
        return created_str

def is_new_paste(created_str):
    """Check if paste was created less than 24 hours ago"""
    try:
        created = datetime.datetime.fromisoformat(created_str.replace(" ", "T"))
        now = datetime.datetime.utcnow()
        return (now - created) < timedelta(hours=24)
    except:
        return False

def init_db():
    with db() as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, rank TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS pastes (id INTEGER PRIMARY KEY, title TEXT, content TEXT, author TEXT, views INTEGER DEFAULT 0, created TEXT, tags TEXT, pinned INTEGER DEFAULT 0)")
        
        # Add columns if they don't exist (for existing databases)
        try:
            cur.execute("ALTER TABLE pastes ADD COLUMN tags TEXT")
        except:
            pass
        try:
            cur.execute("ALTER TABLE pastes ADD COLUMN pinned INTEGER DEFAULT 0")
        except:
            pass
        
        cur.execute("SELECT * FROM users WHERE username=?", (OWNER_USERNAME,))
        if not cur.fetchone():
            cur.execute("INSERT INTO users (username,password,rank) VALUES (?,?,?)",
                        (OWNER_USERNAME, generate_password_hash(OWNER_PASSWORD), "OWNER"))
        con.commit()

class User(UserMixin):
    def __init__(self, id, username, rank):
        self.id=id; self.username=username; self.rank=rank

@login_manager.user_loader
def load_user(uid):
    with db() as con:
        cur=con.cursor()
        cur.execute("SELECT id,username,rank FROM users WHERE id=?", (uid,))
        u=cur.fetchone()
        return User(*u) if u else None

@app.route("/")
def index():
    search = request.args.get("q", "").lower()
    with db() as con:
        pastes = con.execute("SELECT * FROM pastes ORDER BY pinned DESC, id DESC").fetchall()
    
    # Filter by search query
    if search:
        pastes = [p for p in pastes if search in p[1].lower() or search in p[2].lower() or search in (p[6] or "").lower()]
    
    return render_template("index.html", pastes=pastes, get_relative_time=get_relative_time, is_new_paste=is_new_paste, current_user=current_user)

@app.route("/paste/<int:pid>")
def paste(pid):
    with db() as con:
        con.execute("UPDATE pastes SET views=views+1 WHERE id=?", (pid,))
        p=con.execute("SELECT * FROM pastes WHERE id=?", (pid,)).fetchone()
        con.commit()
    if not p: abort(404)
    return render_template("paste.html", paste=p)

@app.route("/new", methods=["GET","POST"])
def new():
    if request.method=="POST":
        author=current_user.username if current_user.is_authenticated else "Anonymous"
        tags = request.form.get("tags", "")
        with db() as con:
            con.execute("INSERT INTO pastes (title,content,author,created,tags,pinned) VALUES (?,?,?,?,?,?)",
                        (request.form["title"], request.form["content"], author,
                         datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), tags, 0))
            con.commit()
        return redirect(url_for("index"))
    return render_template("new_paste.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        with db() as con:
            u=con.execute("SELECT id,username,password,rank FROM users WHERE username=?",
                          (request.form["username"],)).fetchone()
            if u and check_password_hash(u[2], request.form["password"]):
                login_user(User(u[0],u[1],u[3]))
                return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            with db() as con:
                con.execute("INSERT INTO users (username,password,rank) VALUES (?,?,?)",
                            (request.form["username"], generate_password_hash(request.form["password"]), "MEMBERS"))
                con.commit()
            return redirect(url_for("login"))
        except: pass
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/admin")
@login_required
def admin():
    if current_user.rank != "OWNER": abort(403)
    with db() as con:
        users=con.execute("SELECT id, username, rank FROM users ORDER BY CASE " + 
                         " ".join([f"WHEN rank='{rank}' THEN {i}" for i, rank in enumerate(RANK_HIERARCHY)]) +
                         " ELSE 999 END").fetchall()
    return render_template("admin.html", users=users, rank_hierarchy=RANK_HIERARCHY, current_user=current_user)

@app.route("/delete/<int:pid>")
@login_required
def delete(pid):
    if current_user.rank not in ["OWNER","MANAGER","MOD"]: abort(403)
    with db() as con:
        con.execute("DELETE FROM pastes WHERE id=?", (pid,))
        con.commit()
    return redirect(url_for("index"))

@app.route("/pin/<int:pid>", methods=["POST"])
@login_required
def pin(pid):
    if current_user.rank not in ["OWNER","MANAGER","MOD"]: abort(403)
    with db() as con:
        p = con.execute("SELECT pinned FROM pastes WHERE id=?", (pid,)).fetchone()
        if p:
            con.execute("UPDATE pastes SET pinned=? WHERE id=?", (1 - p[0], pid))
            con.commit()
    return redirect(url_for("index"))

@app.route("/users")
def users_list():
    with db() as con:
        users = con.execute("SELECT id, username, rank FROM users ORDER BY CASE " + 
                           " ".join([f"WHEN rank='{rank}' THEN {i}" for i, rank in enumerate(RANK_HIERARCHY)]) +
                           " ELSE 999 END").fetchall()
    return render_template("users.html", users=users)

@app.route("/admin/user/<int:uid>/rank", methods=["POST"])
@login_required
def change_user_rank(uid):
    if current_user.rank != "OWNER": abort(403)
    
    new_rank = request.form.get("rank")
    if new_rank not in RANK_HIERARCHY:
        abort(400)
    
    with db() as con:
        con.execute("UPDATE users SET rank=? WHERE id=?", (new_rank, uid))
        con.commit()
    
    return redirect(url_for("admin"))

@app.route("/fix-owner/<username>")
def fix_owner(username):
    """Debug route to set OWNER rank - remove after use"""
    with db() as con:
        con.execute("UPDATE users SET rank='OWNER' WHERE username=?", (username,))
        con.commit()
    return f"✅ Updated {username} to OWNER rank. Now <a href='/'>go home</a> and log back in."

if __name__=="__main__":
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
