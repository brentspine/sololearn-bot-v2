import requests
import json
import os
import time

class User:
    def __init__(self, username=None, email=None, access_token=None, refresh_token=None, id=None, profile_picture_url=None):
        self.username = username
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id = id
        self.profile_picture_url = profile_picture_url
        self.updated_at = time.time() - 15
    
    def set_tokens(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
    
    def update_user_info(self, username=None, email=None):
        if username:
            self.username = username
        if email:
            self.email = email
    
    def is_authenticated(self):
        return self.access_token is not None
    
    def to_json(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "updated_at": self.updated_at,
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_picture_url": self.profile_picture_url
        }
    
    def __str__(self):
        return f"User: {self.username}, Email: {self.email}"

profile_picture_timeout = 0

def get_headers(authorization_token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.7",
        "authorization": f"Bearer {authorization_token}",
        "content-type": "application/json",
        "sl-locale": "de",
        "sl-plan-id": "",
        "sl-time-zone": "+2"
    }
    return headers

def register_user(username, email, password, authorization_token):
    headers = get_headers(authorization_token)
    
    # Make sure username is not None or empty
    if not username or not username.strip():
        print("Error: Username cannot be empty")
        return None
        
    data = {
        "email": email,
        "password": password,
        "name": username.strip(),  # Ensure name is properly formatted
        "subject": "0b62bccd8590cd91486567da8deb6de5"  # This appears to be a static value
    }
    
    response = requests.post(
        "https://api2.sololearn.com/v2/authentication/user",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        print(f"Error registering user: {response.status_code}, {response.text}, {data}")
        return None
    
    return response.json()

def follow(authorization_token, target_id, output=True):
    headers = get_headers(authorization_token)
    response = requests.post(
        f"https://api2.sololearn.com/v2/userinfo/v3/profile/follow/{target_id}",
        headers=headers,
        json={}
    )
    if output:
        print(f"Following {target_id}: {response.status_code}")
    return response.json()

def update_profile_picture(authorization_token, image_url):
    global profile_picture_timeout
    if profile_picture_timeout > time.time():
        print("Profile picture update is on cooldown")
        return None
    headers = get_headers(authorization_token)
    
    # Download the image from the URL
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        print(f"Error downloading image: {image_response.status_code}")
        return {"error": "Failed to download image"}
    
    image_data = image_response.content

    # Set up multipart form boundary
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
    headers["content-type"] = f"multipart/form-data; boundary={boundary}"

    # Remove the authorization part as it's already in headers
    if "authorization" in headers:
        headers["authorization"] = f"Bearer {authorization_token}"

    # Build the multipart form data
    form_data = f"--{boundary}\r\n"
    form_data += 'Content-Disposition: form-data; name="file"; filename="newProfileAvatar"\r\n'
    form_data += 'Content-Type: image/png\r\n\r\n'

    # Combine the form data with the binary image data and closing boundary
    payload = form_data.encode('utf-8') + image_data + f"\r\n--{boundary}--\r\n".encode('utf-8')

    # Send the request
    response = requests.post(
        "https://api2.sololearn.com/v2/userinfo/v3/profile/uploadavatar",
        headers=headers,
        data=payload
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
    
    try:
        r = response.json()
        print("Profile picture updated")
    except json.JSONDecodeError:
        r = {"error": "Failed to parse JSON response"}
        profile_picture_timeout = time.time() + 60 * 5  # Set cooldown to 5 minutes
        print("CloudFlare error setting profile picture, retrying in 5 minutes")

    return r


def refresh_token(refresh_token):
    """
    Refresh an access token using the refresh token
    
    Args:
        refresh_token (str): The refresh token to use
        
    Returns:
        dict: The response from the token refresh API
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en;q=0.7",
        "content-type": "application/json",
        "priority": "u=1, i"
    }
    
    response = requests.post(
        "https://api2.sololearn.com/v2/authentication/token:refresh",
        headers=headers,
        json=refresh_token  # The refresh token is sent as the raw JSON body
    )
    
    if response.status_code != 200:
        print(f"Error refreshing token: {response.status_code}, {response.text}")
        return None
    
    r = response.json()
    print(r)
    return r
    
    