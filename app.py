# app.py
import re
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from auth import AuthManager
from itinerary_generator import generate_itinerary
from booking import search_flights, search_hotels
from budget import estimate_budget
from openai_integration import ai_planner  # Import from the renamed module with correct variable

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "itinify-secret-key"  # For session management

# Initialize the AuthManager for user auth and data storage
auth_manager = AuthManager()

# Track user chat sessions
user_sessions = {}

# Email validation helper
def is_valid_email(email):
    """Check if the provided string is a valid email address."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

# Get or create a unique session ID for a user
def get_user_session_id(email):
    if email not in user_sessions:
        user_sessions[email] = str(uuid.uuid4())
    return user_sessions[email]

# Flask routes
@app.route('/')
def index():
    """Render the login page or redirect to dashboard if logged in."""
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validate inputs
    if not email or not password:
        return render_template('login.html', login_error="Email and password are required.")
    
    if not is_valid_email(email):
        return render_template('login.html', login_error="Please enter a valid email address.")
    
    # Authenticate
    success, msg = auth_manager.authenticate(email, password)
    if success:
        session['email'] = email
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', login_error=msg)

@app.route('/register', methods=['POST'])
def register():
    """Handle registration form submission."""
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate inputs
    if not email or not password or not confirm_password:
        return render_template('login.html', register_error="All fields are required.")
    
    if not is_valid_email(email):
        return render_template('login.html', register_error="Please enter a valid email address.")
    
    if password != confirm_password:
        return render_template('login.html', register_error="Passwords do not match.")
    
    # Register new user
    success, msg = auth_manager.register(email, password)
    if success:
        return render_template('login.html', register_success=msg)
    else:
        return render_template('login.html', register_error=msg)

@app.route('/dashboard')
def dashboard():
    """Render the dashboard with embedded chat interface."""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    # Pass the user's email to the template
    return render_template('dashboard.html', email=session['email'])

@app.route('/logout')
def logout():
    """Log out the user and redirect to login page."""
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/save_itinerary', methods=['POST'])
def save_itinerary():
    """API endpoint to save an itinerary."""
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    if not data or 'itinerary' not in data:
        return jsonify({"success": False, "message": "No itinerary provided"}), 400
    
    success, msg = auth_manager.save_itinerary(session['email'], data['itinerary'])
    return jsonify({"success": success, "message": msg})

@app.route('/get_itineraries')
def get_itineraries():
    """API endpoint to get user's saved itineraries."""
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    itineraries = auth_manager.get_itineraries(session['email'])
    return jsonify({"success": True, "itineraries": itineraries})

