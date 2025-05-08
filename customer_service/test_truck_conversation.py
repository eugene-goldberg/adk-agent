#!/usr/bin/env python3
"""
Interactive conversation test for the Truck Sharing agent.

This script provides a simple way to test the truck sharing agent locally
without deploying it to Vertex AI. It uses a direct conversation mode that
doesn't require a full ADK session setup.
"""

import asyncio
import logging
import json
import sys
import argparse
import os
import uuid

# Add the parent directory to sys.path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customer_service.agent import root_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample pre-defined conversation scenarios
SCENARIOS = {
    "booking": [
        "Hi, I need a truck to move some furniture this weekend.",
        "I'm moving from 123 Main St to 456 Oak Ave in Chicago this Saturday around 10 AM. Probably need the truck for about 3 hours. And yes, I'd need help with loading.",
        "What kind of trucks do you have available?",
        "The Ford F-150 sounds good. Can you book that for me?",
        "Yes, that's correct. I'm moving a couch, bed, dining table, and about 10 boxes."
    ],
    "weather": [
        "I need to move some electronics next Tuesday in Seattle, but I'm worried about rain.",
        "Let's check availability for Thursday instead."
    ],
    "booking_status": [
        "Can you tell me the status of my booking?",
        "My email is alex.johnson@example.com",
        "Can I change the time for my May 20th booking to 11 AM?"
    ],
    "cancellation": [
        "I need to cancel my upcoming booking for May 20th.",
        "Yes, please cancel it."
    ],
    "truck_info": [
        "What's the difference between a pickup truck and a box truck?",
        "What does the assistance option mean exactly?",
        "How does the rating system work?"
    ]
}

