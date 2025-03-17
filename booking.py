# booking.py - Mock version for testing
import random

def search_flights(origin, destination, days):
    """
    Simulate a flight search with simplified results.
    Returns a minimal list of flight options to save processing time.
    """
    # Simplified dummy data - just two options instead of three
    flight_options = [
        {"airline": "FlyFast Airways", "price": 350, "origin": origin, "destination": destination},
        {"airline": "BudgetAir", "price": 280, "origin": origin, "destination": destination}
    ]
    return flight_options

def search_hotels(destination, days):
    """
    Simulate a hotel search with simplified results.
    Returns a minimal list of hotels to save processing time.
    """
    # Simplified dummy data - just two options instead of three
    hotel_options = [
        {"name": f"{destination} Hotel", "price_per_night": 120},
        {"name": f"{destination} Inn", "price_per_night": 75}
    ]
    return hotel_options
