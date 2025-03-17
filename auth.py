# auth.py
import json, os, hashlib
import re

DB_FILE = "users_db.json"


class AuthManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        # If database file doesn't exist, create an empty JSON file
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({}, f)

    def _load_db(self):
        """Load user database from the JSON file."""
        with open(self.db_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        return data

    def _save_db(self, data):
        """Save the entire database dictionary back to the JSON file."""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def _is_valid_email(self, email):
        """Check if the provided string is a valid email address."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def register(self, email, password):
        """Register a new user with a hashed password."""
        # Validate email format
        if not self._is_valid_email(email):
            return False, "Please enter a valid email address."
            
        data = self._load_db()
        if email in data:
            return False, "This email address is already registered."
        # Hash the password for storage
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        data[email] = {"password": hashed_pw, "itineraries": []}
        self._save_db(data)
        return True, "Account created successfully."

    def authenticate(self, email, password):
        """Verify email and password. Returns (True, msg) if valid, else (False, msg)."""
        # Special case for test user (for development purposes)
        if email == "test" and password == "123":
            return True, "Authentication successful."
            
        # Validate email format for regular users
        if not self._is_valid_email(email):
            return False, "Please enter a valid email address."
            
        data = self._load_db()
        if email not in data:
            return False, "No account found with this email address."
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if data[email]["password"] == hashed_pw:
            return True, "Authentication successful."
        else:
            return False, "Incorrect password."

    def save_itinerary(self, email, itinerary_text):
        """Save a new itinerary (text) under the given user's account."""
        # Special case for test user
        if email == "test":
            return True, "Itinerary saved."
            
        data = self._load_db()
        if email not in data:
            return False, "User not found."
        # Append the itinerary text to the user's list of itineraries
        data[email]["itineraries"].append(itinerary_text)
        self._save_db(data)
        return True, "Itinerary saved."

    def get_itineraries(self, email):
        """Retrieve all itineraries saved by the user."""
        # Special case for test user
        if email == "test":
            return []
            
        data = self._load_db()
        if email in data:
            return data[email].get("itineraries", [])
        return []

    def delete_itinerary(self, email, index):
        """Delete an itinerary at the specified index from the user's account."""
        # Special case for test user
        if email == "test":
            return True, "Itinerary deleted."
            
        data = self._load_db()
        if email not in data:
            return False, "User not found."
            
        itineraries = data[email].get("itineraries", [])
        if not 0 <= index < len(itineraries):
            return False, "Itinerary not found."
            
        # Remove the itinerary at the specified index
        del itineraries[index]
        data[email]["itineraries"] = itineraries
        self._save_db(data)
        return True, "Itinerary deleted."
