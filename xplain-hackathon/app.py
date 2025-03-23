from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB Connection
client = MongoClient("mongodb+srv://xplain:xplain123@cluster0.ipjd4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["xplain_db"]
users = db["user_records"]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get("signupUsername")
    email = request.form.get("signupEmail")
    password = generate_password_hash(request.form.get("signupPassword"))
    
    if users.find_one({"email": email}):
        return "Email already exists!", 400
    
    users.insert_one({"username": username, "email": email, "password": password})
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get("loginEmail")
    password = request.form.get("loginPassword")
    user = users.find_one({"email": email})
    
    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']
        return redirect(url_for('dashboard'))
    
    return "Invalid credentials!", 401

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    return redirect(url_for('home'))

@app.route('/process_selection', methods=['POST'])
def process_selection():
    # Get form data
    selected_class = request.form.get('class')
    selected_subject = request.form.get('subject')
    knowledge_level = request.form.get('level')

    # Render the result.html template with the selected data
    return render_template('result.html', selected_class=selected_class, selected_subject=selected_subject, knowledge_level=knowledge_level)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
