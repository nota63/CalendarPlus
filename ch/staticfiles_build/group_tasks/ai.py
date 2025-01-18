import os
from dotenv import load_dotenv
import requests
# Load environment variables from the .env file
load_dotenv()

# Fetch the API key from the environment
api_key = os.getenv('GEMINI_API_KEY')



# Gemini API endpoint
GEMINI_API_URL = "https://gemini.googleapis.com/v1/query"

# Function to ask a question to Gemini AI
def ask_ai(question):
    if not api_key:
        print("API Key is missing. Please check your .env file.")
        return

    # Send request to the API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "question": question,  # The task-related query or anything you want to ask
        "context": "task details: title, description, etc.",  # Add the task context here if necessary
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            print("AI Response:", response.json())  # Print the AI response
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")

# Test the function with a task-related query
ask_ai("What is the current progress of the task?")
