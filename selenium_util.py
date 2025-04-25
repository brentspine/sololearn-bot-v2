import selenium.webdriver as webdriver
import random
import time
import json

def get_random_url():
    LOCALS = ["en", "es", "fr", "de", "it", "pt", "ru", "tr"]
    COURSES = ["genai-in-practice", "python-introduction", "java-introduction", "c-introduction", "c-sharp-introduction", "sql-introduction", "html-introduction", "css-introduction", "java-introduction", "javascript-introduction", "c-sharp-introduction", "php-introduction", "c-plus-plus-introduction", "tech-for-everyone", "python-intermediate", "java-intermediate", "c-intermediate", "c-sharp-intermediate", "sql-intermediate", "html-intermediate", "css-intermediate", "java-intermediate", "javascript-intermediate", "c-sharp-intermediate", "php-intermediate", "c-plus-plus-intermediate", "coding-foundations", "angular", "python-developer", "web-development", "data-programming", "angular-developer", "data-ai", "data-fundamentals", "gen-ai-safety", "ai-writing", "ab-testing", "ai-prompting", "presenting-data", "llms-ai", "ml-fundamentals", "brainstorm-ai", "creativity-ai", "planning-ai", "research-ai", "sm-ai", "seo-ai"]
    LANGS = ["python", "java", "html", "javascript", "cpp", "csharp", "css", "typescript", "kotlin", "swift", "php", "c", "nodejs", "go", "r", "ruby", "jquery", "web"]
    URLS = {
        "https://www.sololearn.com/%%local%%/learn": 8,
        "https://www.sololearn.com/%%local%%/learn/courses/%%course%%": 20,
        "https://www.sololearn.com/%%local%%/compiler-playground": 3,
        "https://www.sololearn.com/%%local%%/compiler-playground/%%lang%%": 10,
        "https://www.sololearn.com/%%local%%/contact": 1,
        "https://www.sololearn.com/%%local%%/leaderboard-league": 2,
        "https://www.sololearn.com/%%local%%/codes": 8,
        "https://www.sololearn.com/%%local%%/codes?language=%%lang%%&page=%%randomsmall%%": 5,
        "https://www.sololearn.com/%%local%%/discuss": 3,
        "https://www.sololearn.com/blog": 4,
        "https://www.sololearn.com/%%local%%/user/%%randomuser%%": 3,
        "https://www.sololearn.com/%%local%%/user/%%someshit%%": 3,
    }
    # Select a URL based on weights
    urls = list(URLS.keys())
    weights = list(URLS.values())
    selected_url = random.choices(urls, weights=weights, k=1)[0]
    
    # Replace variables in the URL
    if "%%local%%" in selected_url:
        selected_url = selected_url.replace("%%local%%", random.choice(LOCALS))
    
    if "%%course%%" in selected_url:
        selected_url = selected_url.replace("%%course%%", random.choice(COURSES))
    
    if "%%lang%%" in selected_url:
        selected_url = selected_url.replace("%%lang%%", random.choice(LANGS))
    
    if "%%randomsmall%%" in selected_url:
        selected_url = selected_url.replace("%%randomsmall%%", str(random.randint(1, 25)))

    if "%%randomuser%%" in selected_url:
        selected_url = selected_url.replace("%%randomuser%%", str(random.randint(1, 20_000_000)))
    
    return selected_url

def find_public_token():
    # Create selenium window, try simulating headfull
    driver = webdriver.Chrome()
    driver.get(get_random_url())
    
    # Set timeout and start timer
    timeout = 30
    start_time = time.time()
    access_token = None
    refresh_token = None
    
    # Loop until tokens found or timeout reached
    while time.time() - start_time < timeout:
        # Find the tokens in localStorage
        access_token = driver.execute_script("return localStorage.getItem('accessToken');")
        refresh_token = driver.execute_script("return localStorage.getItem('refreshToken');")
        
        # If both tokens found, break the loop
        if access_token and refresh_token:
            break
            
        # Wait a short time before checking again
        time.sleep(0.5)
    
    # Parse tokens if they exist
    if access_token:
        try:
            parsed_token = json.loads(access_token)
            access_token = parsed_token.get('data')
        except json.JSONDecodeError:
            print("Error parsing access token JSON")
    
    if refresh_token:
        try:
            parsed_token = json.loads(refresh_token)
            refresh_token = parsed_token.get('data')
        except json.JSONDecodeError:
            print("Error parsing refresh token JSON")
    
    # Close the browser
    driver.quit()
    
    if access_token is None or refresh_token is None:
        print("Error: Could not find access token or refresh token within timeout period.")
        return None
    
    return access_token, refresh_token