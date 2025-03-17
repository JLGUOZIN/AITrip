"""
OpenAI Integration for AI Trip Planner
This module handles the integration with OpenAI API for travel planning.
"""
import os
import json
import logging
import time
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('openai_integration')

# Load environment variables from .env file
load_dotenv()

# Configuration for OpenAI API
API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")  # Fastest GPT-4 option
MAX_TOKENS = 1024  # Limiting max tokens to get faster responses

# Validate API key exists
if not API_KEY:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it to use OpenAI API.")
else:
    # Mask API key for logging (show only first and last 4 characters)
    masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "****"
    logger.info(f"OpenAI API configured with key: {masked_key}")
    logger.info(f"Using model: {MODEL_NAME}")

class OpenAITravelPlanner:
    def __init__(self):
        self.chat_histories = {}  # Store chat histories by user_id
        self.client = OpenAI(api_key=API_KEY)
        self.response_cache = {}  # Cache for common destinations
        logger.info("OpenAITravelPlanner initialized")
    
    def _get_chat_history(self, user_id):
        """Get chat history for a specific user"""
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = []
            logger.debug(f"Created new chat history for user_id: {user_id}")
        return self.chat_histories[user_id]
    
    def _build_prompt(self, destination, days, preferences, chat_history=None):
        """Build a detailed prompt for OpenAI based on user inputs and history"""
        # Start with a system prompt that guides the AI's behavior
        system_prompt = """You are an expert travel planner with deep knowledge of destinations worldwide. 
Format your responses in a visually appealing way using HTML tables for better readability:

1. Use <table>, <tr>, <th>, <td> tags to structure itineraries and information
2. For daily itineraries, create tables with columns for Time/Period, Activity, and Description
3. For budget information, use a table with Item and Cost columns
4. Use light styling to improve readability (e.g., <table style="width:100%; border-collapse: collapse">)
5. Add simple CSS styling for better appearance (e.g., alternating row colors)

If you need more information to create a high-quality itinerary, politely ask 1-2 specific questions first.
Keep your overall responses concise and well-structured.
For trips shorter than the requested duration, explain why and offer alternatives."""
        
        # Build user query
        user_query = f"I want a {days}-day trip to {destination}."
        
        if preferences:
            preference_text = ", ".join(preferences)
            user_query += f" I'm interested in {preference_text}."
        
        # Format messages for the API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if available
        if chat_history:
            messages.extend(chat_history)
        
        # Add the current query
        messages.append({"role": "user", "content": user_query})
        
        logger.debug(f"Built prompt for destination: {destination}, days: {days}, preferences: {preferences}")
        return messages
    
    def generate_travel_plan(self, user_id, destination, days, preferences, new_message=None):
        """Generate a travel plan using OpenAI API"""
        logger.info(f"Generating travel plan for user_id: {user_id}, destination: {destination}, days: {days}")
        if preferences:
            logger.info(f"Preferences: {preferences}")
        if new_message:
            logger.info(f"Follow-up message: {new_message}")
        
        # Check cache for common destinations (only for new queries, not follow-ups)
        cache_key = f"{destination.lower()}_{days}_{'-'.join(sorted(preferences))}"
        if not new_message and cache_key in self.response_cache:
            logger.info(f"Using cached response for {destination}")
            return self.response_cache[cache_key]
        
        # Get existing chat history
        chat_history = self._get_chat_history(user_id)
        
        # If there's a new message and we have history, add it to continue the conversation
        if new_message and chat_history:
            chat_history.append({"role": "user", "content": new_message})
            messages = [{"role": "system", "content": "You are an expert travel planner."}]
            messages.extend(chat_history)
            logger.debug(f"Added follow-up message to chat history for user_id: {user_id}")
        else:
            # Starting a new conversation
            messages = self._build_prompt(destination, days, preferences)
            logger.debug(f"Started new conversation for user_id: {user_id}")
        
        # Try the API call with retries
        max_retries = 2
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                # Call OpenAI API with the prepared messages
                logger.info(f"Calling OpenAI API for user_id: {user_id}" + (f" (attempt {attempt+1}/{max_retries+1})" if attempt > 0 else ""))
                response = self._call_openai_api(messages)
                
                # Add response to chat history
                chat_history.append({"role": "user", "content": new_message or f"Plan a trip to {destination}"})
                chat_history.append({"role": "assistant", "content": response})
                
                # Update the stored chat history
                self.chat_histories[user_id] = chat_history
                logger.debug(f"Updated chat history for user_id: {user_id}")
                
                # Cache the response for future use (only for new queries, not follow-ups)
                if not new_message:
                    self.response_cache[cache_key] = response
                    logger.debug(f"Cached response for {destination}")
                
                return response
                
            except Exception as e:
                logger.error(f"Error generating travel plan (attempt {attempt+1}/{max_retries+1}): {str(e)}", exc_info=True)
                
                if attempt < max_retries:
                    # Use exponential backoff
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    # All retries failed, return a fallback response
                    logger.info(f"All API attempts failed, using fallback response")
                    return self.get_fallback_response(destination, days, preferences)
    
    def _call_openai_api(self, messages):
        """Call the OpenAI API using the official client library"""
        try:
            logger.info(f"Calling OpenAI API with model {MODEL_NAME}")
            
            # Log request data (excluding sensitive information)
            logger.debug(f"Sending {len(messages)} messages to OpenAI")
            
            # Using the official OpenAI client library
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=MAX_TOKENS,
                stream=False,  # We'll implement streaming in the Flask endpoint
                presence_penalty=0.2,  # Add slight presence penalty for more concise responses
                frequency_penalty=0.2   # Add slight frequency penalty for more concise responses
            )
            
            # Extract content from the response
            content = response.choices[0].message.content
            
            # Improve formatting for better UX - replace markdown headers with more user-friendly formatting
            content = content.replace("### ", "")
            content = content.replace("## ", "")
            content = content.replace("# ", "")
            
            # Format the budget section to be more user-friendly if it's not already in a table
            if ("Budget Estimate" in content or "Total Estimated Budget" in content) and "<table" not in content:
                content = self._format_budget_section(content)
            
            logger.info(f"OpenAI API response successful")
            # Log a portion of the response for debugging
            preview = content[:100] + "..." if len(content) > 100 else content
            logger.debug(f"Response preview: {preview}")
            
            return content
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
            raise
    
    def _format_budget_section(self, content):
        """Format the budget section to be more user-friendly"""
        # Only process if we definitely have a budget section to avoid unnecessary processing
        if "Budget" not in content:
            return content
            
        lines = content.split('\n')
        formatted_lines = []
        
        in_budget_section = False
        for line in lines:
            # Check if we're entering a budget section
            if "Budget Estimate" in line or "Total Estimated Budget" in line or "Budget" in line and ":" not in line:
                in_budget_section = True
                formatted_lines.append("Budget Estimate:")
                continue
            
            # Format budget lines to be more user-friendly
            if in_budget_section:
                # Remove bullet points and other markdown formatting
                line = line.replace("- ", "")
                line = line.replace("* ", "")
                
                # Add emoji for budget items (only if we don't already have an emoji)
                if not any(emoji in line for emoji in ['🏨', '🍽️', '🚌', '🎭', '💰']):
                    if "accommodation" in line.lower() or "hotel" in line.lower():
                        line = "🏨 " + line
                    elif "food" in line.lower() or "meal" in line.lower() or "dining" in line.lower():
                        line = "🍽️ " + line
                    elif "transport" in line.lower() or "transit" in line.lower():
                        line = "🚌 " + line
                    elif "activit" in line.lower() or "attraction" in line.lower() or "sight" in line.lower():
                        line = "🎭 " + line
                    elif "total" in line.lower():
                        line = "💰 " + line
                
                # Skip empty lines in budget section
                if line.strip():
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def get_fallback_response(self, destination, days, preferences):
        """Generate a fallback response when the API is unavailable"""
        logger.info(f"Generating fallback response for destination: {destination}")
        
        # Create a preference-tailored introduction
        pref_intro = ""
        if preferences:
            pref_intro = f"focusing on {', '.join(preferences)}"
        
        response = f"""<h3>5-Day Trip to {destination}</h3>

<p>I've created a {days}-day itinerary for your trip to {destination} {pref_intro}.</p>

<table style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #f2f7ff; font-weight: bold;">
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Day</th>
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Time</th>
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Activity</th>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee; vertical-align: top;" rowspan="3">Day 1</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Morning</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Arrive and check into your accommodation</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Afternoon</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Take a walking tour of the central area to get familiar with the surroundings</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Evening</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Have dinner at a local restaurant to sample the cuisine</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee; vertical-align: top;" rowspan="3">Day 2</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Morning</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Visit the main attractions and landmarks</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Afternoon</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Enjoy lunch at a popular local eatery</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Evening</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Explore cultural sites or museums in the afternoon</td>
    </tr>
"""
        
        # Add middle days based on trip length
        if days > 3:
            response += f"""    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee; vertical-align: top;" rowspan="3">Day 3</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Morning</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Take part in a local cultural activity or workshop</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Afternoon</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Visit markets or shopping districts</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Evening</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Try local specialties for lunch and dinner</td>
    </tr>
"""
        
        if days > 4:
            response += f"""    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee; vertical-align: top;" rowspan="3">Day 4</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Morning</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Take a day trip to natural attractions near {destination}</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Afternoon</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Enjoy outdoor activities suitable for the location</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Evening</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Return to the city for dinner in the evening</td>
    </tr>
"""
        
        # Final day
        response += f"""    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee; vertical-align: top;" rowspan="3">Day {days}</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Morning</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Last-minute souvenir shopping</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Afternoon</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Visit any missed attractions</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Evening</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">Departure from {destination}</td>
    </tr>
</table>

<h3>Budget Estimate</h3>

<table style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background-color: #f2f7ff; font-weight: bold;">
        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #ddd;">Category</th>
        <th style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">Estimated Cost</th>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">🏨 Accommodation</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${75 * days} - ${150 * days}</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">🍽️ Food</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${30 * days} - ${60 * days}</td>
    </tr>
    <tr>
        <td style="padding: 10px; border-bottom: 1px solid #eee;">🚌 Transportation</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${20 * days} - ${40 * days}</td>
    </tr>
    <tr style="background-color: #f9f9f9;">
        <td style="padding: 10px; border-bottom: 1px solid #eee;">🎭 Activities</td>
        <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${25 * days} - ${50 * days}</td>
    </tr>
    <tr style="font-weight: bold; background-color: #e6f0ff;">
        <td style="padding: 10px;">💰 Total estimate</td>
        <td style="padding: 10px; text-align: right;">${(150 * days)} - ${(300 * days)}</td>
    </tr>
</table>

<p>I hope this helps with your trip planning! Feel free to ask for more specific recommendations about accommodations, restaurants, or activities in {destination}.</p>
"""
        
        logger.debug("Generated detailed fallback response")
        return response

# Initialize the planner
ai_planner = OpenAITravelPlanner() 