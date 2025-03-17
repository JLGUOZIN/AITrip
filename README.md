# AITrip - AI-Powered Travel Planner

AITrip is a web application that helps users plan their trips using AI technology. The app integrates with OpenAI's GPT-4o-mini to generate personalized travel itineraries based on user preferences.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API
To use the OpenAI integration for enhanced itineraries:

1. Sign up for an OpenAI account at https://platform.openai.com/
2. Obtain your API key from the OpenAI dashboard
3. Update the `.env` file with your credentials:
   ```
   OPENAI_API_URL=https://api.openai.com/v1
   OPENAI_API_KEY=your_actual_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

**Note:** If you don't have an OpenAI API key or encounter authentication issues, the application will automatically fall back to using the built-in itinerary generator.

### 3. Run the Application
```bash
python app.py
```

The application will be available at http://127.0.0.1:5000

## Features

- AI-powered travel itinerary generation
- User authentication system
- Save and manage travel plans
- Personalized recommendations based on preferences
- Context-aware follow-up questions
- Fallback to local generation when API is unavailable

## Technical Details

The application is built with:
- Flask web framework
- OpenAI GPT-4o-mini for natural language processing (when available)
- Local itinerary generator as fallback
- SQLite for user data storage
- Modern HTML/CSS/JavaScript frontend

## Troubleshooting OpenAI API Integration

### Authentication Error
If you see an authentication error, try these solutions:

1. **Check API Key**: Verify that you've replaced the placeholder in `.env` with your actual OpenAI API key
2. **API Format**: Make sure your API key follows the correct format (begins with "sk-")
3. **API URL**: Confirm the API URL is correct (should be https://api.openai.com/v1)
4. **Account Status**: Ensure your OpenAI account is active and has available credits

### Using the Fallback Generator
The application includes a local fallback generator that will automatically be used when:
- No OpenAI API key is provided
- The OpenAI API returns an error
- There are connectivity issues

The fallback generator provides basic itineraries without requiring external API access.

## OpenAI Model Information

You can configure which OpenAI model to use by changing the `OPENAI_MODEL` value in your .env file:

- The default is set to "gpt-4o-mini"
- You can also use "gpt-3.5-turbo" for a faster but less detailed response
- For premium accounts, "gpt-4" or "gpt-4o" will provide the most detailed itineraries

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions for improvements. 