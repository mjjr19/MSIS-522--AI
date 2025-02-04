from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import os
from jinja2 import Template

app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")  

# HTML Template for Chat Interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Personal Trainer</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f8f9fa; }
        #chatbox { width: 50%; margin: auto; padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        input, button { padding: 10px; margin: 5px; width: 80%; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background-color: #d1ecf1; text-align: left; padding: 10px; border-radius: 10px; }
        .bot { background-color: #d4edda; text-align: left; padding: 10px; border-radius: 10px; }
    </style>
</head>
<body>
    <h1 class="my-4">💪 AI Personal Trainer</h1>
    <div id="chatbox" class="container p-3">
        <div id="messages" class="mb-3"></div>
        <input type="text" id="user_input" class="form-control" placeholder="Ask me something..." />
        <button class="btn btn-primary mt-2" onclick="sendMessage()">Send</button>
    </div>

    <script>
        async function sendMessage() {
            let userInput = document.getElementById("user_input").value;
            let messagesDiv = document.getElementById("messages");

            messagesDiv.innerHTML += `<p class="message user"><strong>You:</strong> ${userInput}</p>`;

            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userInput })
            });

            let data = await response.json();
            let botReply = data.response || "I couldn't process that.";

            messagesDiv.innerHTML += `<p class="message bot"><strong>Bot:</strong> ${botReply}</p>`;
            document.getElementById("user_input").value = "";
        }
    </script>
</body>
</html>
"""


# Serve HTML Webpage
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    return HTMLResponse(content=html_template)

# Chatbot API Endpoint
@app.post("/chat")
async def chatbot(request: Request):
    data = await request.json()
    user_message = data.get("message", "").lower()

    # Check if user is asking about meal plans
    if "meal" in user_message or "food" in user_message:
        return get_meal_recommendation()

    # Check if user is asking about workouts
    elif "workout" in user_message or "exercise" in user_message:
        return get_workout_recommendation()

    # Default response using GPT
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful AI fitness trainer."},
                      {"role": "user", "content": user_message}]
        )
        return {"response": response["choices"][0]["message"]["content"]}

# Fetch meal recommendations from Firebase
def get_meal_recommendation():
    meal_docs = db.collection("meal_plans").stream()
    meals = [meal.to_dict() for meal in meal_docs]
    
    if meals:
        recommended_meal = meals[0]
        return {
            "response": f"{recommended_meal['name']} ({recommended_meal['cuisine']}) - {recommended_meal['calories']} calories."
        }
    else:
        return {"response": "No meals found in the database."}

# Fetch workout recommendations from Firebase
def get_workout_recommendation():
    workout_docs = db.collection("workouts").stream()
    workouts = [workout.to_dict() for workout in workout_docs]

    if workouts:
        recommended_workout = workouts[0]
        return {
            "response": f"Workout: {recommended_workout['name']} for {recommended_workout['goal']}. Exercises: {', '.join(recommended_workout['exercises'])}."
        }
    else:
        return {"response": "No workouts found in the database."}
