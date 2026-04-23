import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import secrets

# PATH CONFIGURATION
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "adi_premium_key_2026" # Changed key to force reset old sessions

# --- Database Simulation ---
ADMIN_CREDENTIALS = {"id": "123", "pass": "123"}
users_db = {}
data_store = {"Silver": [], "Gold": [], "Grand": []}

# --- Page Routes with Session Protection ---

@app.route('/')
def user_login_page():
    # If already logged in as user, go to dashboard
    if session.get('role') == 'user':
        return redirect(url_for('user_dashboard'))
    return render_template('user_login.html')

@app.route('/master-access')
def admin_login_page():
    # If already logged in as admin, go to dashboard
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    # Strict Check: If not admin, kick back to login
    if session.get('role') != 'admin':
        session.clear()
        return redirect(url_for('admin_login_page'))
    return render_template('admin.html')

@app.route('/user')
def user_dashboard():
    # Strict Check: If not user, kick back to login
    if session.get('role') != 'user':
        session.clear()
        return redirect(url_for('user_login_page'))
    return render_template('user.html')

# --- Logic Routes ---

@app.route('/login', methods=['POST'])
def login():
    # CRITICAL: Clear any old session before starting a new one
    session.clear()
    
    data = request.json
    uid = data.get('id')
    pwd = data.get('pass')
    role = data.get('role')

    if role == "admin":
        if uid == ADMIN_CREDENTIALS['id'] and pwd == ADMIN_CREDENTIALS['pass']:
            session['user'] = uid
            session['role'] = 'admin'
            session.permanent = True # Keeps the session stable
            return jsonify({"status": "success", "redirect": "/admin"})
        return jsonify({"status": "error", "message": "Invalid Admin Credentials"}), 401

    # User Login / Auto-Registration
    if not uid or not pwd:
        return jsonify({"status": "error", "message": "Missing credentials"}), 400
        
    if uid not in users_db:
        users_db[uid] = pwd
    elif users_db[uid] != pwd:
        return jsonify({"status": "error", "message": "Incorrect Password"}), 401
    
    session['user'] = uid
    session['role'] = 'user'
    session.permanent = True
    return jsonify({"status": "success", "redirect": "/user"})

@app.route('/api/generate', methods=['POST'])
def generate():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    cat = request.json.get('category')
    
    if cat == "Silver":
        data_store["Silver"] = []
        # 10 Winners: 1k to 5.5k (₹500 increments)
        for i in range(10):
            prize = 1000 + (i * 500)
            ticket = str(secrets.randbelow(900000) + 100000)
            data_store["Silver"].append({"ticket": ticket, "prize": prize})
        # 1 Rank One: ₹5000
        data_store["Silver"].append({"ticket": str(secrets.randbelow(900000) + 100000), "prize": 5000})
        msg = "Silver Draw Successful (11 Winners)"

    elif cat == "Gold":
        # 6 Winners: 7k to 12k (₹1k increments)
        data_store["Gold"] = [{"ticket": str(secrets.randbelow(900000) + 100000), "prize": 7000 + (i*1000)} for i in range(6)]
        msg = "Gold Draw Successful (6 Winners)"

    elif cat == "Grand":
        data_store["Grand"] = [{"ticket": str(secrets.randbelow(900000) + 100000), "prize": 100000}]
        msg = "Grand Prize Set (₹1,00,000)"
    
    return jsonify({"status": "success", "message": msg})

@app.route('/api/results')
def get_results():
    return jsonify(data_store)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_login_page'))

if __name__ == '__main__':
   
    
    print(f" user page: http://127.0.0.1:5000/")
    print(f" admin page: http://127.0.0.1:5000/master-access")
   
    app.run(debug=True) 