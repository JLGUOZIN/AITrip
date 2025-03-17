# itinerary_generator.py - Mock version for testing
import random

def generate_itinerary(destination, days, preferences):
    """
    Mock function to generate a travel itinerary.
    :param destination: str, trip destination
    :param days: int, number of days for the trip
    :param preferences: list of str, e.g. ["Adventure", "Food"]
    :return: str itinerary text
    """
    # Create a simple mock itinerary
    pref_text = ", ".join(preferences) if preferences else "general sightseeing"
    
    itinerary = f"""
{days}-Day Trip to {destination}

Your personalized itinerary focusing on {pref_text}.

Day 1
- Arrive at {destination}
- Check into your hotel
- Explore the local area
- Dinner at a popular restaurant

"""
    
    # Add middle days
    for day in range(2, days):
        activities = [
            f"Visit {destination}'s famous landmarks",
            "Try local cuisine at a recommended restaurant",
            "Shopping at local markets",
            "Museum or cultural site visit",
            "Relax at a park or scenic area"
        ]
        # Shuffle and pick 2-3 activities
        random.shuffle(activities)
        day_activities = activities[:random.randint(2, 3)]
        
        itinerary += f"""
Day {day}
"""
        for activity in day_activities:
            itinerary += f"- {activity}\n"
    
    # Add last day
    itinerary += f"""
Day {days}
- Final sightseeing
- Souvenir shopping
- Departure

Enjoy your trip to {destination}!
"""
    
    return itinerary
