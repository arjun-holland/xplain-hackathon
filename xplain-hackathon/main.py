import os
import google.generativeai as genai
import aixplain as axp
from googleapiclient.discovery import build
from google.oauth2 import service_account
from flask import Flask, request, jsonify, send_file
import yt_dlp
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import ssl
import certifi
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
api="AIzaSyDmO3b9U0oHgYwd__B4I_uSNbsp3Az4epc"
from aixplain.factories import ModelFactory
from aixplain.enums import Function
from pytube import YouTube
# YouTube._cache.clear()

app = Flask(__name__)
app.secret_key = "your_secret_key"
import os

os.environ["TEAM_API_KEY"] = "c08655841f17c61bf73ba3e11bae3e5eb388147bac20bf9ff70abb87709ce68d"

AIXPLAIN_API_KEY = "c08655841f17c61bf73ba3e11bae3e5eb388147bac20bf9ff70abb87709ce68d"
TEAM_API_KEY = "c08655841f17c61bf73ba3e11bae3e5eb388147bac20bf9ff70abb87709ce68d"
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

@app.route('/student_dashboard')
def student_dashboard():
    if 'user' in session:
        return render_template('student_dashboard.html', username=session['user'])
    return redirect(url_for('home'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user' in session:
        return render_template('teacher_dashboard.html', username=session['user'])
    return redirect(url_for('home'))

@app.route('/process_selection', methods=['POST'])
def process_selection():
    selected_class = request.form.get('class')
    selected_subject = request.form.get('subject')
    knowledge_level = request.form.get('level')

    if not selected_class or not selected_subject or not knowledge_level:
        return "Please select all fields", 400

    return redirect(url_for('result_page', selected_class=selected_class, 
                            selected_subject=selected_subject, 
                            knowledge_level=knowledge_level))

@app.route('/result')
def result():
    raw_data = request.args.get("query", "{}")  # Get the 'data' parameter from URL
    try:
        import json
        data = json.loads(raw_data)  # Convert string to dictionary
        video_items = data.get("items", [])  # Extract the list of video items
    except json.JSONDecodeError:
        video_items = []  # Handle invalid JSON gracefully

    return render_template("result.html", result=video_items)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))



SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    "/home/gayathriacharigeetha/Aixplain_yt/adroit-marking-227912-1254f2a39b82.json", scopes=SCOPES)
youtube=build("youtube","v3",credentials=credentials)

aixplain_url = "https://api.aixplain.com/analyze"

def searchquery(query):
    search_results=youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=5,
        order="relevance"
        )
    response=search_results.execute()
    print("response-------", response)
    # return [{"title": item["snippet"]["title"], 
    #          "channel": item["snippet"]["channelTitle"], 
    #          "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"} 
    #         for item in response["items"]]
    return response





def enhance_with_aixplain(query):
    """Refine the search query using AIxplain's NLP tools."""
    #models = list_models()
    #if not models:
     #   return query  # If no models are available, return original query
    
    model_id ="674a17f8098e7d5b18453db"
    #models[0]["id"]  # Pick the first available model (replace with a valid ID)
    
    try:
        model = axp.Aixplain.Model(model_id)
        result = model.run({"text": query})  # Process query
        return result.get("output", query)  # Return refined query or fallback
    except Exception as e:
        print(f"AIxplain Error: {e}")
        return query  # Return original query if enhancement fails

# Test AIxplain Enhancement
#query = "basic courses of machine learning"
#enhanced_query = enhance_with_aixplain(query)
#print(f"Enhanced Query: {enhanced_query}")

# def generatesearchquery(subject,level):
#     prompt = f""" You are a artificially intelligent bot that create search queries based on level of subject for students in a particular subject.
#                    Find courses that would be basic if the knowledge level is low , advance concepts if the knowledge level is advanced and
#                    if the knowledge level is high  projects on {subject}.
                  
#                   high scores  range from 65-100
#                   Example:
                  
#                   Embedded systems:basic
                  
#                   Query: basic  courses of embedded systems
#                   Second Example:
#                   Subject:IoT
#                   Knowledgelevel:Advanced
#                   Query:Advance courses of IoT
#                 Third  Example:
#                   Subject:Linux
#                   Knowledgelevel:High
#                   Query:Projects in Linux

#                   Now generate query based on {subject} and {level}
#                 """
#     client = genai.Client(api_key="AIzaSyCafuTJN94kBNSyi5W0ngs9_wlWOznOpe8")
#     response = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt])
#     print(response.text)
#     raw_query = response.text
#     enhanced_query = enhance_with_aixplain(raw_query)
#     return enhanced_query

def generatesearchquery(subject, level):
    prompt = f"""You are an AI bot that creates search queries based on the knowledge level of students in {subject}.
                 - If knowledge level is low (0-64), find **basic courses**.
                 - If knowledge level is advanced (65-89), find **advanced courses**.
                 - If knowledge level is high (90-100), find **projects**.

                 Examples:
                 - Subject: Embedded systems, Level: Basic → Query: "basic courses of embedded systems"
                 - Subject: IoT, Level: Advanced → Query: "advanced courses of IoT"
                 - Subject: Linux, Level: High → Query: "projects in Linux"

                 Now generate a query for: Subject: {subject}, Level: {level}.
              """

    genai.configure(api_key="AIzaSyCafuTJN94kBNSyi5W0ngs9_wlWOznOpe8")  # Correct way to set API key
    model = genai.GenerativeModel("gemini-1.5-flash")  # Use latest model
    response = model.generate_content(prompt)  # Get response

    raw_query = response.text.strip()
    return raw_query



# gemini_text=generatesearchquery('os',90)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Ensure download folder exists

@app.route("/download_video/<video_id>", methods=["GET"])
def download_video(video_id):
    if not video_id:
        return jsonify({"error": "No video ID provided"}), 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500





model_list = ModelFactory.list(function=Function.TEXT_GENERATION, page_size=50)["results"]

for model in model_list:
    print(model.id, model.name, model.supplier)

@app.route("/generate-query", methods=["GET"])
def generate_query_api():
    subject = request.args.get("subject")
    level = request.args.get("level")
    if not subject or not level:
        return jsonify({"error": "Missing subject or level"}), 400

    result = searchquery(generatesearchquery(subject,level))
    print("result-----", {"data": result})

    return jsonify(result)


@app.route("/search", methods=["GET"])
def search_videos():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    results = searchquery(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
