import user
import json
import user_generation
import random
import time
import selenium_util
import xp_util
from dotenv import load_dotenv
import os

load_dotenv()
ACCOUNT_PASSWORD = os.getenv("ACCOUNT_PASSWORD")

def load_tokens(filename='users.json'):
    """Load tokens from a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    
def save_tokens(tokens, filename='users.json'):
    """Save tokens to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(tokens, file, indent=4)

def add_user_to_file(user, filename='users.json'):
    """Add a user to the JSON file."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.get("users", []).append(user.to_json())

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"User {user.username} added to {filename}.")

def update_token_in_file(original_token, access_token, refresh_token, filename='users.json'):
    # Find the original token in the json under "tokens[x].access_token"
    # and replace it with the new token
    tokens = load_tokens(filename)
    if tokens is None:
        return
    found = False
    i = 1
    for token in tokens["tokens"]:
        if token["access_token"] == original_token:
            token["access_token"] = access_token
            token["refresh_token"] = refresh_token
            token["updated_at"] = time.time()
            found = True
            break
        i += 1
    if not found:
        print(f"Token {original_token} not found in {filename}.")
        return
    print(f"Token {i} updated in {filename}.")
    save_tokens(tokens, filename)

def add_token_to_file(access_token, refresh_token, filename='users.json'):
    """Add a token to the JSON file."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"tokens": []}

    # Check if the token already exists in the file
    for token in data["tokens"]:
        if token["access_token"] == access_token:
            print(f"Token {access_token} already exists in {filename}.")
            return

    # Add new token to the list
    new_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "updated_at": time.time()
    }
    data["tokens"].append(new_token)

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Token {access_token} added to {filename}.")

def main():
    skip_token = 0
    last_run = 0
    while True:
        if time.time() - last_run > 900:
            token_data = load_tokens()
            last_run = time.time()
            i = 0
            for token in token_data["tokens"]:
                i += 1
                if skip_token > 0:
                    skip_token -= 1
                    continue
                print("")
                print(f"Token {i}")
                authorization_token = check_token_refresh(token)
                if register_update_and_follow(authorization_token):
                    register_update_and_follow(authorization_token)
                #time.sleep(20)
        token_data = selenium_find_public_token()
        if token_data is not None:
            access_token, refresh_token = token_data
            # authorization_token = check_token_refresh(access_token)
            if register_update_and_follow(access_token):
                register_update_and_follow(access_token)


def selenium_find_public_token():
    token_data = selenium_util.find_public_token()
    if token_data is not None:
        access_token, refresh_token = token_data
        add_token_to_file(access_token, refresh_token)
        return token_data
    return None


def check_token_refresh(token):
    do_refresh = (token["updated_at"] + 3600 - 60 < time.time())
    # do_refresh = True

    if do_refresh:
        print("Trying to refresh token")
        new_token = user.refresh_token(token["refresh_token"])
        if new_token is None:
            time.sleep(10)
            return
        authorization_token = new_token["accessToken"]
        refresh_token = new_token["refreshToken"]
        update_token_in_file(token["access_token"], authorization_token, refresh_token)
    else:
        authorization_token = token["access_token"]
    return authorization_token

def register_update_and_follow(authorization_token):
    print("Getting persona")
    persona = user_generation.get_user()

    if persona is None:
        print("Error fetching user data.")
        return False
    if random.randint(0, 1) == 0:
        username = persona["mail_without_provider"].replace(".", " ")
    else:
        username = persona["first_name"].title() + " " + persona["last_name"].title() 
    print("Username: ", username)
    mail = persona["mail"]
    print("Trying to register user")
    user_data = user.register_user(username, mail, ACCOUNT_PASSWORD, authorization_token)
    if user_data is None:
        # print(f"Error registering user: {response.status_code}")
        return False
    print(f"Registered {username}: ID({user_data["user"]["id"]})")

    user.update_profile_picture(user_data["accessToken"], "https://"+persona["profile_picture_url"])
    
    # Follow user
    target_id = "33777091"

    user.follow(user_data["accessToken"], target_id)

    # Add user to file
    new_user = user.User(
        access_token=user_data["accessToken"],
        refresh_token=user_data["refreshToken"],
        id=user_data["user"]["id"],
        username=username,
        email=mail,
        profile_picture_url=persona["profile_picture_url"]
    )
    add_user_to_file(new_user)

    # Submit answers
    #xp_util.run(user_data["accessToken"])

    return True

if __name__ == "__main__":
    main()