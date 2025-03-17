# budget.py
def estimate_budget(flights, hotels, days):
    """
    Estimate total trip cost based on flight, hotel, and daily expenses.
    - flights: list of flight option dicts (expects at least one)
    - hotels: list of hotel option dicts (expects at least one)
    - days: int, number of days of the trip
    """
    if not flights or not hotels or days is None:
        return 0
    
    # Choose the cheapest flight option and hotel option
    cheapest_flight = min(f["price"] for f in flights)
    cheapest_hotel_nightly = min(h["price_per_night"] for h in hotels)
    
    # Calculate hotel cost for the entire trip
    hotel_cost = cheapest_hotel_nightly * days
    
    # Simplified daily expenses (food, transport, activities)
    daily_expense = 80  # reduced from 100 to be more conservative
    other_costs = daily_expense * days
    
    # Calculate total and round to nearest 10 for simplicity
    total_estimate = cheapest_flight + hotel_cost + other_costs
    rounded_estimate = round(total_estimate / 10) * 10
    
    return rounded_estimate