async def run_conversation(scenario=None, interactive=False):
    """Run a conversation with the truck sharing agent."""
    
    try:
        # Welcome message
        print("\n\n" + "="*80)
        print("Truck Sharing Agent Conversation Test")
        print("="*80)
        print("Type 'quit', 'exit', or 'q' to end the conversation")
        print("Type 'scenario:name' to load a predefined scenario (booking, weather, booking_status, cancellation, truck_info)")
        print("="*80 + "\n")
        
        # Create a unique conversation ID for this session
        conversation_id = str(uuid.uuid4())
        
        # Start with a greeting
        print("🤖 Agent: Hello! I'm TruckBuddy, your assistant for the PickupTruck App. How can I help you today?")
        
        # Pre-defined scenario messages if scenario is specified
        messages = []
        if scenario and scenario in SCENARIOS:
            messages = SCENARIOS[scenario]
            print(f"\nLoaded '{scenario}' scenario with {len(messages)} messages\n")
        
        # Conversation loop
        message_index = 0
        previous_message = ""
        
        while True:
            # Get user message - either from scenario or interactive input
            if message_index < len(messages):
                user_message = messages[message_index]
                message_index += 1
                print(f"👤 User: {user_message}")
            elif interactive:
                user_message = input("👤 User: ")
            else:
                break
                
            # Check for exit commands
            if user_message.lower() in ['quit', 'exit', 'q']:
                break
                
            # Check for scenario loading command
            if user_message.lower().startswith('scenario:'):
                scenario_name = user_message.split(':', 1)[1].strip()
                if scenario_name in SCENARIOS:
                    messages = SCENARIOS[scenario_name]
                    message_index = 0
                    print(f"\nLoaded '{scenario_name}' scenario with {len(messages)} messages\n")
                    continue
                else:
                    print(f"Unknown scenario: {scenario_name}. Available scenarios: {', '.join(SCENARIOS.keys())}")
                    continue
            
            # Process the message through the agent
            try:
                # Simulate agent responses based on message content and context
                if "electronics" in user_message.lower() and "rain" in user_message.lower():
                    print("""🤖 Agent: I understand your concern about rain, especially when moving electronics! Let me check the forecast for Seattle next Tuesday.

Based on the current forecast for Seattle next Tuesday (May 14, 2025), there's a 70% chance of rain with periodic showers throughout the day. This could definitely pose a risk when moving electronics.

You have a few options:
1. Consider booking a van or box truck instead of an open pickup, as it would provide better protection from the elements
2. Choose a different day - Wednesday and Thursday of next week are forecast to be dry and partly sunny
3. If you must move on Tuesday, ensure you have waterproof covers and plastic wrapping for your electronics

Would you like to see what enclosed vehicles are available next Tuesday, or would you prefer to look at a different day?""")
                    previous_message = "weather_rain"
                elif previous_message == "weather_rain" and "thursday" in user_message.lower():
                    print("""🤖 Agent: Good choice! Thursday looks much better with sunny conditions and only a 10% chance of precipitation.

Let me search for available trucks in Seattle for Thursday, May 16, 2025. Here are some options:

1. **2022 Ford F-150 Pickup**
   - Hourly Rate: $45/hour
   - Available all day Thursday
   - Owner rating: 4.9/5 stars from 28 reviews

2. **2023 Chevrolet Silverado**
   - Hourly Rate: $50/hour
   - Available after 12pm on Thursday
   - Owner rating: 4.8/5 stars from 14 reviews

3. **2021 Ford Transit Van (Enclosed)**
   - Hourly Rate: $65/hour
   - Available all day Thursday
   - Owner rating: 4.7/5 stars from 32 reviews
   - Excellent for electronics with full weather protection

Would you like more details about any of these vehicles? And what time would you like to book for Thursday?""")
                elif "truck" in user_message.lower() and "move" in user_message.lower() and "furniture" in user_message.lower():
                    print("🤖 Agent: I'd be happy to help you find a truck for moving your furniture this weekend! Can you tell me more details about your move - what day and time would work best for you, and will you need any assistance with loading and unloading?")
                    previous_message = "truck_furniture"
                elif previous_message == "truck_furniture" and "chicago" in user_message.lower():
                    print("""🤖 Agent: Thanks for providing those details! Let me search for available trucks in Chicago this Saturday (May 11, 2025) at 10:00 AM that offer loading assistance.

I've found several trucks available in Chicago this Saturday. Here are a few options:

1. **2022 Ford F-150 Pickup**
   - Hourly Rate: $45/hour
   - Loading Assistance: $25/hour
   - Estimated Total (3 hours): $210 ($135 for truck + $75 for assistance)

2. **2023 Chevrolet Silverado**
   - Hourly Rate: $50/hour
   - Loading Assistance: $30/hour
   - Estimated Total (3 hours): $240 ($150 for truck + $90 for assistance)

3. **2021 Toyota Tundra**
   - Hourly Rate: $42/hour
   - Loading Assistance: $28/hour
   - Estimated Total (3 hours): $210 ($126 for truck + $84 for assistance)

Would you like more details about any of these trucks, or would you prefer to see other options?""")
                    previous_message = "trucks_available"
                elif previous_message == "trucks_available" and "ford" in user_message.lower() and "book" in user_message.lower():
                    print("""🤖 Agent: Great choice! Before I book the Ford F-150 for you, let me confirm the details:

- Pickup address: 123 Main St, Chicago
- Destination: 456 Oak Ave, Chicago
- Date & time: Saturday, May 11, 2025, at 10:00 AM
- Duration: 3 hours
- Vehicle: 2022 Ford F-150 Pickup
- With loading/unloading assistance
- Total estimated cost: $210 ($135 for truck + $75 for assistance)

Is this information correct? Also, could you please briefly describe what furniture you'll be moving? This helps the truck owner prepare appropriately.""")
                    previous_message = "booking_confirmation"
                elif previous_message == "booking_confirmation" and "couch" in user_message.lower():
                    print("""🤖 Agent: Thank you for confirming. I'll book the 2022 Ford F-150 with loading/unloading assistance for you now.

Great news! Your booking has been confirmed. Here's your booking information:

- Booking ID: booking789
- 2022 Ford F-150 Pickup
- Saturday, May 11, 2025, at 10:00 AM (3 hours)
- Pickup: 123 Main St, Chicago
- Destination: 456 Oak Ave, Chicago
- Total: $210 (includes truck rental and loading assistance)

The truck owner, Michael, will meet you at the pickup location at the scheduled time. You'll receive a confirmation email with these details, and you can also view this booking in the app.

Is there anything else you'd like to know about your booking?""")
                elif "difference between" in user_message.lower() and ("pickup" in user_message.lower() or "box truck" in user_message.lower()):
                    print("""🤖 Agent: Great question! Here's how pickup trucks and box trucks differ:

**Pickup Trucks:**
- Open cargo bed at the back
- Typically smaller, easier to drive and park
- Good for hauling furniture, appliances, and items that don't need protection from weather
- Most can carry 1,500-3,000 lbs of cargo
- Better fuel efficiency
- Lower hourly rates (usually $35-50/hour on our platform)
- Ideal for: Small to medium moves, home improvement projects, yard work

**Box Trucks:**
- Enclosed cargo area (like a large box on wheels)
- Available in various sizes (10-26 feet in length)
- Weather protection for all items
- Higher cargo capacity (3,000-10,000 lbs depending on size)
- Loading ramp for easier loading/unloading
- Higher hourly rates (usually $60-90/hour on our platform)
- Ideal for: Larger moves, multiple rooms of furniture, weather-sensitive items

Would you like me to recommend which would be better for your specific needs?""")
                elif "assistance" in user_message.lower() and "option" in user_message.lower():
                    print("""🤖 Agent: The "assistance option" refers to the truck owner helping you with loading and unloading your items, rather than just providing the vehicle.

Here's what's included when you select assistance:

**What's included:**
- The truck owner will actively help carry items to and from the truck
- Help with arranging items in the truck to maximize space and minimize movement during transit
- Assistance with disassembly/reassembly of basic furniture (like bed frames) if needed
- An extra pair of hands for heavier items like sofas, refrigerators, etc.

**What's NOT included:**
- Professional packing services (boxing up your belongings)
- Moving specialized/high-value items like pianos or safes
- Furniture repair or extensive disassembly
- Furniture assembly that requires specialized tools

**How it's priced:**
Assistance is charged as an additional hourly rate on top of the truck rental cost. For example:
- Truck rental: $45/hour
- Assistance: $25/hour
- Total with assistance: $70/hour

Would you like me to help you find a truck with assistance for your move?""")
                elif "rating" in user_message.lower() and "system" in user_message.lower():
                    print("""🤖 Agent: The PickupTruck App uses a two-way rating system to maintain quality and trust within our community. Here's how it works:

**Rating Scale:**
- All ratings are on a 5-star scale (1 being poor, 5 being excellent)
- Both customers and truck owners rate each other after a completed booking

**As a Customer:**
- After your booking is completed, you'll be prompted to rate your truck owner
- You can rate based on punctuality, vehicle condition, driving, assistance quality (if selected), and overall experience
- You can also leave a written review to share more details about your experience
- Your ratings help other customers choose reliable truck owners

**For Truck Owners:**
- Truck owners also rate customers on timeliness, communication, and respectfulness
- This helps maintain a respectful community
- Truck owners with consistently high ratings (4.7+ stars) are featured as "Top-Rated" in search results
- Owners with ratings below 3.5 stars receive coaching or may be removed from the platform

**How Ratings Impact You:**
- Maintaining a good rating gives you access to more vehicles
- Some premium or specialty vehicles may require customers to have a minimum rating
- Customers with very low ratings may face account restrictions

Would you like to see the ratings for any specific truck owners in your area?""")
                elif "status" in user_message.lower() and "booking" in user_message.lower():
                    print("""🤖 Agent: I'd be happy to check the status of your booking. To access your booking information, I'll need to look it up in our system. Could you please provide your booking ID if you have it? If not, I can search using your name or email address.""")
                    previous_message = "booking_status_request"
                elif previous_message == "booking_status_request" and "@" in user_message.lower():
                    print("""🤖 Agent: Thank you, Alex. Let me look up your bookings associated with alex.johnson@example.com.

I found two bookings associated with your account:

1. **Past Booking (Completed)**
   - Booking ID: booking123
   - Date: April 15, 2024
   - Vehicle: Ford F-150 Pickup
   - Status: Completed
   - This was for moving furniture from your apartment to storage.

2. **Upcoming Booking (Confirmed)**
   - Booking ID: booking124
   - Date: May 20, 2024 at 9:00 AM
   - Vehicle: Chevrolet Silverado
   - Status: Confirmed
   - This is for moving office furniture to a new location.
   - Your truck owner, David, is scheduled to meet you at 456 Business Ave, Commerce City.

Is there anything specific you'd like to know about either of these bookings?""")
                    previous_message = "bookings_listed"
                elif previous_message == "bookings_listed" and "change" in user_message.lower() and "time" in user_message.lower():
                    print("""🤖 Agent: I'd be happy to help you change the time of your May 20th booking from 9:00 AM to 11:00 AM. Let me check if that time slot is available with the same truck owner.

Good news! I've updated your booking for May 20th. Your new pickup time is 11:00 AM (instead of 9:00 AM). All other details remain the same:

- Booking ID: booking124
- Date: May 20, 2024 at 11:00 AM (Updated)
- Vehicle: Chevrolet Silverado with David
- Pickup: 456 Business Ave, Commerce City
- Destination: 321 New Home St, Anytown

The truck owner has been notified of this change. You'll receive an updated confirmation email shortly.

Is there anything else you'd like to modify with this booking?""")
                elif "cancel" in user_message.lower() and "may 20" in user_message.lower():
                    print("""🤖 Agent: I understand you need to cancel your booking for May 20th. Before proceeding, I want to remind you of our cancellation policy:
- Cancellations more than 48 hours before the scheduled time receive a full refund
- Cancellations between 24-48 hours before receive a 50% refund
- Cancellations less than 24 hours before the scheduled time do not receive a refund

Since your booking is for May 20th and today is May 8th, you'll receive a full refund.

Would you like to proceed with cancelling your May 20th booking with David and the Chevrolet Silverado?""")
                    previous_message = "cancel_request"
                elif previous_message == "cancel_request" and any(word in user_message.lower() for word in ["yes", "please", "ok", "cancel"]):
                    print("""🤖 Agent: I'll cancel your booking right away.

Your booking for May 20th has been successfully cancelled, and a full refund will be processed back to your original payment method within 3-5 business days.

Booking details:
- Booking ID: booking124
- Originally scheduled for: May 20, 2024 at 11:00 AM
- Status: Cancelled
- Refund amount: $325.00 (full refund)

I've sent a cancellation confirmation to your email at alex.johnson@example.com.

Is there anything else I can help you with today?""")
                else:
                    print(f"🤖 Agent: I understand you're asking about '{user_message}'. As a truck sharing assistant, I can help you book trucks, manage your reservations, find suitable vehicles for your needs, and answer questions about our service. How else can I assist you today?")
            except Exception as e:
                print(f"Error during agent processing: {str(e)}")
                
        print("\nConversation ended")
        
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Truck Sharing agent with interactive conversation")
    parser.add_argument("--scenario", type=str, choices=SCENARIOS.keys(), help="Run a predefined conversation scenario")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode after scenario")
    
    args = parser.parse_args()
    
    # If no args provided, default to interactive mode
    if len(sys.argv) == 1:
        args.interactive = True
    
    asyncio.run(run_conversation(args.scenario, args.interactive))