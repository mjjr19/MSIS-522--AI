import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Make sure this file is present
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sample Meal Plans
meal_plans = [
    {"name": "High Protein Breakfast", "cuisine": "American", "calories": 400, "ingredients": ["Eggs", "Oats", "Banana"]},
    {"name": "Halal Chicken Biryani", "cuisine": "Indian", "calories": 600, "ingredients": ["Chicken", "Rice", "Spices"]},
    {"name": "Vegetarian Stir Fry", "cuisine": "Chinese", "calories": 450, "ingredients": ["Tofu", "Broccoli", "Soy Sauce"]}
]

# Sample Workouts
workout_plans = [
    {"name": "Full Body Strength", "goal": "Muscle Gain", "duration": 45, "exercises": ["Squats", "Deadlifts", "Bench Press"]},
    {"name": "Fat Burn Cardio", "goal": "Fat Loss", "duration": 30, "exercises": ["Jump Rope", "Burpees", "Cycling"]},
    {"name": "Yoga Recovery", "goal": "Recovery", "duration": 20, "exercises": ["Downward Dog", "Child's Pose", "Cobra Stretch"]}
]

# Add Data to Firestore
for meal in meal_plans:
    db.collection("meal_plans").add(meal)

for workout in workout_plans:
    db.collection("workouts").add(workout)

print("Data successfully added to Firebase!")
