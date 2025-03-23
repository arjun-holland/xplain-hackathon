import os
import ssl
import certifi
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import aixplain as axp
import google.generativeai as genai
# from google.generativeai.models import gemini
import google.generativeai as genai
api=os.environ.get("AIzaSyDmO3b9U0oHgYwd__B4I_uSNbsp3Az4epc")
from aixplain.factories import ModelFactory
from aixplain.enums import Function


SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    "adroit-marking-227912-1254f2a39b82.json", scopes=SCOPES)
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
    print("response", response)
    return [{"title": item["snippet"]["title"], 
             "channel": item["snippet"]["channelTitle"], 
             "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"} 
            for item in response["items"]]



AIXPLAIN_API_KEY = "c08655841f17c61bf73ba3e11bae3e5eb388147bac20bf9ff70abb87709ce68d"
TEAM_API_KEY = "c08655841f17c61bf73ba3e11bae3e5eb388147bac20bf9ff70abb87709ce68d"

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
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# searchquery(generatesearchquery("operating system",90))
def download_video(video_id):
    """Download YouTube video using pytube."""
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        stream = yt.streams.get_highest_resolution()
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{yt.title}.mp4")
        stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{yt.title}.mp4")
        return file_path
    except Exception as e:
        return str(e)

model_list = ModelFactory.list(function=Function.TEXT_GENERATION, page_size=50)["results"]

for model in model_list:
    print(model.id, model.name, model.supplier)

@app.route("/generate-query", methods=["GET"])
def generate_query_api():
    subject = request.args.get("subject")
    level = request.args.get("level")
    if not subject or not level:
        return jsonify({"error": "Missing subject or level"}), 400

    query = searchquery(generatesearchquery(subject,level))
    return jsonify({"query": query})

@app.route("/search", methods=["GET"])
def search_videos():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    results = searchquery(query)
    return jsonify(results)