import requests
import json
from typing import Dict, List, Any, Union

class SoloLearnXPUtil:
    BASE_URL = "https://api2.sololearn.com/v2/learnEngine/api/learn/solve"
    
    def __init__(self, auth_token: str, locale: str = "de", plan_id: str = "2", time_zone: str = "+2"):
        """Initialize the SoloLearn client with authentication and configuration"""
        self.auth_token = auth_token
        self.locale = locale
        self.plan_id = plan_id
        self.time_zone = time_zone
        
    def get_headers(self, exp_alias: str = None, exp_type: str = None, put_session_id: bool = False) -> Dict[str, str]:
        """Generate request headers with authentication token
        
        Args:
            exp_alias: Optional experience alias to include in headers
            exp_type: Optional experience type to include in headers
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en;q=0.8",
            "authorization": f"Bearer {self.auth_token}",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Brave\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "sl-api-version": "2.0",
            "sl-locale": self.locale,
            "sl-plan-id": self.plan_id,
            "sl-time-zone": self.time_zone
        }
        
        # Only add experience-specific headers if provided
        if exp_alias:
            headers["le-exp-alias"] = exp_alias
        if exp_type:
            headers["le-exp-type"] = exp_type

        headers["User-Agent"] = self.get_user_agent()
        if put_session_id:
            if not hasattr(self, "session_id"):
                raise ValueError("Session ID not set. Cannot add to headers.")
            if self.session_id is None:
                raise ValueError("Session ID is None. Cannot add to headers.")
            headers["sl-le-session"] = self.session_id

        # print(headers)
            
        return headers
    
    def enroll(self, course_alias: str, location_type_id: int = 3) -> bool:
        """Enroll in a SoloLearn course
        
        Args:
            course_alias: The course alias (e.g., "python-introduction")
            location_type_id: Location type ID (default: 3)
            
        Returns:
            Dict containing the response data or empty dict on error
        """
        ENROLL_URL = "https://api2.sololearn.com/v2/learnEngine/api/learn/enroll"
        
        payload = {
            "alias": course_alias,
            "locationTypeId": location_type_id
        }
        
        response = requests.post(
            ENROLL_URL,
            headers=self.get_headers(),  # No exp_alias needed for enrollment
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Error enrolling in course: {response.status_code}, {response.text}")
            return False
        
        return True
    
    def get_user_agent(self) -> str:
        """Return a standard user agent string for requests"""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    
    def submit_answer(self, 
                     material_relation_id: int,
                     selected_options: List[Dict[str, Any]],
                     exp_type_id: int = 1,
                     type_id: int = 2,
                     answer_type_id: int = 6,
                     course_alias = "") -> Dict:
        """Submit a single answer to SoloLearn"""
        
        payload = {
            "solutions": [
                {
                    "typeId": type_id,
                    "materialRelationId": material_relation_id,
                }
            ],
            "experience_type_id": exp_type_id
        }
        if selected_options != [] and len(selected_options) > 0:
            payload["solutions"][0]["answer"] = {
                "answerTypeId": answer_type_id,
                "selectedOptions": selected_options
            }
        
        headers = self.get_headers(exp_alias=course_alias, exp_type="lesson", put_session_id=True)
        headers["User-Agent"] = self.get_user_agent()
        
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Error submitting answer: {response.status_code}, {response.text}, {payload}")
            return {}

        return response.json()
    
    def submit_multiple_answers(self, answers_config: List[Dict], course_alias) -> List[Dict]:
        """Submit multiple answers based on a configuration list"""
        results = []
        
        for config in answers_config:
            result = self.submit_answer(
                material_relation_id=config["material_relation_id"],
                selected_options=config["selected_options"],
                course_alias=course_alias
            )
            results.append(result)
            
        return results
        
    def get_course_structure(self, course_id) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        COURSE_URL = "https://api2.sololearn.com/v2/learnEngine/api/learn/coursesubtree"
        response = requests.get(
            COURSE_URL+f"?alias={course_id}",
            headers=self.get_headers()
        )
        if response.status_code != 200:
            print(f"Error fetching course structure: {response.status_code}, {response.text}")
            return {}
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            print(f"Response text: {response.text}")
            return []
        sections = data["children"]
        lessons = []
        for section in sections:
            lessons.extend(section["children"])
        return lessons

    def get_questions_for_lesson(self, material_relation_id: int, course_alias = "") -> List[Dict[str, Any]]:
        LESSON_URL = f"https://api2.sololearn.com/v2/learnEngine/api/learn/lessonsubtree?materialRelationId={material_relation_id}"
        
        # Create headers with correct parameters
        headers = self.get_headers(exp_alias=course_alias, exp_type="1")
        # Update API version to match the fetch request
        headers["sl-api-version"] = "3.0"
        
        response = requests.get(
            LESSON_URL,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error fetching lesson questions: {response.status_code}, {response.text}")
            return []
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            print(f"Response text: {response.text}")
            return []
        
        self.session_id = data["session"]

        print("Session ID: ", self.session_id)

        if "tree" in data:
            data = data["tree"]
        
        questions = data["children"] if "children" in data else []
        r = []
        for question in questions:
            if not "children" in question:
                print("Couldn't find children in question")
                continue
                
            for child in question["children"]:
                r.append(child["materialInfo"])
        
        return r
            

def create_option(id: int, text: str, order_number: int, status: str = "selected") -> Dict[str, Any]:
    """Helper function to create an option object"""
    return {
        "id": id,
        "text": text,
        "data": {},
        "orderNumber": order_number,
        "status": status
    }
    

def run(authorization_token: str):
    print("Running SoloLearn XP Util...")
    answers_config = [
        ["<"],
        [">"],
        ["button ", ">"],
        [">"],
        ["<button>", "<img>", "<p>", "<table>"],
        ["HTML ", "CSS  ", "JavaScript"],
        ["<", "button", ">"]
    ]

    course = "html-introduction"
    client = SoloLearnXPUtil(auth_token=authorization_token)
    client.enroll(course_alias=course)
    structure = client.get_course_structure(course_id=course)
    # print(structure)
    questions = client.get_questions_for_lesson(structure[0]["materialInfo"]["header"]["materialRelationId"], course_alias=course)
    #print(questions)

    rconfigs = []
    i = 0
    questionCounter = 0
    while i < len(answers_config):
        if "answer" in questions[questionCounter]:
            if questionCounter >= len(questions):
                break
            rconfigs.append(get_relation_config_for_question(questions[questionCounter], answer=answers_config[i]))
            i += 1
        else:
            rconfigs.append(get_relation_config_for_question(questions[questionCounter], answer=None))
        questionCounter += 1
    print("\n\n")
    print(rconfigs)
    # Submit all answers
    results = client.submit_multiple_answers(rconfigs, course_alias=course)
    print(f"Submitted {len(results)} answers successfully")
    for r in results:
        print(r)
    
def get_relation_config_for_question(question, answer):
    materialRelationId = question["header"]["materialRelationId"]
    if "answer" not in question:
        print("No answer in question")
        return {
            "material_relation_id": materialRelationId,
            "selected_options": []
        }
    selected_options = []
    option_dict = {}
    for option in question["answer"]["options"]:
        option_dict[option["text"]] = option["id"]
    i = 1
    for option in answer:
        selected_options.append(create_option(option_dict[option], option, i))
        i += 1
    print("Selected options: ", selected_options)
    return {
        "material_relation_id": materialRelationId,
        "selected_options": selected_options
    }