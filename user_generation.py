import requests
import json
import random
import os
from dotenv import load_dotenv
load_dotenv()

FAKE_PERSONA_URL = os.getenv("FAKE_PERSONA_URL")
# FAKE_PERSONA_URL = "https://17b1-95-223-231-187.ngrok-free.app/fake_persona/get.php"

def get_user():
    """Fetch a random user from the fake persona API."""
    try:
        response = requests.get(FAKE_PERSONA_URL)
        user_data = response.json()
        if user_data.get("errors", []) != []:
            print("Warning, error in fake persona: ", user_data["errors"])
        return user_data
    except requests.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None