@app.route('/delete_itinerary', methods=['POST'])
def delete_itinerary():
    """API endpoint to delete a saved itinerary."""
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    if not data or 'index' not in data:
        return jsonify({"success": False, "message": "No itinerary index provided"}), 400
    
    try:
        index = int(data['index'])
        success, msg = auth_manager.delete_itinerary(session['email'], index)
        return jsonify({"success": success, "message": msg})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid itinerary index"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions to generate travel itineraries using OpenAI."""
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "message": "No message provided"}), 400
        
        user_msg = data['message'].strip()
        if not user_msg:
            return jsonify({"success": False, "message": "Empty message"}), 400
        
        # Get user preferences if provided
        days = int(data.get('days', 5))
        preferences = data.get('preferences', [])
        
        # Get or create a session ID for this user
        user_id = get_user_session_id(session['email'])
        
        # Determine if this is a follow-up or a new conversation
        is_followup = data.get('is_followup', False)
        
        # Print for debugging
        print(f"Processing chat message: {user_msg}, days: {days}, preferences: {preferences}, is_followup: {is_followup}")
        
        try:
            # First try to generate response using OpenAI
            if "?" in user_msg or is_followup:
                # Follow-up question logic
                destination = None
                for word in user_msg.split():
                    if word.istitle() and len(word) > 3 and word.lower() not in ['what', 'where', 'when', 'how', 'tell', 'about']:
                        destination = word
                        break
                
                if not destination and 'last_destination' in session:
                    destination = session.get('last_destination')
                elif not destination:
                    destination = "the destination"
                
                response = ai_planner.generate_travel_plan(
                    user_id=user_id,
                    destination=destination,
                    days=days,
                    preferences=preferences,
                    new_message=user_msg
                )
            else:
                # New destination query
                destination = user_msg
                session['last_destination'] = destination
                
                response = ai_planner.generate_travel_plan(
                    user_id=user_id,
                    destination=destination,
                    days=days,
                    preferences=preferences
                )
                
                # Check if the response is asking a clarification question
                # This is a simple heuristic - we check if it contains a question mark and is relatively short
                # or explicitly contains phrases indicating a clarification
                is_clarification = ("?" in response and len(response) < 500) or any(phrase in response.lower() for phrase in [
                    "could you clarify", 
                    "can you provide more details",
                    "need more information",
                    "can you specify",
                    "would you mind telling me",
                    "would help to know"
                ])
                
                if is_clarification:
                    # If it's a clarification question, we'll set a flag to indicate this
                    # so the frontend can handle it appropriately
                    return jsonify({
                        "success": True,
                        "response": response,
                        "is_clarification": True,
                        "destination": destination,
                        "streaming": False
                    })
        except Exception as e:
            # If OpenAI API fails, fall back to local itinerary generator
            print(f"OpenAI API error: {str(e)}. Falling back to local generator.")
            
            if "?" in user_msg or is_followup:
                # For follow-up questions, extract destination if possible
                destination = None
                for word in user_msg.split():
                    if word.istitle() and len(word) > 3 and word.lower() not in ['what', 'where', 'when', 'how', 'tell', 'about']:
                        destination = word
                        break
                
                if not destination and 'last_destination' in session:
                    destination = session.get('last_destination')
                elif not destination:
                    destination = "Generic Destination"
                
                # Generate basic response for follow-up
                if "restaurant" in user_msg.lower() or "food" in user_msg.lower() or "eat" in user_msg.lower():
                    response = f"Restaurant Recommendations for {destination}\n\nHere are some excellent dining options in {destination}:\n\n"
                    response += "1. **Local Traditional Restaurant** - Authentic cuisine with moderate prices\n"
                    response += "2. **Waterfront Dining** - Seafood with amazing views\n"
                    response += "3. **Street Food Market** - Various local vendors with budget-friendly options\n"
                    response += "4. **Garden Terrace** - Farm-to-table concept with vegetarian options\n\n"
                    response += "These range from budget-friendly street food to upscale dining experiences."
                elif "hotel" in user_msg.lower() or "stay" in user_msg.lower() or "accommodation" in user_msg.lower():
                    response = f"Accommodation Options in {destination}\n\n"
                    response += "Luxury Options\n- **Grand Resort** - Full amenities and central location\n- **Beachfront Villa** - Private and exclusive\n\n"
                    response += "Mid-range Options\n- **Boutique Hotel** - Great location, comfortable rooms\n- **City Suites** - Modern amenities\n\n"
                    response += "Budget Options\n- **Backpacker's Hostel** - Social atmosphere and affordable\n- **Local Guesthouse** - Authentic experience\n\n"
                else:
                    # Use the itinerary generator for general questions
                    response = generate_itinerary(destination, days, preferences)
            else:
                # For new destination queries, use the itinerary generator
                destination = user_msg
                session['last_destination'] = destination
                response = generate_itinerary(destination, days, preferences)
        
        # Calculate a placeholder budget
        base_budget = days * 100  # Base daily rate
        budget = base_budget * (1 + 0.1 * len(preferences))  # Add 10% per preference
        
        # Extract budget from the response if it contains one
        response_budget = budget
        if "Budget" in response and "$" in response:
            try:
                # Very simple budget extraction
                budget_section = response.split("Budget")[1]
                total_line = [line for line in budget_section.split('\n') if "Total" in line][0]
                budget_str = total_line.split("$")[-1].split()[0].replace(',', '')
                response_budget = float(budget_str)
            except:
                response_budget = budget
        
        return jsonify({
            "success": True, 
            "response": response,
            "budget": response_budget,
            "destination": destination,
            "streaming": False,  # Indicate this is not a streaming response
            "is_clarification": False  # Default is not a clarification question
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": f"Error generating itinerary: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 